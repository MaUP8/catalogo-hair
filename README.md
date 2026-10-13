# Catálogo Hair · Wella Professionals, Nioxin y Sebastian Professional

Catálogo para profesionales con pedido por WhatsApp. Se publica en **hair.catalogospbg.com** y se administra desde el portal (admin.catalogospbg.com, pestaña *Hair*).

- `index.html`: la página. Navegación como las webs oficiales: marca → categoría → línea; en Color, carta de tonos por familia y altura.
- `data/productos.json`: estructura del catálogo (marcas, categorías, líneas, familias, tipos) y productos `[sku, nombre, línea, tono, familia, tipo, presentación]`.
- `data/disponibles.json`: precio profesional con impuestos (lista GRAL), Outlet por vencimiento (`o`: unidades que vencen dentro del plazo y el mes del primer vencimiento) y ranking. Lo recalcula el portal dos veces por día.
- `data/config.json`: vendedores (`id` del link, nombre, celular), pedido mínimo y Outlet (`activo`, `mecanica`: `descuento` por tramos o `1+1`, `tramos`, `meses`). Lo edita el portal.
- `data/ajustes.json`: productos ocultos. Lo edita el portal.
- `img/p/<sku>.jpg`: fotos 600×600 sobre blanco (packshots de Bynder; en tonos, el mechón).
- `tools/`: scripts de la primera carga.

Cada vendedor comparte su link: `https://hair.catalogospbg.com/?v=<id>`. Sin link, la clienta elige a quién enviar el pedido.
