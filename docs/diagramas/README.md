# Diagramas de la base de datos (Biblioteca)

| Archivo | Descripción |
|---|---|
| `er_chen.svg` / `er_chen.png` | Diagrama Entidad/Relación en notación Chen (entidades, atributos con la clave primaria subrayada, relaciones en rombo con cardinalidades 1/N/M y (mín,máx)). Las relaciones N:M `escrito por` y `tiene rol` van destacadas en naranja; la capa de seguridad (entidad `ROL`) aparece en un recuadro verde. |
| `relacional.svg` / `relacional.png` | Modelo relacional (lógico) para MariaDB: tablas con columnas, tipos y marcas PK / FK / UQ / NULL, flechas FK -> PK con pata de gallo e incluyendo las tablas intermedias `libro_autor` y `usuario_rol` (capa de seguridad: `roles`, `usuario_rol` y `usuarios.password`). |
| `relacional.mmd` | Equivalente en Mermaid `erDiagram` (se renderiza directamente en GitHub si se pega en un bloque ```` ```mermaid ````). |
| `er_chen.drawio` | Diagrama Chen editable en [diagrams.net](https://app.diagrams.net) (Archivo > Abrir). |
| `generar_diagramas.py` | Script generador de los SVG, PNG y el `.drawio`. |

Los PNG se exportan al doble de resolución (3200x2580 y 3200x1980) a partir de SVG de 1600x1290 y 1600x990.

## Regenerar

Requiere Python 3 (solo biblioteca estándar) y Google Chrome (`/usr/bin/google-chrome`, o indicar otra ruta con la variable `CHROME`):

```bash
python3 docs/diagramas/generar_diagramas.py
```

`relacional.mmd` se mantiene a mano; si cambia el modelo, actualiza también el script.
