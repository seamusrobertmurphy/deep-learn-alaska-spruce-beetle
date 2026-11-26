"""Fits every figure of a rendered Word file inside the text width, so that none is cut at the right margin.

Run on the rendered file after forestry-layout.py (the manuscript) or supplement-labels.py (the supplement),
and before table-format.py:
  python3 ../05.scripts/fit-figures.py manuscript-2026-11-24.docx

Quarto puts each figure in a one-cell table as wide as the text, 6.30 inches on this template, and draws the
picture at its fig-width, 6.30 inches. The cell keeps 0.075 inches of margin a side and the picture's paragraph
inherits the body text's indent, so the picture ran past the right margin and Figure 2 lost its last column
(Seamus, 2026-11-25). Each picture is scaled to at most 6.0 inches wide, keeping its shape, and its paragraph
loses its indent. The image file inside the Word file is not changed, so the separate TIFF files keep 500 dpi.
"""
import os, shutil, sys, tempfile, zipfile
from lxml import etree

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
WP = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
q = lambda tag: f"{{{W}}}{tag}"
MAX = int(6.0 * 914400)  # the widest a picture may be, in English Metric Units

path = sys.argv[1]
with zipfile.ZipFile(path) as z:
    names = z.namelist(); data = {n: z.read(n) for n in names}
root = etree.fromstring(data["word/document.xml"])
scaled = 0
for p in root.iter(q("p")):
    if p.find(f".//{q('drawing')}") is None: continue
    ppr = p.find(q("pPr"))
    if ppr is None:
        ppr = etree.SubElement(p, q("pPr")); p.insert(0, ppr)
    for old in ppr.findall(q("ind")): ppr.remove(old)
    ind = etree.SubElement(ppr, q("ind")); ind.set(q("left"), "0"); ind.set(q("right"), "0"); ind.set(q("firstLine"), "0")
    jc = ppr.find(q("jc"))
    if jc is not None: ppr.remove(jc); ppr.append(jc)  # w:jc follows w:ind in the schema's order
    for ext in p.iter(f"{{{WP}}}extent"):
        cx, cy = int(ext.get("cx")), int(ext.get("cy"))
        if cx <= MAX: continue
        k = MAX / cx; ext.set("cx", str(MAX)); ext.set("cy", str(round(cy * k))); scaled += 1
        for e in ext.getparent().iter(f"{{{A}}}ext"):  # the picture's own size inside the drawing
            if e.get("cx") == str(cx): e.set("cx", str(MAX)); e.set("cy", str(round(cy * k)))
data["word/document.xml"] = etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)
fd, tmp = tempfile.mkstemp(suffix=".docx", dir=os.path.dirname(os.path.abspath(path))); os.close(fd)
with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as z:
    for n in names: z.writestr(n, data[n])
shutil.move(tmp, path)
print(f"{path}: {scaled} figures scaled to 6.0 inches wide, none indented")
