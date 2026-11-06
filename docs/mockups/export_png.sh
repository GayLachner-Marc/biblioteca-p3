#!/usr/bin/env bash
# Regenera los PNG de los mockups con Chrome headless.
D="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$D/png"
for p in 01-dashboard:660 02-libros-listado:540 03-libro-formulario:900 04-prestamos-listado:520 05-prestamo-formulario:560 06-usuarios-listado:540 07-usuario-formulario:620 08-autores-listado:500; do
  n="${p%%:*}"; h="${p##*:}"
  google-chrome --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=1 \
    --window-size=1280,$h --screenshot="$D/png/$n.png" "file://$D/$n.html"
done
