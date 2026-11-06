import os
import os
OUT=os.path.dirname(os.path.abspath(__file__))
CSS="""*{box-sizing:border-box}
body{margin:0;width:1280px;font-family:"Helvetica Neue",Arial,"Liberation Sans",sans-serif;font-size:16px;color:#212529;background:#f1f3f5;line-height:1.5;position:relative}
.tag{position:absolute;top:62px;right:12px;font-size:11px;color:#868e96;background:#fff;border:1px dashed #adb5bd;padding:1px 8px;border-radius:3px;z-index:5}
.navbar{background:#212529;height:56px;display:flex;align-items:center;padding:0 24px}
.brand{color:#fff;font-size:20px;margin-right:32px}
.navbar a{color:#adb5bd;text-decoration:none;margin-right:20px;font-size:16px}
.navbar a.active{color:#fff;font-weight:bold;border-bottom:2px solid #fff;padding-bottom:2px}
.container{padding:28px 48px 40px}
h1{font-size:32px;font-weight:500;margin:0 0 16px}
h2{font-size:24px;font-weight:500;margin:28px 0 12px}
.head{display:flex;justify-content:space-between;align-items:center;margin-bottom:16px}
.head h1{margin:0}
.btn{display:inline-block;padding:6px 14px;border-radius:5px;border:1px solid;font-size:16px;color:#fff;text-decoration:none;line-height:1.5;cursor:pointer}
.btn-sm{padding:2px 9px;font-size:14px}
.btn-primary{background:#0d6efd;border-color:#0d6efd}
.btn-secondary{background:#6c757d;border-color:#6c757d}
.btn-warning{background:#ffc107;border-color:#ffc107;color:#000}
.btn-danger{background:#dc3545;border-color:#dc3545}
.btn-success{background:#198754;border-color:#198754}
.cards{display:flex;gap:24px}
.card{background:#fff;border:1px solid #ced4da;border-radius:6px;padding:20px 24px;flex:1}
.card .lbl{color:#6c757d;font-size:14px;text-transform:uppercase;letter-spacing:.05em}
.card .num{font-size:44px;font-weight:600;color:#495057;line-height:1.2}
table{width:100%;border-collapse:collapse;background:#fff;border:1px solid #ced4da}
th,td{text-align:left;padding:9px 12px;border-bottom:1px solid #dee2e6;font-size:15px}
thead th{background:#e9ecef;border-bottom:2px solid #adb5bd}
tbody tr:nth-child(even){background:#f8f9fa}
td.act{white-space:nowrap}
.badge{display:inline-block;font-size:12px;font-weight:bold;padding:3px 9px;border-radius:4px;color:#fff}
.b-act{background:#0d6efd}.b-dev{background:#198754}.b-ret{background:#dc3545}
.form{background:#fff;border:1px solid #ced4da;border-radius:6px;padding:28px 32px;max-width:720px}
.field{margin-bottom:18px}
label{display:block;font-weight:500;margin-bottom:4px}
.input{display:block;width:100%;border:1px solid #adb5bd;border-radius:4px;background:#fff;padding:6px 12px;min-height:38px;color:#495057}
.input.ph{color:#868e96}
.input.invalid{border-color:#dc3545}
.err{color:#dc3545;font-size:14px;margin-top:4px}
.hint{color:#6c757d;font-size:14px;margin-top:4px}
.sel{position:relative;padding-right:30px}
.sel:after{content:"\\25BE";position:absolute;right:12px;top:6px;color:#495057}
.multi{border:1px solid #adb5bd;border-radius:4px;background:#fff;padding:2px 0}
.multi div{padding:3px 12px}
.multi .on{background:#0d6efd;color:#fff}
.row2{display:flex;gap:20px}.row2 .field{flex:1}
.actions{display:flex;gap:10px;margin-top:8px}
.route{color:#6c757d;font-size:13px;margin:-8px 0 14px}
"""
NAV=[("Inicio","/","01-dashboard"),("Libros","/libros","02-libros-listado"),("Usuarios","/usuarios","06-usuarios-listado"),("Préstamos","/prestamos","04-prestamos-listado"),("Autores","/autores","08-autores-listado")]
def page(fn,title,active,route,body):
    nav="".join(f'<a href="{f}.html"{" class=active" if n==active else ""}>{n}</a>' for n,_,f in NAV)
    h=f'<!DOCTYPE html><html lang="es"><head><meta charset="utf-8"><title>Mockup – {title}</title><link rel="stylesheet" href="wireframe.css"></head><body><div class="navbar"><span class="brand">Biblioteca</span>{nav}</div><div class="tag">Mockup – {title}</div><div class="container"><div class="route">Ruta: {route}</div>{body}</div></body></html>'
    open(f"{OUT}/{fn}.html","w").write(h)
open(f"{OUT}/wireframe.css","w").write(CSS)
def badge(e):
    c={"ACTIVO":"b-act","DEVUELTO":"b-dev","RETRASADO":"b-ret"}[e];return f'<span class="badge {c}">{e}</span>'
def table(heads,rows):
    return "<table><thead><tr>"+"".join(f"<th>{h}</th>" for h in heads)+"</tr></thead><tbody>"+"".join("<tr>"+"".join(f'<td{" class=act" if str(c).startswith("<a") else ""}>{c}</td>' for c in r)+"</tr>" for r in rows)+"</tbody></table>"
EE='<a class="btn btn-sm btn-warning">Editar</a> <a class="btn btn-sm btn-danger">Eliminar</a>'
def head(t,b): return f'<div class="head"><h1>{t}</h1><a class="btn btn-primary">{b}</a></div>'
def field(l,v,ph=False,sel=False,err=None):
    c="input"+(" ph" if ph else "")+(" sel" if sel else "")+(" invalid" if err else "")
    return f'<div class="field"><label>{l}</label><div class="{c}">{v or "&nbsp;"}</div>'+(f'<div class="err">{err}</div>' if err else "")+'</div>'
def btns(): return '<div class="actions"><a class="btn btn-primary">Guardar</a><a class="btn btn-secondary">Cancelar</a></div>'

P=[("Ana","García López"),("Carlos","Martínez Ruiz"),("Lucía","Fernández Soto"),("Javier","Sánchez Mora"),("Marta","Gómez Prieto"),("Pablo","Navarro Díaz")]
L=["Cien años de soledad","Don Quijote de la Mancha","La sombra del viento","Rimas y leyendas","El amor en los tiempos del cólera","La casa de los espíritus"]
# 01
pr=[(f"{P[0][0]} {P[0][1]}",L[0],"02/09/2026","16/09/2026","ACTIVO"),
(f"{P[1][0]} {P[1][1]}",L[2],"28/08/2026","11/09/2026","RETRASADO"),
(f"{P[2][0]} {P[2][1]}",L[1],"20/08/2026","03/09/2026","DEVUELTO"),
(f"{P[3][0]} {P[3][1]}",L[4],"15/08/2026","29/08/2026","RETRASADO"),
(f"{P[4][0]} {P[4][1]}",L[5],"10/08/2026","24/08/2026","DEVUELTO")]
body='<h1>Inicio</h1><div class="cards"><div class="card"><div class="lbl">Libros</div><div class="num">248</div></div><div class="card"><div class="lbl">Usuarios</div><div class="num">112</div></div><div class="card"><div class="lbl">Préstamos activos</div><div class="num">17</div></div></div><h2>Últimos préstamos</h2>'
body+=table(["Usuario","Libro","Fecha préstamo","Devolución prevista","Estado"],[r[:4]+(badge(r[4]),) for r in pr])
page("01-dashboard","Dashboard","Inicio","/",body)
# 02
libs=[(L[0],"978-84-376-0494-7","Debolsillo",1967,"Gabriel García Márquez",3),
(L[1],"978-84-206-5026-7","Alianza Editorial",1605,"Miguel de Cervantes",5),
(L[2],"978-84-08-17208-3","Planeta",2001,"Carlos Ruiz Zafón",2),
(L[3],"978-84-376-0987-4","Cátedra",1871,"Gustavo Adolfo Bécquer",1),
(L[4],"978-84-397-1230-5","Mondadori",1985,"Gabriel García Márquez",0),
(L[5],"978-84-01-02921-6","Plaza &amp; Janés",1982,"Isabel Allende",4)]
body=head("Libros","+ Nuevo libro")+table(["Título","ISBN","Editorial","Año","Autores","Ejemplares disp.","Acciones"],[l+(EE,) for l in libs])
page("02-libros-listado","Listado de libros","Libros","/libros",body)
# 03
authors=["Gabriel García Márquez","Isabel Allende","Miguel de Cervantes","Carlos Ruiz Zafón","Gustavo Adolfo Bécquer"]
ms='<div class="multi">'+"".join(f'<div{" class=on" if i in(0,1) else ""}>{a}</div>' for i,a in enumerate(authors))+'</div>'
body='<h1>Nuevo libro</h1><div class="form">'+field("Título","Cien años de soledad")+field("ISBN","978-84",err="El ISBN debe tener 13 dígitos")+'<div class="row2">'+field("Editorial","Debolsillo")+field("Año de publicación","1967")+'</div>'+field("Ejemplares disponibles","3")+f'<div class="field"><label>Autores</label>{ms}<div class="hint">Ctrl+clic para seleccionar varios</div></div>'+btns()+'</div>'
page("03-libro-formulario","Formulario de libro","Libros","/libros/nuevo  y  /libros/{id}/editar",body)
# 04
pl=[(f"{P[0][0]} {P[0][1]}",L[0],"02/09/2026","16/09/2026","—","ACTIVO"),
(f"{P[1][0]} {P[1][1]}",L[2],"28/08/2026","11/09/2026","—","RETRASADO"),
(f"{P[2][0]} {P[2][1]}",L[1],"20/08/2026","03/09/2026","01/09/2026","DEVUELTO"),
(f"{P[3][0]} {P[3][1]}",L[4],"15/08/2026","29/08/2026","—","RETRASADO"),
(f"{P[4][0]} {P[4][1]}",L[5],"10/08/2026","24/08/2026","22/08/2026","DEVUELTO"),
(f"{P[5][0]} {P[5][1]}",L[3],"05/10/2026","19/10/2026","—","ACTIVO")]
D='<a class="btn btn-sm btn-success">Devolver</a>'
body=head("Préstamos","+ Nuevo préstamo")+table(["Usuario","Libro","Fecha préstamo","Devolución prevista","Fecha devolución","Estado","Acciones"],[r[:5]+(badge(r[5]),D if r[5]!="DEVUELTO" else "") for r in pl])
page("04-prestamos-listado","Listado de préstamos","Préstamos","/prestamos",body)
# 05
body='<h1>Nuevo préstamo</h1><div class="form">'+field("Usuario","Ana García López (ana.garcia@example.com)",sel=True)+field("Libro","Cien años de soledad — 3 ejemplares disponibles",sel=True)+'<div class="row2">'+field("Fecha préstamo","06/10/2026")+field("Fecha devolución prevista","20/10/2026")+'</div>'+btns()+'</div>'
page("05-prestamo-formulario","Formulario de préstamo","Préstamos","/prestamos/nuevo",body)
# 06
us=[(n,a,f"{n.lower()}.{a.split()[0].lower().replace('í','i').replace('á','a').replace('ó','o').replace('é','e')}@example.com",f"6{12+i}  345 {600+i*7}",f"{10+i*3:02d}/0{1+i}/2025") for i,(n,a) in enumerate(P)]
us[2]=("Lucía","Fernández Soto","lucia.fernandez@example.com","612 345 614","16/03/2025")
body=head("Usuarios","+ Nuevo usuario")+table(["Nombre","Apellidos","Email","Teléfono","Fecha alta","Acciones"],[u+(EE,) for u in us])
page("06-usuarios-listado","Listado de usuarios","Usuarios","/usuarios",body)
# 07
body='<h1>Nuevo usuario</h1><div class="form">'+'<div class="row2">'+field("Nombre","Ana")+field("Apellidos","García López")+'</div>'+field("Email","ana.garcia@example.com")+field("Teléfono","612 345 678")+field("Fecha de alta","06/10/2026")+btns()+'</div>'
page("07-usuario-formulario","Formulario de usuario","Usuarios","/usuarios/nuevo",body)
# 08
au=[("Gabriel García Márquez","Colombia",2),("Isabel Allende","Chile",1),("Miguel de Cervantes","España",1),("Carlos Ruiz Zafón","España",1),("Gustavo Adolfo Bécquer","España",1),("Julio Cortázar","Argentina",0)]
body=head("Autores","+ Nuevo autor")+table(["Nombre","Nacionalidad","Nº libros","Acciones"],[a+(EE,) for a in au])
page("08-autores-listado","Listado de autores","Autores","/autores",body)
# index
items=[("01-dashboard","Dashboard","/"),("02-libros-listado","Listado de libros","/libros"),("03-libro-formulario","Formulario de libro","/libros/nuevo, /libros/{id}/editar"),("04-prestamos-listado","Listado de préstamos","/prestamos"),("05-prestamo-formulario","Formulario de préstamo","/prestamos/nuevo"),("06-usuarios-listado","Listado de usuarios","/usuarios"),("07-usuario-formulario","Formulario de usuario","/usuarios/nuevo"),("08-autores-listado","Listado de autores","/autores")]
body='<h1>Mockups – Biblioteca</h1><table><thead><tr><th>Pantalla</th><th>Ruta</th><th>HTML</th><th>PNG</th></tr></thead><tbody>'+"".join(f'<tr><td>{n}</td><td>{r}</td><td><a href="{f}.html">{f}.html</a></td><td><a href="png/{f}.png">png/{f}.png</a></td></tr>' for f,n,r in items)+'</tbody></table>'
page("index","Índice","","—",body)
