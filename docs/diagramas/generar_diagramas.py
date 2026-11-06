#!/usr/bin/env python3
"""Genera los diagramas de la base de datos de Biblioteca.

Salidas (en la carpeta de este script): er_chen.svg/png, relacional.svg/png,
er_chen.drawio. Solo usa la biblioteca estandar + google-chrome (headless).
Uso: python3 generar_diagramas.py
"""
import os, subprocess, tempfile
from xml.sax.saxutils import escape

AQUI = os.path.dirname(os.path.abspath(__file__))
CHROME = os.environ.get("CHROME", "/usr/bin/google-chrome")
SANS = "DejaVu Sans, Arial, Helvetica, sans-serif"
MONO = "DejaVu Sans Mono, Consolas, monospace"

# ---------------------------------------------------------------- E/R Chen
W, H = 1600, 1000
EY = 500  # y de las entidades
ENT = {  # nombre: (cx, w)
    "USUARIO": 190, "PRÉSTAMO": 600, "LIBRO": 1010, "AUTOR": 1480}
EW, EH = 150, 60

# (texto, cx, cy, es_pk)
ATTRS = {
    "USUARIO": [("id", 190, 200, 1), ("nombre", 85, 300, 0), ("apellidos", 295, 300, 0),
                ("email (UQ)", 85, 700, 0), ("telefono", 295, 700, 0), ("fecha_alta", 190, 800, 0)],
    "PRÉSTAMO": [("id", 610, 200, 1), ("fecha_prestamo", 480, 300, 0),
                 ("fecha_devolucion_prevista", 735, 300, 0),
                 ("fecha_devolucion", 520, 700, 0), ("estado", 720, 700, 0)],
    "LIBRO": [("id", 1010, 200, 1), ("titulo", 910, 300, 0), ("isbn (UQ)", 1110, 300, 0),
              ("anio_publicacion", 900, 700, 0), ("ejemplares_disponibles", 1120, 700, 0),
              ("editorial", 1010, 800, 0)],
    "AUTOR": [("id", 1390, 300, 1), ("nacionalidad", 1530, 300, 0), ("nombre", 1480, 700, 0)],
}
# rombos: (texto, cx, ancho, destacado)
RELS = [
    ("realiza", 395, 130, False, "USUARIO", "PRÉSTAMO"),
    ("se presta en", 805, 140, False, "PRÉSTAMO", "LIBRO"),
    ("escrito por", 1245, 150, True, "LIBRO", "AUTOR"),
]
# cardinalidades: (rel_idx, lado_izq(card, minmax), lado_der(card, minmax))
CARD = [(("1", "(0,n)"), ("N", "(1,1)")),
        (("N", "(1,1)"), ("1", "(0,n)")),
        (("N", "(1,n)"), ("M", "(0,n)"))]

C_ENT, C_ENT_S = "#dbeafe", "#1e40af"
C_REL, C_REL_S = "#dcfce7", "#15803d"
C_NM, C_NM_S = "#fed7aa", "#c2410c"
C_ATT_S = "#475569"


def aw(t):
    return max(96, int(7.4 * len(t) + 30))


class Svg:
    def __init__(self, w, h):
        self.w, self.h, self.p = w, h, []

    def add(self, s):
        self.p.append(s)

    def text(self, x, y, t, size=13, anchor="middle", weight="normal", fill="#0f172a",
             font=SANS, deco=None, style=""):
        d = f' text-decoration="{deco}"' if deco else ""
        self.add(f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" '
                 f'font-weight="{weight}" fill="{fill}" font-family="{font}" '
                 f'dominant-baseline="central"{d} {style}>{escape(t)}</text>')

    def out(self):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" '
                f'viewBox="0 0 {self.w} {self.h}">'
                f'<rect width="{self.w}" height="{self.h}" fill="#ffffff"/>' + "".join(self.p) + "</svg>")


def diamond_pts(cx, cy, w, h):
    return f"{cx},{cy-h/2} {cx+w/2},{cy} {cx},{cy+h/2} {cx-w/2},{cy}"


def chen():
    s = Svg(W, H)
    s.text(W / 2, 38, "Diagrama Entidad/Relación (notación Chen) · Biblioteca", 22, weight="bold")
    # lineas (debajo de las formas)
    for e, lst in ATTRS.items():
        for t, x, y, pk in lst:
            s.add(f'<line x1="{ENT[e]}" y1="{EY}" x2="{x}" y2="{y}" stroke="{C_ATT_S}" stroke-width="1.3"/>')
    for i, (t, cx, w, nm, a, b) in enumerate(RELS):
        s.add(f'<line x1="{ENT[a]}" y1="{EY}" x2="{ENT[b]}" y2="{EY}" stroke="#1f2937" stroke-width="{3 if nm else 2}"/>')
    # atributos
    for e, lst in ATTRS.items():
        for t, x, y, pk in lst:
            s.add(f'<ellipse cx="{x}" cy="{y}" rx="{aw(t)/2}" ry="23" fill="#ffffff" stroke="{C_ATT_S}" stroke-width="1.5"/>')
            s.text(x, y, t, 13, deco="underline" if pk else None, weight="bold" if pk else "normal")
    # entidades
    for e, x in ENT.items():
        s.add(f'<rect x="{x-EW/2}" y="{EY-EH/2}" width="{EW}" height="{EH}" fill="{C_ENT}" stroke="{C_ENT_S}" stroke-width="2.5"/>')
        s.text(x, EY, e, 17, weight="bold", fill="#1e3a8a")
    # rombos
    for i, (t, cx, w, nm, a, b) in enumerate(RELS):
        f, st = (C_NM, C_NM_S) if nm else (C_REL, C_REL_S)
        h = 90 if nm else 80
        s.add(f'<polygon points="{diamond_pts(cx, EY, w, h)}" fill="{f}" stroke="{st}" stroke-width="{3.5 if nm else 2}"/>')
        s.text(cx, EY, t, 13, weight="bold", fill="#7c2d12" if nm else "#14532d")
        if nm:
            s.add(f'<rect x="{cx-30}" y="{EY+h/2+8}" width="60" height="26" rx="13" fill="{C_NM_S}"/>')
            s.text(cx, EY + h / 2 + 21, "N:M", 14, weight="bold", fill="#ffffff")
            s.text(cx, EY + h / 2 + 52, "se resuelve en la tabla", 12, fill="#7c2d12")
            s.text(cx, EY + h / 2 + 68, "intermedia libro_autor", 12, fill="#7c2d12", font=SANS)
        # cardinalidades
        (cl, ml), (cr, mr) = CARD[i]
        xl = ENT[a] + EW / 2
        xr = ENT[b] - EW / 2
        s.text(xl + 26, EY - 14, cl, 16, weight="bold", fill="#b91c1c")
        s.text(xl + 28, EY + 16, ml, 13, fill="#475569")
        s.text(xr - 26, EY - 14, cr, 16, weight="bold", fill="#b91c1c")
        s.text(xr - 28, EY + 16, mr, 13, fill="#475569")
    # leyenda
    ly = 880
    s.add(f'<rect x="30" y="{ly}" width="1540" height="96" rx="8" fill="#f8fafc" stroke="#cbd5e1"/>')
    s.text(48, ly + 18, "Leyenda", 13, "start", "bold")
    cy = ly + 56
    s.add(f'<rect x="48" y="{cy-14}" width="56" height="28" fill="{C_ENT}" stroke="{C_ENT_S}" stroke-width="2"/>')
    s.text(114, cy, "Entidad", 13, "start")
    s.add(f'<ellipse cx="225" cy="{cy}" rx="30" ry="15" fill="#fff" stroke="{C_ATT_S}" stroke-width="1.5"/>')
    s.text(265, cy, "Atributo", 13, "start")
    s.add(f'<ellipse cx="385" cy="{cy}" rx="30" ry="15" fill="#fff" stroke="{C_ATT_S}" stroke-width="1.5"/>')
    s.text(385, cy, "id", 13, deco="underline", weight="bold")
    s.text(425, cy, "Clave primaria (subrayado)", 13, "start")
    s.add(f'<polygon points="{diamond_pts(665, cy, 56, 34)}" fill="{C_REL}" stroke="{C_REL_S}" stroke-width="2"/>')
    s.text(702, cy, "Relación", 13, "start")
    s.add(f'<polygon points="{diamond_pts(830, cy, 56, 34)}" fill="{C_NM}" stroke="{C_NM_S}" stroke-width="3"/>')
    s.text(867, cy, "Relación N:M", 13, "start")
    s.text(1000, cy - 12, "1 / N / M = cardinalidad máxima (Chen)", 13, "start", fill="#b91c1c")
    s.text(1000, cy + 10, "(mín,máx) = participación de la entidad · (UQ) = valor único", 13, "start", fill="#475569")
    return s


# ------------------------------------------------------------- drawio (Chen)
def drawio():
    cells, ids = [], {}
    n = [1]

    def nid():
        n[0] += 1
        return f"c{n[0]}"

    def cell(value, style, x, y, w, h):
        i = nid()
        cells.append(f'<mxCell id="{i}" value="{escape(value, {chr(34): "&quot;"})}" style="{style}" vertex="1" parent="1">'
                     f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>')
        return i

    def edge(a, b, style="endArrow=none;html=1;strokeWidth=1.5;"):
        i = nid()
        cells.append(f'<mxCell id="{i}" style="{style}" edge="1" parent="1" source="{a}" target="{b}">'
                     f'<mxGeometry relative="1" as="geometry"/></mxCell>')

    for e, x in ENT.items():
        ids[e] = cell(e, f"rounded=0;whiteSpace=wrap;html=1;fillColor={C_ENT};strokeColor={C_ENT_S};strokeWidth=2;fontStyle=1;fontSize=15;",
                      x - EW / 2, EY - EH / 2, EW, EH)
    for e, lst in ATTRS.items():
        for t, x, y, pk in lst:
            w = aw(t)
            a = cell(t, f"ellipse;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor={C_ATT_S};fontSize=12;" + ("fontStyle=5;" if pk else ""),
                     x - w / 2, y - 23, w, 46)
            edge(a, ids[e], "endArrow=none;html=1;strokeColor=#475569;")
    for i, (t, cx, w, nm, a, b) in enumerate(RELS):
        h = 90 if nm else 80
        f, st = (C_NM, C_NM_S) if nm else (C_REL, C_REL_S)
        r = cell(t, f"rhombus;whiteSpace=wrap;html=1;fillColor={f};strokeColor={st};strokeWidth={3 if nm else 2};fontStyle=1;fontSize=12;",
                 cx - w / 2, EY - h / 2, w, h)
        edge(ids[a], r, "endArrow=none;html=1;strokeWidth=2;")
        edge(r, ids[b], "endArrow=none;html=1;strokeWidth=2;")
        if nm:
            cell("N:M (tabla intermedia libro_autor)", f"text;html=1;align=center;verticalAlign=middle;fontStyle=1;fontColor={C_NM_S};",
                 cx - 100, EY + h / 2 + 6, 200, 24)
        (cl, ml), (cr, mr) = CARD[i]
        xl, xr = ENT[a] + EW / 2, ENT[b] - EW / 2
        for txt, x, y, st in ((cl, xl + 26, EY - 14, "fontStyle=1;fontSize=14;fontColor=#b91c1c;"),
                              (ml, xl + 28, EY + 16, "fontSize=12;fontColor=#475569;"),
                              (cr, xr - 26, EY - 14, "fontStyle=1;fontSize=14;fontColor=#b91c1c;"),
                              (mr, xr - 28, EY + 16, "fontSize=12;fontColor=#475569;")):
            cell(txt, "text;html=1;align=center;verticalAlign=middle;" + st, x - 22, y - 10, 44, 20)
    return ('<mxfile host="app.diagrams.net"><diagram id="er-chen" name="ER Chen - Biblioteca">'
            f'<mxGraphModel dx="1600" dy="1000" grid="1" gridSize="10" page="1" pageScale="1" pageWidth="{W}" pageHeight="{H}">'
            '<root><mxCell id="0"/><mxCell id="1" parent="0"/>' + "".join(cells) +
            '</root></mxGraphModel></diagram></mxfile>')


# --------------------------------------------------------------- Relacional
RW, RH = 1600, 760
HDR, ROW = 40, 30
TABLAS = {  # nombre: (x, y, w, [(col, tipo, marcas)], nota)
    "usuarios": (40, 110, 290, [("id", "BIGINT", ["PK"]), ("nombre", "VARCHAR(100)", []),
                                 ("apellidos", "VARCHAR(150)", []), ("email", "VARCHAR(150)", ["UQ"]),
                                 ("telefono", "VARCHAR(20)", ["NULL"]), ("fecha_alta", "DATE", [])], None),
    "prestamos": (430, 110, 340, [("id", "BIGINT", ["PK"]), ("usuario_id", "BIGINT", ["FK"]),
                                   ("libro_id", "BIGINT", ["FK"]), ("fecha_prestamo", "DATE", []),
                                   ("fecha_devolucion_prevista", "DATE", []),
                                   ("fecha_devolucion", "DATE", ["NULL"]), ("estado", "VARCHAR(20)", [])],
                  ["estado: DEFAULT 'ACTIVO'", "CHECK (ACTIVO | DEVUELTO | RETRASADO)"]),
    "libros": (880, 110, 310, [("id", "BIGINT", ["PK"]), ("titulo", "VARCHAR(200)", []),
                                ("isbn", "VARCHAR(20)", ["UQ"]), ("editorial", "VARCHAR(150)", ["NULL"]),
                                ("anio_publicacion", "INT", ["NULL"]), ("ejemplares_disponibles", "INT", [])],
                ["ejemplares_disponibles: DEFAULT 1"]),
    "libro_autor": (1290, 110, 290, [("libro_id", "BIGINT", ["PK", "FK"]), ("autor_id", "BIGINT", ["PK", "FK"])],
                    ["PK compuesta (libro_id, autor_id)", "FK: ON DELETE CASCADE"]),
    "autores": (1290, 330, 290, [("id", "BIGINT", ["PK"]), ("nombre", "VARCHAR(150)", []),
                                  ("nacionalidad", "VARCHAR(100)", ["NULL"])], None),
}
BADGE = {"PK": ("#fef3c7", "#b45309"), "FK": ("#dbeafe", "#1d4ed8"),
         "UQ": ("#ede9fe", "#6d28d9"), "NULL": ("#f1f5f9", "#475569")}


def rowy(t, i):
    x, y, w, cols, _ = TABLAS[t]
    return y + HDR + i * ROW + ROW / 2


def crow(s, x, y, d, col="#1f2937"):
    """Pata de gallo (muchos) en (x,y); d=+1 si la linea llega desde la derecha, -1 desde la izquierda."""
    for dy in (-9, 0, 9):
        s.add(f'<line x1="{x+d*16}" y1="{y}" x2="{x}" y2="{y+dy}" stroke="{col}" stroke-width="1.8"/>')


def one(s, x, y, d, col="#1f2937"):
    for off in (10, 16):
        s.add(f'<line x1="{x+d*off}" y1="{y-8}" x2="{x+d*off}" y2="{y+8}" stroke="{col}" stroke-width="1.8"/>')


def relacional():
    s = Svg(RW, RH)
    s.text(RW / 2, 38, "Modelo relacional (lógico) · Biblioteca · MariaDB", 22, weight="bold")
    s.text(RW / 2, 66, "Las flechas van de la clave foránea (FK, lado N) a la clave primaria (PK, lado 1)", 13, fill="#475569")
    ln = "#1f2937"
    # conexiones (debajo de las tablas)
    def path(d):
        s.add(f'<path d="{d}" fill="none" stroke="{ln}" stroke-width="1.8"/>')
    # prestamos.usuario_id -> usuarios.id
    xp, yp, wp, _, _ = TABLAS["prestamos"]
    xu, yu, wu, _, _ = TABLAS["usuarios"]
    xl, yl, wl, _, _ = TABLAS["libros"]
    xa, ya, wa, _, _ = TABLAS["libro_autor"]
    xr, yr, wr, _, _ = TABLAS["autores"]
    a, b, mx = rowy("prestamos", 1), rowy("usuarios", 0), (xu + wu + xp) / 2
    path(f"M{xp},{a} H{mx} V{b} H{xu+wu}")
    crow(s, xp, a, -1); one(s, xu + wu, b, 1)
    s.text(xp - 14, a - 16, "N", 14, weight="bold", fill="#b91c1c")
    s.text(xu + wu + 14, b - 16, "1", 14, weight="bold", fill="#b91c1c")
    # prestamos.libro_id -> libros.id
    a, b, mx = rowy("prestamos", 2), rowy("libros", 0), (xp + wp + xl) / 2
    path(f"M{xp+wp},{a} H{mx} V{b} H{xl}")
    crow(s, xp + wp, a, 1); one(s, xl, b, -1)
    s.text(xp + wp + 14, a - 16, "N", 14, weight="bold", fill="#b91c1c")
    s.text(xl - 14, b - 16, "1", 14, weight="bold", fill="#b91c1c")
    # libro_autor.libro_id -> libros.id
    a, b = rowy("libro_autor", 0), rowy("libros", 0)
    path(f"M{xa},{a} H{xl+wl}")
    crow(s, xa, a, -1); one(s, xl + wl, b, 1)
    s.text(xa - 14, a - 16, "N", 14, weight="bold", fill="#b91c1c")
    s.text(xl + wl + 14, b - 16, "1", 14, weight="bold", fill="#b91c1c")
    # libro_autor.autor_id -> autores.id (por abajo)
    cx = xa + wa - 20
    ybot = ya + HDR + 2 * ROW
    path(f"M{cx},{ybot} V{yr}")
    for dx in (-9, 0, 9):
        s.add(f'<line x1="{cx}" y1="{ybot+16}" x2="{cx+dx}" y2="{ybot}" stroke="{ln}" stroke-width="1.8"/>')
    for off in (10, 16):
        s.add(f'<line x1="{cx-8}" y1="{yr-off}" x2="{cx+8}" y2="{yr-off}" stroke="{ln}" stroke-width="1.8"/>')
    s.text(cx + 18, ybot + 18, "N", 14, "start", weight="bold", fill="#b91c1c")
    s.text(cx + 18, yr - 14, "1", 14, "start", weight="bold", fill="#b91c1c")
    # tablas
    for t, (x, y, w, cols, nota) in TABLAS.items():
        h = HDR + len(cols) * ROW
        s.add(f'<rect x="{x+3}" y="{y+3}" width="{w}" height="{h}" rx="6" fill="#0f172a" opacity="0.08"/>')
        s.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="#ffffff" stroke="#1e40af" stroke-width="2"/>')
        inter = t == "libro_autor"
        s.add(f'<path d="M{x},{y+HDR} V{y+6} Q{x},{y} {x+6},{y} H{x+w-6} Q{x+w},{y} {x+w},{y+6} V{y+HDR} Z" fill="{C_NM_S if inter else "#1e40af"}"/>')
        s.text(x + w / 2, y + HDR / 2, t + (" (N:M)" if inter else ""), 15, weight="bold", fill="#ffffff")
        for i, (c, ty, marks) in enumerate(cols):
            ry = y + HDR + i * ROW
            if i:
                s.add(f'<line x1="{x}" y1="{ry}" x2="{x+w}" y2="{ry}" stroke="#e2e8f0"/>')
            s.text(x + 12, ry + ROW / 2, f"{c} : {ty}", 13, "start", "bold" if "PK" in marks else "normal", font=MONO)
            bx = x + w - 8
            for m in reversed(marks):
                bw = 40 if m == "NULL" else 30
                bx -= bw
                f, st = BADGE[m]
                s.add(f'<rect x="{bx}" y="{ry+6}" width="{bw}" height="18" rx="4" fill="{f}" stroke="{st}"/>')
                s.text(bx + bw / 2, ry + 15, m, 10.5, weight="bold", fill=st)
                bx -= 4
        if nota:
            for k, ln_ in enumerate(nota):
                s.text(x + 4, y + h + 18 + 16 * k, ln_, 12, "start", fill="#475569", style='font-style="italic"')
    # leyenda / notas
    ly = 470
    s.add(f'<rect x="40" y="{ly}" width="1000" height="250" rx="8" fill="#f8fafc" stroke="#cbd5e1"/>')
    s.text(58, ly + 20, "Leyenda y relaciones", 14, "start", "bold")
    x0 = 58
    for k, (m, d) in enumerate([("PK", "clave primaria"), ("FK", "clave foránea"), ("UQ", "valor único (UNIQUE)"),
                                ("NULL", "admite nulos (el resto es NOT NULL)")]):
        px = x0 + [0, 150, 300, 500][k]
        f, st = BADGE[m]
        bw = 40 if m == "NULL" else 30
        s.add(f'<rect x="{px}" y="{ly+40}" width="{bw}" height="18" rx="4" fill="{f}" stroke="{st}"/>')
        s.text(px + bw / 2, ly + 49, m, 10.5, weight="bold", fill=st)
        s.text(px + bw + 8, ly + 49, d, 12.5, "start")
    cy = ly + 85
    crow(s, 70, cy, 1); s.text(100, cy, "extremo «muchos» (N): lado de la clave foránea", 12.5, "start")
    one(s, 570, cy, 1); s.text(595, cy, "extremo «uno» (1): lado de la clave primaria", 12.5, "start")
    rel = ["usuarios 1 : N prestamos   (prestamos.usuario_id → usuarios.id)",
           "libros 1 : N prestamos   (prestamos.libro_id → libros.id)",
           "libros N : M autores   (a través de libro_autor, PK compuesta libro_id + autor_id)",
           "libro_autor.libro_id → libros.id   y   libro_autor.autor_id → autores.id",
           "Claves BIGINT AUTO_INCREMENT · libro_autor: ambas FK con ON DELETE CASCADE · prestamos.estado: VARCHAR(20) + CHECK"]
    for i, r in enumerate(rel):
        s.text(58, ly + 125 + i * 24, "• " + r, 13, "start", font=SANS)
    return s


# ------------------------------------------------------------------ salida
def png(svg, w, h, dest):
    with tempfile.TemporaryDirectory() as d:
        html = os.path.join(d, "w.html")
        with open(html, "w") as f:
            f.write(f'<!doctype html><html><head><meta charset="utf-8"></head>'
                    f'<body style="margin:0;background:#fff">{svg}</body></html>')
        subprocess.run([CHROME, "--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
                        "--force-device-scale-factor=2", f"--screenshot={dest}",
                        f"--window-size={w},{h}", "file://" + html],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def main():
    for nombre, s in (("er_chen", chen()), ("relacional", relacional())):
        svg = s.out()
        with open(os.path.join(AQUI, nombre + ".svg"), "w", encoding="utf-8") as f:
            f.write(svg)
        png(svg, s.w, s.h, os.path.join(AQUI, nombre + ".png"))
        print("generado", nombre)
    with open(os.path.join(AQUI, "er_chen.drawio"), "w", encoding="utf-8") as f:
        f.write(drawio())
    print("generado er_chen.drawio")


if __name__ == "__main__":
    main()
