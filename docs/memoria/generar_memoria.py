#!/usr/bin/env python3
"""Genera la memoria del Producto 2 (FP065) en DOCX.

Uso:
    python3 -m venv /tmp/docvenv && /tmp/docvenv/bin/pip install python-docx
    /tmp/docvenv/bin/python docs/memoria/generar_memoria.py
    python3 docs/memoria/exportar_pdf.py   # PDF con el índice actualizado (LibreOffice)

El script lee en cada ejecución los ficheros reales del repositorio
(application.properties, docker-compose.yml, db/init.sql, Dockerfile...) para
citar fragmentos, e inserta los diagramas, mockups y capturas que existan.
Las capturas reales de la app se colocan en docs/memoria/capturas/ con los
nombres indicados en CAPTURAS; si falta alguna se deja un hueco marcado.
"""
from pathlib import Path
import re

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

DOCS = Path(__file__).resolve().parent.parent
REPO = DOCS.parent
SALIDA = DOCS / "memoria" / "producto2(FP065)_ValeroSanz_Andrea.docx"

ALUMNA = "Andrea Valero Sanz"
MODULO = "FP065 · Desarrollo back-end"
PRODUCTO = "Producto 2"
TITULO = "Aplicación web de gestión de Biblioteca"
SUBTITULO = "Spring Boot + Spring Data JPA + Thymeleaf + MariaDB + Docker"
VIDEO_URL = None  # p.ej. "https://youtu.be/XXXXXXXXXXX" cuando esté publicado

AZUL = RGBColor(0x1F, 0x3A, 0x5F)
GRIS = RGBColor(0x55, 0x55, 0x55)

DIAGRAMAS = [
    ("diagramas/er_chen.png", "Diagrama Entidad/Relación (notación Chen)"),
    ("diagramas/relacional.png", "Modelo relacional (tablas, claves primarias y foráneas)"),
]
MOCKUPS = [
    ("mockups/png/01-dashboard.png", "Mockup – Inicio / dashboard (ruta /)"),
    ("mockups/png/02-libros-listado.png", "Mockup – Listado de libros (/libros)"),
    ("mockups/png/03-libro-formulario.png", "Mockup – Formulario de libro (/libros/nuevo, /libros/{id}/editar)"),
    ("mockups/png/04-prestamos-listado.png", "Mockup – Listado de préstamos (/prestamos)"),
    ("mockups/png/05-prestamo-formulario.png", "Mockup – Nuevo préstamo (/prestamos/nuevo)"),
    ("mockups/png/06-usuarios-listado.png", "Mockup – Listado de usuarios (/usuarios)"),
    ("mockups/png/07-usuario-formulario.png", "Mockup – Formulario de usuario (/usuarios/nuevo)"),
    ("mockups/png/08-autores-listado.png", "Mockup – Listado de autores (/autores)"),
]
CAPTURAS = [
    ("memoria/capturas/01-dashboard.png", "Captura – Página de inicio con contadores y últimos préstamos"),
    ("memoria/capturas/02-libros.png", "Captura – Listado de libros con sus autores"),
    ("memoria/capturas/03-libro-form.png", "Captura – Formulario de libro con selección múltiple de autores"),
    ("memoria/capturas/04-prestamos.png", "Captura – Listado de préstamos con estados y botón «Marcar devuelto»"),
    ("memoria/capturas/05-usuarios.png", "Captura – Listado de usuarios"),
    ("memoria/capturas/06-docker.png", "Captura – docker compose ps (app y db en marcha) y códigos HTTP 200 de todas las rutas"),
    ("memoria/capturas/07-libro-validacion.png", "Captura – Errores de validación al guardar un libro sin título ni ISBN"),
    ("memoria/capturas/08-borrado-bloqueado.png", "Captura – Borrado bloqueado de un libro que tiene préstamos asociados"),
    ("memoria/capturas/09-prestamo-nuevo.png", "Captura – Formulario de nuevo préstamo"),
    ("memoria/capturas/10-autores.png", "Captura – Listado de autores con el número de libros de cada uno"),
    ("memoria/capturas/11-usuario-editar.png", "Captura – Edición de un usuario"),
]
REPO_URL = "https://github.com/andreavalerosanz-rgb/biblioteca-p2"

doc = Document()
_figura = 0


# ---------------------------------------------------------------- utilidades
def leer(rel):
    p = REPO / rel
    return p.read_text(encoding="utf-8") if p.exists() else None


def sombrear(elemento, color):
    pr = elemento.get_or_add_pPr() if hasattr(elemento, "get_or_add_pPr") else elemento
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), color)
    pr.append(shd)


def sombrear_celda(celda, color):
    tcPr = celda._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), color)
    tcPr.append(shd)


def borde_inferior(parrafo, color="1F3A5F", grosor=8):
    pPr = parrafo._p.get_or_add_pPr()
    bdr = OxmlElement("w:pBdr")
    b = OxmlElement("w:bottom")
    b.set(qn("w:val"), "single")
    b.set(qn("w:sz"), str(grosor))
    b.set(qn("w:space"), "4")
    b.set(qn("w:color"), color)
    bdr.append(b)
    pPr.append(bdr)


def campo(parrafo, instr):
    run = parrafo.add_run()
    for tipo, texto in (("begin", None), (None, instr), ("separate", None), ("end", None)):
        if tipo:
            fc = OxmlElement("w:fldChar")
            fc.set(qn("w:fldCharType"), tipo)
            run._r.append(fc)
        else:
            it = OxmlElement("w:instrText")
            it.set(qn("xml:space"), "preserve")
            it.text = texto
            run._r.append(it)
    return run


def h1(texto):
    return doc.add_heading(texto, level=1)


def h2(texto):
    return doc.add_heading(texto, level=2)


def p(texto="", negrita=False, cursiva=False):
    par = doc.add_paragraph()
    _inline(par, texto, negrita, cursiva)
    return par


def _inline(par, texto, negrita=False, cursiva=False):
    """Admite **negrita** y `código` dentro del texto."""
    for trozo in re.split(r"(\*\*[^*]+\*\*|`[^`]+`)", texto):
        if not trozo:
            continue
        if trozo.startswith("**"):
            r = par.add_run(trozo[2:-2])
            r.bold = True
        elif trozo.startswith("`"):
            r = par.add_run(trozo[1:-1])
            r.font.name = "Consolas"
            r.font.size = Pt(9.5)
        else:
            r = par.add_run(trozo)
            r.bold = negrita
        r.italic = cursiva or r.italic


def vineta(texto, nivel=0):
    par = doc.add_paragraph(style="List Bullet" if nivel == 0 else "List Bullet 2")
    _inline(par, texto)
    return par


def numerada(texto):
    par = doc.add_paragraph(style="List Number")
    _inline(par, texto)
    return par


def codigo(texto, titulo=None):
    if titulo:
        t = doc.add_paragraph()
        r = t.add_run(titulo)
        r.bold = True
        r.font.size = Pt(9)
        r.font.color.rgb = GRIS
        t.paragraph_format.space_after = Pt(2)
        t.paragraph_format.keep_with_next = True
    tabla = doc.add_table(rows=1, cols=1)
    tabla.alignment = WD_TABLE_ALIGNMENT.CENTER
    celda = tabla.cell(0, 0)
    sombrear_celda(celda, "F3F4F6")
    celda.paragraphs[0].text = ""
    lineas = texto.rstrip("\n").split("\n")
    for i, linea in enumerate(lineas):
        par = celda.paragraphs[0] if i == 0 else celda.add_paragraph()
        par.paragraph_format.space_after = Pt(0)
        par.paragraph_format.line_spacing = 1.0
        r = par.add_run(linea if linea else " ")
        r.font.name = "Consolas"
        r._r.get_or_add_rPr().get_or_add_rFonts().set(qn("w:eastAsia"), "Consolas")
        r.font.size = Pt(8.5)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


def hueco(texto):
    """Recuadro amarillo para contenido pendiente de insertar."""
    tabla = doc.add_table(rows=1, cols=1)
    tabla.style = "Table Grid"
    tabla.alignment = WD_TABLE_ALIGNMENT.CENTER
    celda = tabla.cell(0, 0)
    sombrear_celda(celda, "FFF4C2")
    par = celda.paragraphs[0]
    par.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = par.add_run("⚠ PENDIENTE · " + texto)
    r.bold = True
    r.font.color.rgb = RGBColor(0x8A, 0x5A, 0x00)
    doc.add_paragraph()


def figura(rel, pie, ancho_cm=16):
    global _figura
    ruta = DOCS / rel
    if not ruta.exists():
        hueco(f"Insertar imagen «{pie}» (archivo esperado: docs/{rel})")
        return
    _figura += 1
    par = doc.add_paragraph()
    par.alignment = WD_ALIGN_PARAGRAPH.CENTER
    par.paragraph_format.keep_with_next = True
    par.add_run().add_picture(str(ruta), width=Cm(ancho_cm))
    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = cap.add_run(f"Figura {_figura}. {pie}")
    r.italic = True
    r.font.size = Pt(9)
    r.font.color.rgb = GRIS


def tabla(cabecera, filas, anchos=None):
    t = doc.add_table(rows=1, cols=len(cabecera))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, c in enumerate(cabecera):
        celda = t.rows[0].cells[i]
        celda.text = ""
        r = celda.paragraphs[0].add_run(c)
        r.bold = True
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        sombrear_celda(celda, "1F3A5F")
    for fila in filas:
        cells = t.add_row().cells
        for i, v in enumerate(fila):
            cells[i].text = ""
            _inline(cells[i].paragraphs[0], str(v))
    for fila in t.rows:
        for c in fila.cells:
            for par in c.paragraphs:
                par.paragraph_format.space_after = Pt(1)
                for r in par.runs:
                    r.font.size = Pt(9.5)
    if anchos:
        t.autofit = False
        for col, a in zip(t._tbl.tblGrid.findall(qn("w:gridCol")), anchos):
            col.set(qn("w:w"), str(int(a * 567)))
        for fila in t.rows:
            for i, a in enumerate(anchos):
                fila.cells[i].width = Cm(a)
    doc.add_paragraph()
    return t


def extraer(texto, inicio, fin=None, max_lineas=40):
    """Devuelve el bloque desde la línea que contiene `inicio` hasta `fin` (incluida)."""
    if not texto:
        return None
    lineas = texto.split("\n")
    for i, l in enumerate(lineas):
        if inicio in l:
            res = []
            for l2 in lineas[i:]:
                res.append(l2)
                if (fin and fin in l2 and len(res) > 1) or len(res) >= max_lineas:
                    break
            return "\n".join(res)
    return None


# ---------------------------------------------------------------- estilos
st = doc.styles["Normal"]
st.font.name = "Calibri"
st._element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")
st.font.size = Pt(11)
st.paragraph_format.space_after = Pt(6)
st.paragraph_format.line_spacing = 1.15
for nombre, tam in (("Heading 1", 16), ("Heading 2", 13), ("Heading 3", 11.5)):
    s = doc.styles[nombre]
    s.font.name = "Calibri"
    s._element.rPr.rFonts.set(qn("w:asciiTheme"), "") if False else None
    s.font.size = Pt(tam)
    s.font.color.rgb = AZUL
    s.font.bold = True
    s.paragraph_format.space_before = Pt(14 if nombre == "Heading 1" else 10)
    s.paragraph_format.space_after = Pt(6)

sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21), Cm(29.7)
for lado in ("left_margin", "right_margin"):
    setattr(sec, lado, Cm(2.3))
sec.top_margin, sec.bottom_margin = Cm(2.2), Cm(2.2)
sec.different_first_page_header_footer = True

# ---------------------------------------------------------------- portada
for _ in range(6):
    doc.add_paragraph()
par = doc.add_paragraph()
par.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = par.add_run(f"{MODULO}")
r.font.size = Pt(14)
r.font.color.rgb = GRIS
par = doc.add_paragraph()
par.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = par.add_run(PRODUCTO)
r.font.size = Pt(30)
r.bold = True
r.font.color.rgb = AZUL
par = doc.add_paragraph()
par.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = par.add_run(TITULO)
r.font.size = Pt(20)
r.font.color.rgb = AZUL
borde_inferior(par)
par = doc.add_paragraph()
par.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = par.add_run(SUBTITULO)
r.font.size = Pt(12)
r.italic = True
r.font.color.rgb = GRIS
for _ in range(10):
    doc.add_paragraph()
for etiqueta, valor in (("Alumna", ALUMNA), ("Módulo", MODULO), ("Entrega", PRODUCTO),
                        ("Curso", "2026/2027")):
    par = doc.add_paragraph()
    par.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    par.paragraph_format.space_after = Pt(2)
    r = par.add_run(f"{etiqueta}: ")
    r.bold = True
    par.add_run(valor)
doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)

# cabecera/pie (no en portada)
cab = sec.header.paragraphs[0]
cab.text = f"{PRODUCTO} · {TITULO}"
cab.alignment = WD_ALIGN_PARAGRAPH.RIGHT
for r in cab.runs:
    r.font.size = Pt(8.5)
    r.font.color.rgb = GRIS
pie = sec.footer.paragraphs[0]
pie.alignment = WD_ALIGN_PARAGRAPH.CENTER
rr = pie.add_run(f"{ALUMNA} · Página ")
rr.font.size = Pt(8.5)
campo(pie, "PAGE").font.size = Pt(8.5)

# ---------------------------------------------------------------- índice
tit = doc.add_paragraph()  # no es Heading para que no aparezca dentro del propio índice
r = tit.add_run("Índice")
r.bold = True
r.font.size = Pt(16)
r.font.color.rgb = AZUL
par = doc.add_paragraph()
campo(par, 'TOC \\o "1-2" \\h \\z \\u')
nota = doc.add_paragraph()
r = nota.add_run("(Si el índice aparece vacío, en Word: clic derecho → «Actualizar campo». "
                 "En LibreOffice: Herramientas → Actualizar → Índices.)")
r.italic = True
r.font.size = Pt(8.5)
r.font.color.rgb = GRIS
doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)

# ---------------------------------------------------------------- 1. introducción
h1("1. Introducción")
p("Este documento es la memoria del **Producto 2** del módulo FP065. El objetivo es desarrollar "
  "una aplicación web del lado servidor que gestione los datos de una **biblioteca**: su catálogo de "
  "libros, los autores de cada libro, los usuarios (socios) y los préstamos de libros a esos usuarios.")
p("La aplicación sigue el patrón **Modelo-Vista-Controlador (MVC)** con **Spring Boot**. La persistencia "
  "se implementa con **Spring Data JPA** (Hibernate) sobre una base de datos **MariaDB**, las vistas se "
  "generan en el servidor con **Thymeleaf** y se maquetan con **Bootstrap 5**. Toda la solución "
  "(aplicación + base de datos) se levanta con **Docker Compose**, de forma que cualquiera puede "
  "ejecutarla con un único comando sin instalar Java ni MariaDB.")
p(f"El código fuente está en el repositorio (privado) **{REPO_URL}**.")
p("La memoria recoge los requisitos, el diseño de la base de datos (modelo E/R y modelo relacional), "
  "los mockups de las pantallas, la arquitectura del código, la configuración de la base de datos y de "
  "Docker, el trabajo realizado, las dificultades encontradas, las mejoras propuestas y una "
  "autoevaluación según la rúbrica.")

h2("1.1. Tecnologías utilizadas")
tabla(["Capa", "Tecnología", "Uso en el proyecto"], [
    ["Lenguaje", "Java 25", "Código de la aplicación"],
    ["Framework", "Spring Boot 4 (spring-boot-starter-webmvc)", "Arranque, servidor embebido, controladores MVC"],
    ["Persistencia", "Spring Data JPA + Hibernate", "Entidades, repositorios y consultas derivadas"],
    ["Validación", "Jakarta Bean Validation", "@NotBlank, @Email, @Min… en las entidades"],
    ["Vistas", "Thymeleaf + Bootstrap 5 + Bootstrap Icons", "Plantillas HTML renderizadas en servidor y hoja de estilos propia (biblioteca.css)"],
    ["Base de datos", "MariaDB 11", "Almacenamiento; driver mariadb-java-client"],
    ["Contenedores", "Docker + Docker Compose", "Imagen multi-etapa de la app y servicio de BD"],
    ["Construcción", "Maven (wrapper mvnw)", "Compilación y empaquetado en JAR"],
], anchos=[3, 6, 7.4])

# ---------------------------------------------------------------- 2. requisitos
h1("2. Requisitos")
h2("2.1. Requisitos funcionales")
tabla(["ID", "Requisito"], [
    ["RF-01", "Mostrar una página de inicio con el número de libros, usuarios y préstamos activos, y los últimos préstamos realizados."],
    ["RF-02", "Listar, crear, editar y eliminar **libros** (título, ISBN, editorial, año de publicación y ejemplares disponibles)."],
    ["RF-03", "Asignar a cada libro **uno o varios autores** mediante casillas de selección múltiple (relación N:M)."],
    ["RF-04", "Listar y dar de alta **autores** (nombre y nacionalidad), mostrando cuántos libros tiene cada uno."],
    ["RF-05", "Listar, crear, editar y eliminar **usuarios** (nombre, apellidos, email único, teléfono y fecha de alta)."],
    ["RF-06", "Registrar un **préstamo** eligiendo usuario y libro, con fecha de préstamo y fecha de devolución prevista."],
    ["RF-07", "**Devolver** un préstamo: se guarda la fecha de devolución, el estado pasa a DEVUELTO y se repone el ejemplar."],
    ["RF-08", "Mostrar el **estado** de cada préstamo (ACTIVO, DEVUELTO, RETRASADO) con un distintivo de color."],
    ["RF-09", "No permitir prestar un libro sin ejemplares disponibles ni borrar libros/usuarios con préstamos asociados."],
    ["RF-10", "Validar los formularios y mostrar mensajes de error junto al campo y avisos de éxito tras cada operación."],
], anchos=[1.8, 14.6])
h2("2.2. Requisitos no funcionales")
vineta("**Arquitectura MVC** con separación en paquetes `model`, `repository`, `controller` y plantillas en `templates`.")
vineta("**Persistencia en MariaDB** con integridad referencial (claves foráneas) y restricciones de unicidad (email, ISBN).")
vineta("**Despliegue reproducible con Docker Compose**: la base de datos se inicializa sola con `db/init.sql`.")
vineta("**Configuración externalizada**: credenciales y URL de la BD por variables de entorno con valores por defecto.")
vineta("Interfaz **responsive** y homogénea con Bootstrap 5: barra de navegación común y estilos de botón coherentes.")
vineta("Textos de la interfaz y del código de dominio **en español**; codificación UTF-8 (utf8mb4) de extremo a extremo.")

# ---------------------------------------------------------------- 3. diseño BD
h1("3. Diseño de la base de datos")
h2("3.1. Entidades y relaciones")
p("El dominio se modela con cuatro entidades:")
vineta("**Usuario**: socio de la biblioteca. Atributos: id, nombre, apellidos, email (único), teléfono, fecha de alta.")
vineta("**Libro**: obra del catálogo. Atributos: id, título, ISBN (único), editorial, año de publicación, ejemplares disponibles.")
vineta("**Autor**: escritor. Atributos: id, nombre, nacionalidad.")
vineta("**Préstamo**: un libro prestado a un usuario. Atributos: id, fecha de préstamo, fecha de devolución prevista, "
       "fecha de devolución (vacía mientras no se devuelve) y estado.")
p("Relaciones:")
tabla(["Relación", "Cardinalidad", "Significado"], [
    ["Usuario – realiza – Préstamo", "1 : N", "Un usuario puede tener muchos préstamos; cada préstamo es de un único usuario."],
    ["Libro – se presta en – Préstamo", "1 : N", "Un libro puede prestarse muchas veces; cada préstamo es de un único libro."],
    ["Libro – escrito por – Autor", "**N : M**", "Un libro puede tener varios autores y un autor puede haber escrito varios libros."],
], anchos=[5.2, 2.6, 8.6])
p("La relación **N:M entre Libro y Autor** (exigida por la rúbrica) se transforma en el modelo relacional en la "
  "tabla intermedia `libro_autor`, cuya clave primaria es compuesta (`libro_id`, `autor_id`) y cuyas dos columnas "
  "son claves foráneas. «Préstamo» se modela como entidad propia (y no como atributo de una relación N:M "
  "Usuario–Libro) porque tiene identidad, estado e historial: el mismo usuario puede tomar el mismo libro varias veces.")
h2("3.2. Diagrama Entidad/Relación")
figura(*DIAGRAMAS[0])
h2("3.3. Modelo relacional")
figura(*DIAGRAMAS[1])
tabla(["Tabla", "Clave primaria", "Claves foráneas", "Restricciones"], [
    ["usuarios", "id", "—", "email UNIQUE"],
    ["libros", "id", "—", "isbn UNIQUE; ejemplares_disponibles ≥ 0"],
    ["autores", "id", "—", "—"],
    ["libro_autor", "(libro_id, autor_id)", "libro_id → libros.id; autor_id → autores.id", "ON DELETE CASCADE"],
    ["prestamos", "id", "usuario_id → usuarios.id; libro_id → libros.id", "estado IN (ACTIVO, DEVUELTO, RETRASADO); fecha_devolucion NULL"],
], anchos=[2.6, 3.2, 5.6, 5])
p("Los archivos fuente editables de los diagramas están en `docs/diagramas/` (script generador, Mermaid y draw.io).")

# ---------------------------------------------------------------- 4. mockups
h1("4. Mockups de la interfaz")
p("Antes de programar las vistas se diseñaron los mockups (wireframes) de las pantallas principales. Todas comparten "
  "una **barra de navegación oscura** con la marca «Biblioteca» y los enlaces Inicio, Libros, Usuarios, Préstamos y "
  "Autores. Los listados tienen el botón azul «+ Nuevo» arriba a la derecha y, en cada fila, los botones "
  "**Editar** (amarillo) y **Eliminar** (rojo); los préstamos pendientes muestran el botón **Devolver** (verde). "
  "Los HTML de los mockups están en `docs/mockups/`.")
for rel, pie_ in MOCKUPS:
    if (DOCS / rel).exists() or rel in (m[0] for m in MOCKUPS[:4]):
        figura(rel, pie_, ancho_cm=16)

# ---------------------------------------------------------------- 5. arquitectura
h1("5. Arquitectura de la aplicación (MVC)")
p("El código se organiza en el paquete `com.serverside.appbackendp1` siguiendo el patrón MVC:")
codigo("""src/main/java/com/serverside/appbackendp1/
├── AppBackendP1Application.java   ← clase principal (@SpringBootApplication)
├── model/          ← Modelo: entidades JPA
│   ├── Usuario.java, Libro.java, Autor.java, Prestamo.java
│   └── EstadoPrestamo.java (enum ACTIVO | DEVUELTO | RETRASADO)
├── repository/     ← Acceso a datos: interfaces JpaRepository
│   └── UsuarioRepository, LibroRepository, AutorRepository, PrestamoRepository
├── service/        ← Lógica de negocio (@Service, @Transactional)
│   └── LibroService, UsuarioService, PrestamoService
└── controller/     ← Controlador: @Controller por entidad + HomeController
src/main/resources/
├── application.properties
└── templates/      ← Vista: plantillas Thymeleaf
    ├── fragments/layout.html (cabecera, navbar, mensajes)
    ├── index.html, libros/, usuarios/, prestamos/, autores/""", "Estructura de paquetes")

h2("5.1. Modelo (entidades JPA)")
p("Cada tabla se representa con una clase anotada con `@Entity` y `@Table`. Las claves primarias usan "
  "`@GeneratedValue(strategy = GenerationType.IDENTITY)` (AUTO_INCREMENT en MariaDB). Las restricciones de "
  "validación (`@NotBlank`, `@Email`, `@Min`, `@NotNull`) se declaran en los propios atributos y Spring las "
  "comprueba al recibir el formulario con `@Valid`.")
libro = leer("src/main/java/com/serverside/appbackendp1/model/Libro.java")
frag = extraer(libro, "@ManyToMany", "private List<Prestamo>")
if frag:
    codigo(frag, "Libro.java – relación N:M con Autor y 1:N con Préstamo")
prest = leer("src/main/java/com/serverside/appbackendp1/model/Prestamo.java")
frag = extraer(prest, "@ManyToOne(optional = false)", "private Libro libro;")
if frag:
    codigo(frag, "Prestamo.java – relaciones N:1 con Usuario y Libro")
p("La relación N:M se mapea con `@ManyToMany` + `@JoinTable(name = \"libro_autor\")` en el lado propietario "
  "(Libro) y `@ManyToMany(mappedBy = \"autores\")` en Autor. El estado del préstamo es un `enum` guardado "
  "como texto (`@Enumerated(EnumType.STRING)`).")

h2("5.2. Repositorios (Spring Data JPA)")
p("Los repositorios son interfaces que extienden `JpaRepository<Entidad, Long>`; Spring genera la implementación "
  "en tiempo de ejecución (CRUD completo: `findAll`, `findById`, `save`, `deleteById`…). Además se definen "
  "**consultas derivadas** a partir del nombre del método:")
rep = leer("src/main/java/com/serverside/appbackendp1/repository/PrestamoRepository.java")
frag = extraer(rep, "public interface", "}")
if frag:
    codigo(frag, "PrestamoRepository.java")

h2("5.3. Controladores")
p("Cada entidad tiene un `@Controller` que atiende las rutas de su listado y formularios. Los métodos "
  "devuelven el nombre de la plantilla Thymeleaf y pasan los datos a través del `Model`. Tras guardar o "
  "eliminar se aplica el patrón **Post/Redirect/Get** (`redirect:/libros`) con un mensaje flash "
  "(`RedirectAttributes`).")
tabla(["Método y ruta", "Acción"], [
    ["GET /", "Inicio: contadores y últimos 5 préstamos"],
    ["GET /libros", "Listado de libros"],
    ["GET/POST /libros/nuevo", "Formulario de alta y guardado (con @Valid)"],
    ["GET/POST /libros/{id}/editar", "Formulario de edición y guardado"],
    ["POST /libros/{id}/eliminar", "Baja (se impide si tiene préstamos)"],
    ["/usuarios, /usuarios/nuevo, /usuarios/{id}/editar, /usuarios/{id}/eliminar", "Gestión de usuarios (mismo esquema)"],
    ["GET /autores · GET/POST /autores/nuevo", "Listado y alta de autores"],
    ["GET /prestamos · GET /prestamos/nuevo · POST /prestamos", "Listado y alta de préstamos (descuenta un ejemplar)"],
    ["POST /prestamos/{id}/devolver", "Marca DEVUELTO, guarda la fecha y repone el ejemplar"],
], anchos=[7.6, 8.8])
controladores = sorted((REPO / "src/main/java/com/serverside/appbackendp1/controller").glob("*.java")) \
    if (REPO / "src/main/java/com/serverside/appbackendp1/controller").exists() else []
for c in controladores:
    if c.name.startswith("Prestamo"):
        frag = extraer(c.read_text(encoding="utf-8"), '@PostMapping("/{id}/devolver")', None, max_lineas=12)
        if frag:
            codigo(frag, f"{c.name} – acción Devolver")
        break

h2("5.4. Servicios (lógica de negocio)")
p("Entre controladores y repositorios hay una capa de servicios (`@Service`). Los métodos que modifican varios "
  "datos a la vez se marcan con `@Transactional`, de modo que crear un préstamo (insertar el préstamo y descontar "
  "un ejemplar) o devolverlo (cambiar el estado, guardar la fecha y reponer el ejemplar) se ejecuta de forma "
  "atómica. `PrestamoService` también recalcula el estado **RETRASADO** de los préstamos activos vencidos cada "
  "vez que se consultan los listados.")
srv = leer("src/main/java/com/serverside/appbackendp1/service/PrestamoService.java")
frag = extraer(srv, "/** Devuelve true", None, max_lineas=16)
if frag:
    codigo(frag, "PrestamoService.java – devolución de un préstamo")

h2("5.5. Vistas (Thymeleaf + Bootstrap)")
p("Las plantillas están en `src/main/resources/templates`. Los elementos comunes (cabecera `<head>`, barra de "
  "navegación y mensajes flash) se definen una sola vez en `fragments/layout.html` y se reutilizan con "
  "`th:replace`. Los formularios se enlazan al objeto del modelo con `th:object` y `th:field`, y los errores de "
  "validación se muestran con `th:errors`.")
p("El aspecto final se diseñó sobre los mockups con la idea de la **ficha catalográfica** del fichero de una "
  "biblioteca: cada listado y formulario es una «ficha» blanca con el filete rojo doble bajo la cabecera y el margen "
  "rojo vertical; los datos (signaturas, ISBN, fechas) van en tipografía mecanográfica (Courier Prime) y la interfaz "
  "en Atkinson Hyperlegible, pensada para la legibilidad. Los estados de los préstamos se muestran como sellos de "
  "tinta y la fila de un préstamo retrasado se tiñe de rojo. Cada libro muestra su **signatura topográfica** (tres "
  "letras del primer apellido del autor y tres del título, como en el tejuelo), calculada en la propia plantilla. "
  "Los estilos están en `static/css/biblioteca.css`, sobre Bootstrap 5, y cumplen WCAG 2.1 AA (contraste, foco "
  "visible, etiquetas en todos los campos, enlace «Saltar al contenido») y se adaptan a móvil.")
frag = extraer(leer("src/main/resources/templates/fragments/layout.html"), "<!-- Signatura topográfica", None, max_lineas=8)
if frag:
    codigo(frag, "fragments/layout.html – fragmento de la signatura topográfica")
layout = leer("src/main/resources/templates/fragments/layout.html")
frag = extraer(layout, '<nav th:fragment="navbar', "</nav>")
if frag:
    codigo(frag, "fragments/layout.html – barra de navegación común")

# ---------------------------------------------------------------- 6. configuración BD
h1("6. Configuración de la base de datos")
h2("6.1. application.properties")
p("La conexión se define en `src/main/resources/application.properties`. Cada valor puede sobrescribirse "
  "con una variable de entorno (sintaxis `${VARIABLE:valor_por_defecto}`), lo que permite usar `localhost` "
  "en desarrollo y el nombre del servicio `db` dentro de Docker. Como el esquema lo crea `init.sql`, Hibernate "
  "se configura con `ddl-auto=validate`: solo comprueba que las entidades coinciden con las tablas.")
props = leer("src/main/resources/application.properties")
codigo(props or "spring.datasource.url=jdbc:mariadb://localhost:3306/biblioteca\n...", "application.properties")
h2("6.2. Script de inicialización db/init.sql")
p("El script `db/init.sql` crea la base de datos `biblioteca` (utf8mb4), las cinco tablas con sus claves "
  "primarias, foráneas, restricciones UNIQUE y CHECK, e inserta datos de ejemplo (usuarios, autores, libros, "
  "relaciones libro–autor y préstamos). MariaDB lo ejecuta automáticamente la primera vez que arranca el "
  "contenedor, al montarse en `/docker-entrypoint-initdb.d/`.")
sql = leer("db/init.sql")
frag = extraer(sql, "-- Relación N:M", ") ENGINE")
if frag:
    codigo(frag, "init.sql – tabla intermedia de la relación N:M")
frag = extraer(sql, "CREATE TABLE IF NOT EXISTS prestamos", ") ENGINE")
if frag:
    codigo(frag, "init.sql – tabla prestamos")

# ---------------------------------------------------------------- 7. Docker
h1("7. Docker")
p("La aplicación se distribuye en dos contenedores orquestados con Docker Compose: **db** (MariaDB) y **app** "
  "(Spring Boot). El `Dockerfile` usa una construcción **multi-etapa**: la primera etapa compila con el JDK y "
  "Maven Wrapper y la segunda solo copia el JAR sobre una imagen JRE, más ligera.")
dockerfile = leer("Dockerfile")
if dockerfile:
    codigo(dockerfile.strip(), "Dockerfile")
compose = leer("docker-compose.yml") or leer("compose.yml") or leer("compose.yaml") or leer("docker-compose.yaml")
p("En `docker-compose.yml` el servicio `db` monta `db/init.sql` y un volumen para persistir los datos, y "
  "dispone de un *healthcheck*; el servicio `app` espera a que la base de datos esté sana (`depends_on` con "
  "`condition: service_healthy`) y recibe la URL de conexión `jdbc:mariadb://db:3306/biblioteca` por variables "
  "de entorno. El puerto 8080 se publica en el anfitrión.")
if compose:
    codigo(compose.strip(), "docker-compose.yml")
else:
    hueco("Copiar aquí docker-compose.yml cuando esté en el repositorio (regenerar la memoria con el script)")
h2("7.1. Puesta en marcha")
codigo("""# construir las imágenes y arrancar app + base de datos
docker compose up --build -d

# comprobar el estado de los contenedores
docker compose ps

# abrir la aplicación
http://localhost:8080

# parar (y borrar también los datos con -v)
docker compose down        # docker compose down -v""", "Comandos")

# ---------------------------------------------------------------- 8. trabajo realizado
h1("8. Trabajo realizado")
numerada("**Análisis y diseño**: definición de requisitos, modelo E/R en notación Chen con la relación N:M "
         "Libro–Autor y paso a modelo relacional.")
numerada("**Mockups** de las pantallas principales para fijar navegación, tablas, formularios y botones antes de programar.")
numerada("**Base de datos**: script `init.sql` con esquema, restricciones e inserción de datos de ejemplo.")
numerada("**Modelo y repositorios**: entidades JPA con sus relaciones y validaciones; repositorios Spring Data con consultas derivadas.")
numerada("**Controladores y vistas**: CRUD completo de libros y usuarios; listado y alta de autores; listado, alta y devolución de préstamos; "
         "página de inicio con estadísticas; layout común con Bootstrap 5.")
numerada("**Reglas de negocio**: control de ejemplares disponibles al prestar/devolver y bloqueo del borrado de "
         "registros con préstamos asociados.")
numerada("**Pruebas**: 12 tests automáticos con JUnit 5 sobre H2 en modo MariaDB (repositorios con `@DataJpaTest` y controladores con MockMvc).")
numerada("**Diseño de la interfaz**: hoja de estilos propia con el estilo de ficha catalográfica, sellos de estado, signatura topográfica, accesibilidad WCAG 2.1 AA y adaptación a móvil.")
numerada("**Contenerización**: Dockerfile multi-etapa y `docker-compose.yml` con MariaDB, volumen y healthcheck.")
numerada("**Documentación**: esta memoria, diagramas, mockups y vídeo demostrativo.")

h2("8.1. Estado final por entidad")
tabla(["Entidad", "Funcionalidad implementada"], [
    ["Libros", "CRUD completo: listado, alta, edición y borrado; selección múltiple de autores; ISBN único validado; borrado bloqueado si tiene préstamos."],
    ["Usuarios", "CRUD completo: listado, alta, edición y borrado; email único validado; borrado bloqueado si tiene préstamos."],
    ["Préstamos", "Listado, alta (descuenta un ejemplar; no permite prestar sin ejemplares) y devolución con el botón «Marcar devuelto» (repone el ejemplar). El estado RETRASADO se calcula al consultar."],
    ["Autores", "Listado (con número de libros de cada autor) y alta."],
    ["Inicio", "Contadores de libros, usuarios, autores y préstamos activos (indicando cuántos van con retraso) y tabla de los 5 últimos préstamos."],
], anchos=[2.8, 13.6])

h2("8.2. Pruebas automatizadas")
p("`./mvnw test` ejecuta 12 pruebas sobre una base de datos H2 en memoria (perfil `test`, modo de compatibilidad MariaDB):")
tabla(["Clase", "Pruebas"], [
    ["LibroRepositoryTest (3)", "Guardar un libro con dos autores y recuperarlo con ellos (N:M); existsByIsbn; findAllByOrderByTituloAsc."],
    ["PrestamoRepositoryTest (4)", "Crear usuario, libro y préstamo y contar por estado; existsByLibroId; existsByUsuarioId; findTop5 de los últimos préstamos."],
    ["BibliotecaControllerTest (4)", "Las páginas principales responden 200; crear un libro válido redirige y lo guarda; crear un libro sin título muestra errores; eliminar un libro con préstamos muestra un error y no lo borra."],
    ["AppBackendP1ApplicationTests (1)", "El contexto de Spring arranca."],
], anchos=[5, 11.4])

h2("8.3. Capturas de la aplicación en funcionamiento")
p("Capturas de la aplicación real ejecutándose con `docker compose up` en http://localhost:8080. La interfaz final "
  "mantiene la estructura de los mockups (barra oscura, listados con «+ Nuevo» azul, Editar amarillo, Eliminar rojo, "
  "devolución en verde) con el diseño de «ficha catalográfica» descrito en el apartado 5.5. Diferencias respecto a "
  "los mockups: el botón de devolución se rotula «Marcar devuelto», los autores de un libro se marcan con casillas en "
  "lugar de una lista con Ctrl+clic, el panel de inicio permite devolver directamente y muestra el inventario de la "
  "colección, y los libros agotados no se pueden elegir al crear un préstamo.")
for rel, pie_ in CAPTURAS:
    figura(rel, pie_, ancho_cm=16)

h2("8.4. Vídeo demostrativo")
if VIDEO_URL:
    p(f"El vídeo con la demostración de la aplicación está disponible en: {VIDEO_URL}")
else:
    hueco("Enlace al vídeo de YouTube: https://youtu.be/________ (añadir en VIDEO_URL del script o directamente aquí)")
p("Guion del vídeo: arranque con `docker compose up`, recorrido por el menú, alta/edición/borrado de un libro "
  "asignando varios autores, alta de un usuario, creación de un préstamo y su devolución, y comprobación de los "
  "datos en MariaDB.", cursiva=True)

# ---------------------------------------------------------------- 9. dificultades
h1("9. Dificultades encontradas")
vineta("**Mapeo del enum de estado**: Hibernate, con MariaDB, genera por defecto una columna `ENUM` nativa, que no "
       "coincidía con la columna `VARCHAR(20)` + `CHECK` del script SQL y hacía fallar la validación del esquema "
       "(`ddl-auto=validate`). Se resolvió forzando el tipo con `@JdbcTypeCode(SqlTypes.VARCHAR)`.")
vineta("**Relación N:M en formularios**: enlazar la selección múltiple de autores con un `Set<Autor>` requiere que Spring "
       "convierta los identificadores recibidos en entidades; se resolvió recibiendo los ids con "
       "`@RequestParam List<Long> autorIds` y cargándolos con `autorRepository.findAllById`.")
vineta("**Orden de arranque en Docker**: la aplicación arrancaba antes de que MariaDB aceptara conexiones. Se añadió "
       "un *healthcheck* al servicio `db` y `depends_on: condition: service_healthy` en `app`.")
vineta("**Codificación de caracteres**: para que tildes y eñes se guarden y muestren bien se usó `utf8mb4` en la "
       "base de datos y `SET NAMES utf8mb4` en el script de inicialización.")
vineta("**Integridad al borrar**: eliminar un libro o usuario con préstamos provocaba un error de clave foránea; "
       "se comprueba antes con `existsByLibroId`/`existsByUsuarioId` y se muestra un mensaje en lugar del error.")

# ---------------------------------------------------------------- 10. no realizado
h1("10. Puntos no realizados")
vineta("**Autenticación y roles** (bibliotecario/socio): no se ha implementado Spring Security; cualquier persona con acceso a la URL puede gestionar los datos.")
vineta("**Tarea programada para RETRASADO**: el estado se recalcula al consultar los préstamos, no mediante una tarea `@Scheduled` ni con avisos al usuario.")
vineta("**Edición y borrado de autores**: de los autores solo se implementó el listado y el alta.")
vineta("**Edición y borrado de préstamos**: un préstamo se crea y se devuelve, pero no se puede modificar ni eliminar desde la interfaz.")
vineta("**Búsqueda, filtros y paginación** en los listados.")
vineta("**Pruebas contra MariaDB real**: los 12 tests usan H2 en memoria; no hay pruebas de integración con MariaDB ni pruebas de la interfaz en navegador.")

# ---------------------------------------------------------------- 11. mejoras
h1("11. Propuestas de mejora")
vineta("Añadir **Spring Security** con inicio de sesión y roles.")
vineta("Tarea `@Scheduled` diaria que marque como RETRASADO los préstamos vencidos y envíe un aviso por email al usuario.")
vineta("**Paginación y búsqueda** con `Pageable` de Spring Data (por título, ISBN, autor o usuario).")
vineta("**API REST** (`@RestController`) para un futuro cliente móvil o SPA.")
vineta("**Migraciones** de esquema con Flyway en lugar del script `init.sql`.")
vineta("Completar el CRUD de **autores** (editar y eliminar) y permitir corregir o anular préstamos.")
vineta("Pruebas de integración con **Testcontainers** (MariaDB real) además de los tests actuales sobre H2.")
vineta("Gestión de **ejemplares** individuales (código de barras por copia) y reservas.")

# ---------------------------------------------------------------- 12. autoevaluación
h1("12. Autoevaluación")
p("Valoración según los cinco criterios de la rúbrica oficial (5 puntos cada uno). Para cada uno se indica lo que "
  "exige el nivel máximo y la evidencia de este proyecto que lo cumple:")
tabla(["Criterio (nivel máximo exigido)", "Evidencia en el proyecto", "Puntos"], [
    ["**1. Diagrama E/R** – al menos 3 entidades con todos sus atributos (mín. 2 por entidad) y relaciones, siendo una N a M.",
     "4 entidades (Usuario, Libro, Autor, Préstamo) con todos sus atributos: 6, 6, 3 y 5 respectivamente, PK subrayada. "
     "Relaciones Usuario 1:N Préstamo, Libro 1:N Préstamo y **Libro N:M Autor**, con cardinalidades (apartado 3.2). "
     "Se añade el modelo relacional con la tabla intermedia libro_autor (3.3).", "5 / 5"],
    ["**2. Mockup de la aplicación** – al menos 2 interfaces detalladas que presenten al menos las 3 entidades, más el menú y los botones de navegación.",
     "8 mockups detallados (apartado 4): inicio, listado y formulario de libros, listado y formulario de préstamos, "
     "listado y formulario de usuarios y listado de autores. Aparecen las 4 entidades, la barra de navegación "
     "(Inicio, Libros, Usuarios, Préstamos, Autores) y los botones Nuevo, Editar, Eliminar, Devolver, Guardar y Cancelar.", "5 / 5"],
    ["**3. Modelos mediante Spring Data** – al menos 3 modelos y sus relaciones.",
     "4 entidades JPA (Usuario, Libro, Autor, Prestamo) y el enum EstadoPrestamo. Relaciones @ManyToMany/@JoinTable "
     "(Libro–Autor), @OneToMany/@ManyToOne (Usuario–Préstamo y Libro–Préstamo) y 4 repositorios JpaRepository con "
     "consultas derivadas. Los tests de repositorio verifican la relación N:M (apartados 5.1, 5.2 y 8.2).", "5 / 5"],
    ["**4. CRUD mediante Spring** – 1 CRUD completo con controladores y vistas, más listados del resto de modelos.",
     "**Dos** CRUD completos (Libros y Usuarios: listar, crear, editar y eliminar) con controlador, servicio y vistas "
     "Thymeleaf, validación y mensajes. Del resto de modelos hay listados y algo más: Préstamos (listar, crear y "
     "devolver) y Autores (listar y crear). Panel de inicio con contadores (apartados 5.3, 8.1 y 8.3).", "5 / 5"],
    ["**5. Modificaciones del contenedor Docker** – nuevas librerías y binarios para que el proyecto se ejecute y funcione correctamente.",
     "Librerías nuevas en pom.xml (Spring Data JPA, Thymeleaf, Validation, driver mariadb-java-client) que el Dockerfile "
     "descarga en la etapa de compilación (dependency:go-offline). Dockerfile multi-etapa: JDK 25 para compilar y JRE 25 "
     "para ejecutar. docker-compose.yml añade el servidor MariaDB 11 con init.sql, volumen, healthcheck y variables de "
     "entorno. Se ha comprobado que funciona: contenedores en marcha y todas las rutas responden HTTP 200 (apartado 7 y figura 16).", "5 / 5"],
    ["**Total**", "", "**25 / 25**"],
], anchos=[5.4, 8.8, 2.2])
p("Se cumple el nivel máximo de los cinco criterios, en varios casos por encima del mínimo: 4 entidades en lugar de 3, "
  "8 mockups en lugar de 2 y dos CRUD completos en lugar de uno. Lo que no se ha hecho (apartado 10: edición y "
  "borrado de autores y préstamos, autenticación, paginación) va más allá de lo que pide la rúbrica, así que no resta "
  "puntuación.", cursiva=True)

# ---------------------------------------------------------------- 13. webgrafía
h1("13. Webgrafía")
fuentes = [
    ("Spring Boot – Reference Documentation", "https://docs.spring.io/spring-boot/index.html"),
    ("Spring Framework – Web MVC", "https://docs.spring.io/spring-framework/reference/web/webmvc.html"),
    ("Spring Data JPA – Reference Documentation", "https://docs.spring.io/spring-data/jpa/reference/"),
    ("Spring Guides – Accessing Data with JPA", "https://spring.io/guides/gs/accessing-data-jpa"),
    ("Spring Guides – Validating Form Input", "https://spring.io/guides/gs/validating-form-input"),
    ("Hibernate ORM – User Guide", "https://docs.jboss.org/hibernate/orm/current/userguide/html_single/Hibernate_User_Guide.html"),
    ("Jakarta Bean Validation", "https://beanvalidation.org/"),
    ("Thymeleaf – Tutorial: Thymeleaf + Spring", "https://www.thymeleaf.org/doc/tutorials/3.1/thymeleafspring.html"),
    ("MariaDB – Documentación (Knowledge Base)", "https://mariadb.com/kb/en/documentation/"),
    ("MariaDB Connector/J", "https://mariadb.com/kb/en/about-mariadb-connector-j/"),
    ("Imagen oficial de MariaDB en Docker Hub", "https://hub.docker.com/_/mariadb"),
    ("Docker – Documentación", "https://docs.docker.com/"),
    ("Docker Compose – Referencia del fichero", "https://docs.docker.com/reference/compose-file/"),
    ("Bootstrap 5 – Documentación", "https://getbootstrap.com/docs/5.3/getting-started/introduction/"),
    ("Bootstrap Icons", "https://icons.getbootstrap.com/"),
    ("W3C – Pautas de Accesibilidad para el Contenido Web (WCAG) 2.1", "https://www.w3.org/TR/WCAG21/"),
]
for nombre, url in fuentes:
    par = doc.add_paragraph(style="List Bullet")
    par.add_run(nombre + ". ")
    r = par.add_run(url)
    r.font.color.rgb = RGBColor(0x1F, 0x5F, 0xBF)
    r.underline = True

# Word actualiza el índice (campo TOC) al abrir el documento
upd = OxmlElement("w:updateFields")
upd.set(qn("w:val"), "true")
doc.settings.element.append(upd)

doc.save(SALIDA)
print("Generado:", SALIDA)
