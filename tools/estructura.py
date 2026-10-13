"""Arma data/productos.json del catálogo Hair a partir del export de PBG-BI (hair-data/productos.json).

Estructura (orden de las webs oficiales de Wella Professionals, Nioxin y Sebastian Professional):
  marcas -> categorías -> líneas; en las líneas de color, carta de tonos por familia.
Cada producto: [sku, nombre, línea, tono, familia, tipo, presentación]
"""
import json, re, sys

SRC = '/home/claude/hair-data/productos.json'

MARCAS = ['Wella Professionals', 'Nioxin', 'Sebastian Professional']
CATS = [  # (marca, nombre)
    (0, 'Color'), (0, 'Cuidado'), (0, 'Styling'), (0, 'Accesorios'),
    (1, 'Sistemas'), (1, 'Tratamientos'), (1, 'Accesorios'),
    (2, 'Cuidado'), (2, 'Styling'),
]
# (categoría, nombre, es carta de tonos)
LINES = [
    (0, 'Koleston Perfect ME+', 1), (0, 'Illumina Color', 1), (0, 'Shinefinity', 1), (0, 'Color Touch', 1),
    (0, 'Color Perfect', 1), (0, 'Blondor', 0), (0, 'Oxidantes y emulsiones', 0), (0, 'Wellaplex', 0),
    (1, 'Ultimate Repair', 0), (1, 'Ultimate Smooth', 0), (1, 'Fusion', 0), (1, 'Oil Reflections', 0),
    (1, 'Color Motion+', 0), (1, 'Nutricurls', 0), (1, 'Invigo', 0),
    (2, 'EIMI', 0),
    (3, 'Accesorios', 0),
    (4, 'Sistema 1', 0), (4, 'Sistema 2', 0), (4, 'Sistema 3', 0), (4, 'Sistema 4', 0),
    (5, 'Tratamientos', 0),
    (6, 'Accesorios', 0),
    (7, 'Dark Oil', 0), (7, 'Penetraitt', 0), (7, 'Hydre', 0), (7, 'Trilliance', 0),
    (8, 'Dark Oil', 0), (8, 'Potion 9', 0), (8, 'Taming Elixir', 0), (8, 'Trilliant', 0),
]
FAMS = ['Pure Naturals', 'Rich Naturals', 'Deep Browns', 'Vibrant Reds', 'Special Blonde', 'Special Mix']
FAMSUB = {'PURE NATURALS': 0, 'RICH NATURALS': 1, 'DEEP BROWNS': 2, 'VIBRANT REDS': 3, 'SPECIAL BLONDE': 4, 'SPECIAL MIX': 5}
TIPOS = ['Shampoo', 'Acondicionador', 'Máscara', 'Tratamiento', 'Aceite y sérum', 'Styling', 'Kit', 'Oxidante', 'Decolorante', 'Accesorio']

ALTURA = {'1': 'Negro azulado', '2': 'Negro', '3': 'Castaño oscuro', '4': 'Castaño medio', '5': 'Castaño claro', '6': 'Rubio oscuro',
          '7': 'Rubio medio', '8': 'Rubio claro', '9': 'Rubio muy claro', '10': 'Rubio clarísimo', '12': 'Rubio especial'}
REFLEJO = {'0': 'natural', '1': 'ceniza', '2': 'mate', '3': 'dorado', '4': 'cobrizo', '5': 'caoba', '6': 'violeta',
           '7': 'marrón', '8': 'perla', '9': 'cendré'}


def li(cat, nombre):
    for i, (c, n, _) in enumerate(LINES):
        if c == cat and n == nombre:
            return i
    raise KeyError((cat, nombre))


def nombre_tono(a, b):
    """7/18 -> Rubio medio ceniza perla; 66/46 -> Rubio oscuro intenso cobrizo violeta; 0/88 -> Mezclador perla intenso."""
    if a == '0':
        if not b:
            return 'Mezclador'
        if b == '00':
            return 'Mezclador transparente'
        rs = [REFLEJO.get(c, c) for c in b]
        if len(set(b)) == 1 and len(b) == 2:
            return 'Mezclador ' + rs[0] + ' intenso'
        return 'Mezclador ' + ' '.join(rs)
    intenso = len(a) == 2 and a[0] == a[1]
    base = ALTURA.get(a[0] if intenso else a, a)
    if intenso:
        base += ' intenso'
    if not b:
        return base
    b2 = b.lstrip('0') if b.startswith('0') and len(b) == 2 else b
    if b in ('00',):
        return base + ' natural intenso'
    if b.startswith('0') and len(b) == 2:  # /07 natural marrón
        return base + ' natural ' + REFLEJO.get(b[1], '')
    rs = [REFLEJO.get(c, c) for c in b]
    if len(b) == 2 and b[0] == b[1]:
        return base + ' ' + rs[0] + ' intenso'
    return (base + ' ' + ' '.join(rs)).strip()


def tono_de(n):
    m = re.search(r'(\d{1,2})\s*/\s*(\d{1,2})\b', n)
    return (m.group(1).lstrip('0') or '0', m.group(2)) if m else None


def pres(n):
    s = n.upper().replace('6OML', '60ML')
    m = re.search(r'(\d+(?:[.,]\d+)?)\s*(ML|GRS|G|LT|L)\b', s)
    if m:
        v, u = m.group(1).replace(',', '.'), m.group(2)
        if u in ('L', 'LT'):
            return str(int(float(v) * 1000)) + ' ml'
        if u in ('G', 'GRS'):
            return v + ' g'
        return v + ' ml'
    m = re.search(r'\b(1000|500)\s*$', s)
    return (m.group(1) + ' ml') if m else ''


def tipo_de(n, t):
    s = (n + ' ' + (t or '')).upper()
    if 'KIT' in s:
        return 6
    if re.search(r'WELLOXON|EMULSI|OXIDANTE', s):
        return 7
    if re.search(r'BLONDOR|DECOLOR', s):
        return 8
    if re.search(r'SHAMPOO|\bSHP?\b|SH\.|\bSH\b', s):
        return 0
    if re.search(r'ACOND|\bCOND\b|CONDITIONER|\bCND\b|COND\.', s):
        return 1
    if re.search(r'M[AÁ]SC|MASK|MASQUE', s):
        return 2
    if re.search(r'\bOIL\b|ACEITE|ELIXIR|SERUM|SÉRUM|MIRACLE', s) and 'MASK' not in s:
        return 4
    if re.search(r'EIMI|POTION|TRILLIANT|STYLING|CURLIXIR|PROT', s):
        return 5
    if re.search(r'TREAT|TRAT|BOOSTER|RENEW|LEAVE|POST COLOR|BOND|PLEX', s):
        return 3
    return 9


def limpio(x):
    """Nombre de catálogo para productos que no son tonos."""
    n = x['nombre']
    s = n.upper()
    L = x['linea']
    tp = TIPOS[tipo_de(n, x['tipo'])]
    tp_txt = {'Aceite y sérum': 'Aceite'}.get(tp, tp)
    if x['marca'].startswith('NIOXIN'):
        m = re.search(r'\bS(\d)\b', s)
        k = m.group(1) if m else ''
        if 'KIT' in s: return 'Kit Sistema ' + k
        if 'TREATMENT' in s: return 'Sistema ' + k + ' Tratamiento sin enjuague'
        if 'BOOSTER' in s: return 'Hair Booster'
        if 'SCALP RENEW' in s: return 'Scalp Renew Dermabrasión'
        if 'DEEP REPAIR' in s: return 'Deep Repair Hair Masque'
        if 'ALTA FRECUENCIA' in s: return 'Equipo de alta frecuencia'
        return 'Sistema ' + k + ' ' + ('Shampoo' if 'SHAMPOO' in s else 'Acondicionador')
    if x['marca'] == 'SEBASTIAN':
        for key, nm in [('DARK OIL', 'Dark Oil'), ('PENETRA', 'Penetraitt'), ('HYDRE', 'Hydre'), ('TRILLIANCE', 'Trilliance'),
                        ('TRILLIANT', 'Trilliant'), ('POTION 9 LITE', 'Potion 9 Lite'), ('POTION 9', 'Potion 9'), ('TAMING', 'Taming Elixir')]:
            if key in s:
                if nm in ('Trilliant', 'Potion 9 Lite', 'Potion 9', 'Taming Elixir'):
                    return nm
                if nm == 'Dark Oil' and tp == 'Aceite y sérum':
                    return 'Dark Oil'
                return nm + ' ' + tp_txt
    if L == 'EIMI':
        for key, nm in [('MISTIFY', 'Mistify Me Light'), ('NATURAL VOLUME', 'Natural Volume'), ('SHAPE CONTROL', 'Shape Control'),
                        ('SUGAR', 'Sugar Lift'), ('SUPER SET', 'Super Set'), ('THERMAL', 'Thermal Image')]:
            if key in s: return 'EIMI ' + nm
    if L == 'WELLOXON':
        m = re.search(r'(\d{1,2})\s*VOL|(\d{2})V\b', s)
        vol = (m.group(1) or m.group(2)) if m else ''
        pct = {'6': '1,9 %', '10': '3 %', '20': '6 %', '30': '9 %', '40': '12 %'}.get(vol, '')
        return 'Welloxon Perfect ' + pct + ' · ' + vol + ' vol'
    if L == 'EMULSION CT':
        return 'Color Touch Emulsión ' + ('1,9 %' if '1,9' in s else '4 %')
    if L == 'BLONDOR':
        if 'PLEX' in s: return 'Blondor Plex Multi Blonde polvo decolorante'
        return 'Blondor Multi Blonde polvo decolorante'
    if L == 'WELLAPLEX':
        return 'Wellaplex N.º 1 Bond Maker' if 'STEP1' in s.replace(' ', '') else 'Wellaplex N.º 2 Bond Stabilizer'
    for key, nm in [('INVIGO BRILLIANCE', 'Invigo Color Brilliance'), ('COOL BLOND', 'Invigo Blonde Recharge'),
                    ('INVIGO ENRICH', 'Invigo Nutri-Enrich'), ('INVIGO PURE', 'Invigo Balance Aqua Pure'),
                    ('FUSION', 'Fusion'), ('OIL REF', 'Oil Reflections'), ('COLOR MOTION', 'Color Motion+'), ('COLORMOTION', 'Color Motion+'),
                    ('NUTRICURL', 'Nutricurls'), ('ULT. REPAIR', 'Ultimate Repair'), ('ULT SMOOTH', 'Ultimate Smooth')]:
        if key in s:
            if 'MIRACLE' in s: return nm + ' Miracle Hair Rescue'
            if 'LEAVE IN' in s: return nm + ' Protective Leave-In'
            if 'DEEP' in s: return nm + ' Deep Conditioner'
            if 'POST COLOR' in s: return nm + ' Post Color Treatment'
            if 'CURLIXIR' in s: return nm + ' Curlixir Balm'
            if 'PROT' in s and nm == 'Fusion': return 'Fusion Repair Protector'
            if nm == 'Ultimate Smooth' and 'OIL' in s: return 'Ultimate Smooth Miracle Oil Serum'
            if nm == 'Oil Reflections' and tp == 'Accesorio': return 'Oil Reflections Luminous Reveal Oil'
            return nm + ' ' + tp_txt
    # accesorios: nombre del sistema prolijo
    t = re.sub(r'^[*\s]+|^W\.?P\.?\s+|^WLA\s+|^OTHER PRO\s+', '', n).strip()
    t = t.replace('(50 MTS. X 12 CM', '50 m x 12 cm').replace('Roceador', 'rociador')
    return t[:1].upper() + t[1:].lower() if t.isupper() else t


def linea_de(x, nombre):
    L, s = x['linea'], x['nombre'].upper()
    m = x['marca']
    if L == 'KOLESTON PERFECT ME': return li(0, 'Koleston Perfect ME+')
    if L == 'ILLUMINA COLOR': return li(0, 'Illumina Color')
    if L == 'SHINEFINITY': return li(0, 'Shinefinity')
    if L == 'COLOR TOUCH': return li(0, 'Color Touch')
    if L == 'COLOR PERFECT': return li(0, 'Color Perfect')
    if L == 'BLONDOR': return li(0, 'Blondor')
    if L in ('WELLOXON', 'EMULSION CT'): return li(0, 'Oxidantes y emulsiones')
    if L == 'WELLAPLEX': return li(0, 'Wellaplex')
    if L == 'EIMI': return li(2, 'EIMI')
    if L == 'ACCESORIOS WELLA PROFESSIONALS': return li(3, 'Accesorios')
    if m.startswith('NIOXIN'):
        if L == 'NIOXIN ACCESORIOS': return li(6, 'Accesorios')
        k = re.search(r'Sistema (\d)', nombre)
        if k: return li(4, 'Sistema ' + k.group(1))
        return li(5, 'Tratamientos')
    if m == 'SEBASTIAN':
        for nm in ['Dark Oil', 'Penetraitt', 'Hydre', 'Trilliance']:
            if nombre.startswith(nm) and nombre != 'Dark Oil':
                return li(7, nm)
        for nm in ['Dark Oil', 'Potion 9', 'Taming Elixir', 'Trilliant']:
            if nombre.startswith(nm):
                return li(8, nm)
    for key, nm in [('Ultimate Repair', 'Ultimate Repair'), ('Ultimate Smooth', 'Ultimate Smooth'), ('Fusion', 'Fusion'),
                    ('Oil Reflections', 'Oil Reflections'), ('Color Motion+', 'Color Motion+'), ('Nutricurls', 'Nutricurls'), ('Invigo', 'Invigo')]:
        if nombre.startswith(key): return li(1, nm)
    raise ValueError('sin línea: ' + x['sku'] + ' ' + x['nombre'] + ' -> ' + nombre)


EXCLUIR_SKU = {'81622453'}
# Nombres y presentaciones a mano donde el del sistema no sirve (accesorios, kits).
NOMBRES = {
    '81156705': ('Dispensador de folio Wrapmaster', ''),
    '0470000': ('Folio de aluminio plateado', '50 m × 12 cm'),
    '81550909': ('Folio de aluminio, set de 4 colores', ''),
    '99350052751': ('Botella aplicadora con pico', '240 ml'),
    '0408000': ('Vaso medidor', '120 ml'),
    '0471000': ('Rociador Wella Professionals', ''),
    '1237675': ('Bomba dosificadora para shampoo', '1000 ml'),
    '1237676': ('Bomba dosificadora para tratamiento', '500 ml'),
    '99240012341': ('Bomba dosificadora Wellaplex', '500 ml'),
    '3030233': ('Equipo de alta frecuencia', ''),
    '99350180548': ('Kit Sistema 1', '150 + 150 + 50 ml'),
    '99350180567': ('Kit Sistema 2', '150 + 150 + 40 ml'),
    '99350180573': ('Kit Sistema 3', '150 + 150 + 50 ml'),
    '99350180579': ('Kit Sistema 4', '150 + 150 + 40 ml'),
    '1478472': ('Oil Reflections Luminous Reveal Oil', '100 ml'),
    '99240016215': ('Color Motion+ Post Color Treatment', '500 ml'),
}
TIPO_FIJO = {'99240016215': 3, '1478472': 4, '99240044504': 5}  # Climazon S4: precio en dólares en la lista GRAL


def armar(productos=None):
    P = productos if productos is not None else json.load(open(SRC))
    out, fuera = [], []
    for x in P:
        n = x['nombre'] or ''
        s = n.upper()
        if x['sku'] in EXCLUIR_SKU:
            fuera.append((x['sku'], n, 'precio en dólares')); continue
        if not x['pg']:
            fuera.append((x['sku'], n, 'sin precio')); continue
        if x['sublinea'] == 'CARTADECOLOR' or re.search(r'CARTA|CHART|BINDER|PANTONNIER|INSERT', s):
            fuera.append((x['sku'], n, 'carta/material')); continue
        lin = x['linea']
        es_tono = lin in ('KOLESTON PERFECT ME', 'COLOR PERFECT', 'COLOR TOUCH', 'ILLUMINA COLOR', 'SHINEFINITY')
        if es_tono:
            t = tono_de(n)
            if not t:
                fuera.append((x['sku'], n, 'tono ilegible')); continue
            a, b = t
            if lin == 'ILLUMINA COLOR' and re.search(r'\d/\s+60|/60 ML|9/60', s.replace('  ', ' ')):
                fuera.append((x['sku'], n, 'tono ilegible')); continue
            tono = a + '/' + b
            if lin == 'SHINEFINITY':
                tono = a.zfill(2) + '/' + b.zfill(2)
            nombre = nombre_tono(a, b)
            fam = FAMSUB.get(x['sublinea'] or '', -1)
            if a == '0' and fam < 0: fam = 5
            if a == '12' and fam < 0: fam = 4
            row = [x['sku'], nombre, None, tono, fam, -1, pres(n) or '60 ml']
        else:
            nombre = limpio(x)
            tp = TIPO_FIJO.get(x['sku'], tipo_de(n, x['tipo']))
            pr = pres(n) or (x['tamano'] + (' g' if tp == 8 else ' ml') if x['tamano'] and tp != 6 else '')
            if x['sku'] in NOMBRES:
                nombre, pr = NOMBRES[x['sku']][0], NOMBRES[x['sku']][1] or pr
            if x['linea'] in ('ACCESORIOS WELLA PROFESSIONALS', 'NIOXIN ACCESORIOS'):
                tp = 9
            row = [x['sku'], nombre, None, '', -1, tp, pr]
        row[2] = linea_de(x, nombre)
        out.append(row)
    # orden: línea, familia, altura, reflejo; en cuidado: tipo y tamaño
    def clave(r):
        if LINES[r[2]][2]:
            a, b = r[3].split('/')
            return (r[2], r[4] if r[4] >= 0 else 9, int(a), b)
        tam = re.match(r'(\d+)', r[6] or '')
        return (r[2], r[5], r[1], int(tam.group(1)) if tam else 0)
    out.sort(key=clave)
    data = {'marcas': MARCAS, 'cats': [list(c) for c in CATS], 'lines': [list(l) for l in LINES], 'fams': FAMS, 'tipos': TIPOS, 'p': out}
    return data, fuera


if __name__ == '__main__':
    data, fuera = armar()
    dst = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/hair-data/catalogo_productos.json'
    json.dump(data, open(dst, 'w'), ensure_ascii=False, separators=(',', ':'))
    print(len(data['p']), 'productos;', len(fuera), 'fuera')
    for f in fuera: print('  fuera:', f)
