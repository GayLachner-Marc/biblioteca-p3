# Mockups – Biblioteca

Wireframes estáticos (HTML + `wireframe.css`, sin CDN) a 1280px. Los PNG están en `png/`.
Regenerar PNG: `./export_png.sh` (requiere `google-chrome`).

| Pantalla | Ruta |
|---|---|
| `01-dashboard` | `/` |
| `02-libros-listado` | `/libros` |
| `03-libro-formulario` | `/libros/nuevo`, `/libros/{id}/editar` |
| `04-prestamos-listado` | `/prestamos` |
| `05-prestamo-formulario` | `/prestamos/nuevo` |
| `06-usuarios-listado` | `/usuarios` |
| `07-usuario-formulario` | `/usuarios/nuevo` |
| `08-autores-listado` | `/autores` |

`index.html` enlaza a todas las pantallas.
Regenerar HTML: `python3 generar_mockups.py` (luego `./export_png.sh`).
