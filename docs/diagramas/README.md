# Diagramas de la base de datos (Biblioteca)

| Archivo | Descripción |
|---|---|
| `er_chen.svg` / `er_chen.png` | Diagrama Entidad/Relación en notación Chen (entidades, atributos con la clave primaria subrayada, relaciones en rombo con cardinalidades 1/N/M y (mín,máx)). La relación N:M `escrito por` va destacada en naranja. |
| `relacional.svg` / `relacional.png` | Modelo relacional (lógico) para MariaDB: tablas con columnas, tipos y marcas PK / FK / UQ / NULL, flechas FK -> PK con pata de gallo e incluyendo la tabla intermedia `libro_autor`. |
| `relacional.mmd` | Equivalente en Mermaid `erDiagram` (se renderiza directamente en GitHub si se pega en un bloque ```` ```mermaid ````). |
| `er_chen.drawio` | Diagrama Chen editable en [diagrams.net](https://app.diagrams.net) (Archivo > Abrir). |
| `generar_diagramas.py` | Script generador de los SVG, PNG y el `.drawio`. |

Los PNG se exportan al doble de resolución (3200x2000 y 3200x1520) a partir de SVG de 1600x1000 y 1600x760.

## Regenerar

Requiere Python 3 (solo biblioteca estándar) y Google Chrome (`/usr/bin/google-chrome`, o indicar otra ruta con la variable `CHROME`):

```bash
python3 docs/diagramas/generar_diagramas.py
```

`relacional.mmd` se mantiene a mano; si cambia el modelo, actualiza también el script.
