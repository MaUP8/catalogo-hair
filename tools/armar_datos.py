"""Primera carga de data/ del catálogo Hair desde el export de PBG-BI (las siguientes las hace el portal).

Uso: python3 tools/armar_datos.py <productos_pbi.json> <vencimientos_pbi.json>
Escribe data/productos.json, data/disponibles.json y, si no existen, data/config.json y data/ajustes.json.
"""
import json, os, sys, datetime

AQUI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(AQUI)
sys.path.insert(0, AQUI)
from estructura import armar  # noqa: E402

IMESI, IVA = 1.115, 1.22
HORIZONTE_MESES = 6  # Outlet: lotes que vencen dentro de este plazo (lo ajusta el portal)


def r2(x):
    return float(f'{x:.2f}')


def precio_final(x):
    aplica = str(x.get('imesi') or '').strip().upper().startswith('A')
    return r2(r2(x['pg']) * (IMESI if aplica else 1) * IVA)


def meses_hasta(vto, hoy):
    y, m = int(vto[:4]), int(vto[5:7])
    return (y - hoy.year) * 12 + (m - hoy.month)


def outlet(venc, skus, hoy, horizonte):
    """{sku: [unidades que vencen dentro del horizonte, 'AAAA-MM' del primero]}.
    No entran los lotes vencidos ni los que vencen en el mes en curso (no llegan a usarse)."""
    o = {}
    for r in venc:
        s, v, u = str(r['sku']).strip(), r.get('vto'), int(round(float(r.get('u') or 0)))
        if s not in skus or not v or u <= 0:
            continue
        m = meses_hasta(v, hoy)
        if m < 1 or m > horizonte:
            continue
        x = o.setdefault(s, [0, v[:7]])
        x[0] += u
        x[1] = min(x[1], v[:7])
    return o


def main(src, vsrc):
    P = json.load(open(src))
    data, fuera = armar(P)
    # Solo entra lo que tiene foto; el resto queda en «Sin publicar» del portal para subirlo con su foto.
    sin_foto = [r for r in data['p'] if not os.path.exists(os.path.join(REPO, 'img/p', r[0] + '.jpg'))]
    data['p'] = [r for r in data['p'] if r not in sin_foto]
    fuera += [(r[0], r[1], 'sin foto') for r in sin_foto]
    skus = {r[0] for r in data['p']}
    sin_outlet = {r[0] for r in data['p'] if r[5] == 9}  # accesorios: el vencimiento no aplica
    hoy = datetime.date.today()
    d = {x['sku']: precio_final(x) for x in P if x['sku'] in skus}
    top = [x['sku'] for x in sorted(P, key=lambda x: -(x.get('unidV12m') or 0)) if x['sku'] in skus and (x.get('unidV12m') or 0) > 0]
    o = outlet(json.load(open(vsrc)), skus - sin_outlet, hoy, HORIZONTE_MESES)
    os.makedirs(os.path.join(REPO, 'data'), exist_ok=True)
    json.dump(data, open(os.path.join(REPO, 'data/productos.json'), 'w'), ensure_ascii=False, separators=(',', ':'))
    disp = {'fecha': hoy.isoformat(), 'd': {k: d[k] for k in sorted(d)}, 'o': {k: o[k] for k in sorted(o)}, 'top': top}
    json.dump(disp, open(os.path.join(REPO, 'data/disponibles.json'), 'w'), separators=(',', ':'))
    cfg = os.path.join(REPO, 'data/config.json')
    if not os.path.exists(cfg):
        json.dump({'vendedores': [], 'minimo': 0,
                   'outlet': {'activo': False, 'mecanica': 'descuento', 'tramos': [{'meses': 3, 'pct': 40}, {'meses': 6, 'pct': 25}], 'meses': 6}},
                  open(cfg, 'w'), ensure_ascii=False, indent=2)
    aj = os.path.join(REPO, 'data/ajustes.json')
    if not os.path.exists(aj):
        json.dump({'ocultos': []}, open(aj, 'w'), indent=2)
    print(len(d), 'disponibles ·', len(o), 'con lotes por vencer en', HORIZONTE_MESES, 'meses ·', len(top), 'en ranking ·', len(fuera), 'fuera')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
