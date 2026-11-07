"""Builds README.md from the laid-out manuscript and supplement, so that the README's title, abstract, figures, tables
and supplementary material are the rendered manuscript's and cannot drift from it. Nothing else goes into the README.

  cd 01.manuscript && python3 ../05.scripts/readme-from-docx.py manuscript-jars-YYYY-MM-DD.docx supplementary-YYYY-MM-DD.docx ../README.md

Each figure image is copied out of the Word file to 03.outputs/figures/figure<n>.png or figureS<n>.png and shown at
full width with its caption below. Tables become GitHub pipe tables with the caption above, and asterisks and pipes in
cell text are escaped so GitHub does not read them as markup. The equation grids are not tables and are left out.
GitHub sizes a table to its content and ignores width attributes, so no width is set on a table.
"""
import html, os, re, sys, zipfile

def esc(s):
    return s.replace("\\", "\\\\").replace("*", "\\*").replace("|", "\\|").replace("<", "&lt;")

def ptext(p):
    """Paragraph text with italic runs as *text*, markup characters escaped."""
    out, ital = [], None
    for r in re.findall(r"<w:r[ >].*?</w:r>", p, re.S):
        t = "".join(html.unescape(s) for s in re.findall(r"<w:t[^>]*>([^<]*)</w:t>", r))
        if not t: continue
        i = re.search(r'<w:i(?:\s+w:val="(?:true|1|on)")?\s*/>', r) is not None  # an explicit w:val="false" is not italic
        if i != ital and out and ital: out.append("*")
        if i and i != ital: out.append("*")
        out.append(esc(t)); ital = i
    if ital: out.append("*")
    s = "".join(out)
    return re.sub(r"\*(\s+)\*", r"\1", s).strip()

def style(p):
    m = re.search(r'<w:pStyle w:val="([^"]*)"', p); return m.group(1) if m else ""

def label(cap):
    return re.sub(r"^(Table|Figure)\s+(S?\d+)(\.?)", r"**\1 \2\3**", cap)

def parse(path):
    """The file's paragraphs, tables and images in reading order."""
    z = zipfile.ZipFile(path)
    rels = {}
    for r in re.findall(r"<Relationship\b[^>]*>", z.read("word/_rels/document.xml.rels").decode("utf8")):
        i, t = re.search(r'\bId="([^"]+)"', r), re.search(r'\bTarget="([^"]+)"', r)
        if i and t: rels[i.group(1)] = t.group(1)
    body = z.read("word/document.xml").decode("utf8").split("<w:body>")[1]
    items = []
    for b in re.findall(r"<w:tbl\b[^>]*>.*?</w:tbl>|<w:p[ >].*?</w:p>", body, re.S):
        if b.startswith("<w:tbl"):
            assert not re.search(r"<w:tbl\b", b[1:]), f"{path}: a table inside a table; run jars-layout.py on the file first"
            if "<m:oMath" in b: continue  # an equation grid
            rows = [["<br>".join(t for t in (ptext(p) for p in re.findall(r"<w:p[ >].*?</w:p>", tc, re.S)) if t)
                     for tc in re.findall(r"<w:tc[ >].*?</w:tc>", tr, re.S)]
                    for tr in re.findall(r"<w:tr[ >].*?</w:tr>", b, re.S)]
            items.append(("table", rows))
        elif "<w:drawing>" in b:
            items.append(("image", [z.read("word/" + rels[i]) for i in re.findall(r'r:embed="([^"]+)"', b)]))
        else:
            items.append(("p", style(b), ptext(b)))
    return items

def figures_and_tables(items, path):
    figs, tabs, cap = [], [], None
    for k, o in enumerate(items):
        if o[0] == "p" and o[1] == "ImageCaption" and o[2].startswith("Table"):
            cap = o[2]
        elif o[0] == "table":
            assert cap, f"{path}: a table with no caption above it"
            tabs.append((cap, o[1])); cap = None
        elif o[0] == "image":
            nxt = next((p for p in items[k + 1:] if p[0] != "p" or p[2]), None)
            assert nxt and nxt[0] == "p" and nxt[1] == "ImageCaption" and nxt[2].startswith("Figure"), f"{path}: a figure with no caption below it"
            assert len(o[1]) == 1 and o[1][0][:4] == b"\x89PNG", f"{path}: a figure that is not one PNG image"
            figs.append((nxt[2], o[1][0]))
    return figs, tabs

def gfm_table(rows):
    n = max(len(r) for r in rows)
    rows = [r + [""] * (n - len(r)) for r in rows]
    head = "| " + " | ".join(rows[0]) + " |"
    sep = "|" + "|".join(["---"] * n) + "|"
    return "\n".join([head, sep] + ["| " + " | ".join(r) + " |" for r in rows[1:]])

main, supp, dst = sys.argv[1:4]
m, s = parse(main), parse(supp)
title = next(o[2] for o in m if o[0] == "p" and o[1] == "Title")
abstract = " ".join(o[2] for o in m if o[0] == "p" and o[1] == "Abstract" and o[2])
assert abstract, f"{main}: no paragraph in the Abstract style"
figs, tabs = figures_and_tables(m, main)
sfigs, stabs = figures_and_tables(s, supp)
supp_text = [o[2] for o in s if o[0] == "p" and o[1] in ("BodyText", "FirstParagraph") and o[2] and not o[2].startswith("Alt text")]

fig_dir = os.path.join(os.path.dirname(os.path.abspath(dst)), "03.outputs", "figures")
def show(name, cap, png):
    open(os.path.join(fig_dir, name + ".png"), "wb").write(png)
    return [f'<img src="03.outputs/figures/{name}.png" width="100%" alt="{name.replace("figure", "Figure ")}">', "", label(cap), ""]

L = [f"# {title}", "", "## Abstract", "", abstract, "", "## Figures", ""]
for n, (cap, png) in enumerate(figs, 1):
    L += show(f"figure{n}", cap, png)
L += ["## Tables", ""]
for cap, rows in tabs:
    L += [label(cap), "", gfm_table(rows), ""]
L += ["## Supplementary material", "", *[t + "\n" for t in supp_text]]
for n, (cap, png) in enumerate(sfigs, 1):
    L += show(f"figureS{n}", cap, png)
for cap, rows in stabs:
    L += [label(cap), "", gfm_table(rows), ""]
open(dst, "w", encoding="utf8").write("\n".join(L).rstrip("\n") + "\n")
print(f"{dst}: {len(tabs)} tables, {len(figs)} figures, {len(sfigs)} supplementary figures, {len(stabs)} supplementary tables, abstract {len(abstract.split())} words")
