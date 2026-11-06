#!/usr/bin/env python3
"""Exporta la memoria DOCX a PDF con LibreOffice, actualizando antes el índice.

Uso (python del sistema, que trae el módulo uno):  python3 docs/memoria/exportar_pdf.py
"""
import subprocess
import time
from pathlib import Path

import uno
from com.sun.star.beans import PropertyValue

DOCX = Path(__file__).resolve().parent / "producto2(FP065)_ValeroSanz_Andrea.docx"
PDF = DOCX.with_suffix(".pdf")


def prop(nombre, valor):
    p = PropertyValue()
    p.Name, p.Value = nombre, valor
    return p


proc = subprocess.Popen(["soffice", "--headless", "--invisible", "--norestore",
                         "-env:UserInstallation=file:///tmp/lo_memoria",
                         "--accept=socket,host=127.0.0.1,port=2099;urp;"])
try:
    resolver = uno.getComponentContext().ServiceManager.createInstanceWithContext(
        "com.sun.star.bridge.UnoUrlResolver", uno.getComponentContext())
    for _ in range(60):
        try:
            ctx = resolver.resolve("uno:socket,host=127.0.0.1,port=2099;urp;StarOffice.ComponentContext")
            break
        except Exception:
            time.sleep(0.5)
    desktop = ctx.ServiceManager.createInstanceWithContext("com.sun.star.frame.Desktop", ctx)
    doc = desktop.loadComponentFromURL(DOCX.as_uri(), "_blank", 0, (prop("Hidden", True),))
    doc.refresh()
    idx = doc.getDocumentIndexes()
    if idx.getCount() == 0:
        # LibreOffice no convierte el campo TOC vacío en índice: se inserta uno nativo
        # en el lugar de la nota «(Si el índice aparece vacío…)».
        busq = doc.createSearchDescriptor()
        busq.SearchString = "(Si el índice aparece vacío"
        nota = doc.findFirst(busq)
        if nota is not None:
            cursor = nota.getText().createTextCursorByRange(nota.getStart())
            cursor.gotoEndOfParagraph(True)
            cursor.setString("")
            indice = doc.createInstance("com.sun.star.text.ContentIndex")
            indice.Title = ""
            indice.CreateFromOutline = True
            indice.Level = 2
            nota.getText().insertTextContent(cursor, indice, False)
    for i in range(idx.getCount()):
        idx.getByIndex(i).update()
    doc.storeToURL(PDF.as_uri(), (prop("FilterName", "writer_pdf_Export"),))
    doc.close(True)
    print("Generado:", PDF)
finally:
    try:
        desktop.terminate()
    except Exception:
        pass
    proc.wait(timeout=20)
