"""Lays the rendered revision out for the Journal of Applied Remote Sensing, after forestry-layout.py --inline and landscape-tables.py.

  python3 ../05.scripts/jars-layout.py manuscript-jars-2026-11-06.docx
  python3 ../05.scripts/jars-layout.py supplementary-2026-11-05.docx

It makes five changes and can be run again on its own output.

1. Quarto puts each figure and each table, with its caption, in a one-cell outer table of fixed width. Word crops a
   picture at the edge of its cell, which cut the right side off Figure 2 on 5 November 2026, and an outer table of
   fixed width keeps the table inside it from fitting its contents. Each figure and each table is taken out of its
   outer table onto the page, the caption kept with what it describes.
2. Every data table is set to Word's AutoFit to contents. Its columns are made as wide as their longest line, measured
   in the font and size of each run, so that no cell wraps, and every cell is marked not to wrap. Where the one-line
   widths of a table exceed the width of the page, as for Table 1, no width can hold every cell on one line, so the
   columns are shared as Word's AutoFit shares them, each taking its longest word and a part of what remains in
   proportion to the rest of its longest line. The other tables in the file, the borderless grids that hold each
   numbered equation in the template's 10, 80 and 10 per cent columns, are set to AutoFit to the window, which keeps
   those percentage widths, so that every table in the file is AutoFit.
3. Every data table is aligned the same way, as Seamus asked on 5 November 2026: the header row centred and the text
   of every body row on the left.
4. The figure and table captions take the fonts of the journal's Word template, journal_Word_template.docx, read on
   5 November 2026 from https://www.spiedigitallibrary.org/documents/Journals/journal_Word_template.docx. Its Figure
   caption and Table caption styles are 10 pt in the template's Times New Roman, with only the label in bold.
5. Every style and run is set in Times New Roman, the template's font, as Seamus asked on 5 November 2026, at the sizes
   of the template's font table: title 16 pt, authors 12, affiliation, correspondence and abstract 10, headings 12 and
   11, body 12 and references 11, with table text at 10 pt as in the template's own table. The hidden code keeps
   Consolas and the equations Cambria Math, a math font. Cross-references, links and the two Earth Engine asset names
   of the Data availability statement take the font, size and slant of the text around them.
"""
import os, re, shutil, sys, tempfile, zipfile
from lxml import etree
from PIL import ImageFont

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
q = lambda tag: f"{{{W}}}{tag}"
text = lambda el: "".join(t.text or "" for t in el.iter(q("t")))
CAPTION = re.compile(r"^(Figure|Table)[\s ]+S?\d+\.?")
CAPTION_STYLES = {"ImageCaption", "TableCaption", "Caption"}
WORD_FONTS = "/Applications/Microsoft Word.app/Contents/Resources/DFonts/"
FONT_FILES = {  # family and bold to the file and face used to measure it
    ("Calibri", False): (WORD_FONTS + "Calibri.ttf", 0), ("Calibri", True): (WORD_FONTS + "Calibrib.ttf", 0),
    ("Helvetica", False): ("/System/Library/Fonts/Helvetica.ttc", 0), ("Helvetica", True): ("/System/Library/Fonts/Helvetica.ttc", 1),
    ("Times New Roman", False): ("/System/Library/Fonts/Supplemental/Times New Roman.ttf", 0),
    ("Times New Roman", True): ("/System/Library/Fonts/Supplemental/Times New Roman Bold.ttf", 0)}
_fonts = {}


def width(s, family, bold, half_points):
    """Width of s in twips, measured with the font at 20 pixels to the point, so one pixel is one twip."""
    key = (family if (family, bold) in FONT_FILES else "Calibri", bold, half_points)
    if key not in _fonts:
        f, i = FONT_FILES[key[:2]]; _fonts[key] = ImageFont.truetype(f, half_points * 10, index=i)
    return _fonts[key].getlength(s)


def on(el):
    return el is not None and el.get(q("val")) not in ("0", "false")


def child(parent, tag, order):
    """The child tag of parent, created in its place in the schema order if missing."""
    el = parent.find(q(tag))
    if el is None:
        el = etree.Element(q(tag)); later = order[order.index(tag) + 1:]
        nxt = next((c for c in parent if etree.QName(c).localname in later), None)
        nxt.addprevious(el) if nxt is not None else parent.append(el)
    return el


TBLPR = ["tblStyle", "tblpPr", "tblOverlap", "bidiVisual", "tblStyleRowBandSize", "tblStyleColBandSize", "tblW", "jc", "tblCellSpacing",
         "tblInd", "tblBorders", "shd", "tblLayout", "tblCellMar", "tblLook", "tblCaption", "tblDescription"]
TCPR = ["cnfStyle", "tcW", "gridSpan", "hMerge", "vMerge", "tcBorders", "shd", "noWrap", "tcMar", "textDirection", "tcFitText", "vAlign", "hideMark"]
RPR = ["rStyle", "rFonts", "b", "bCs", "i", "iCs", "caps", "smallCaps", "strike", "dstrike", "outline", "shadow", "emboss", "imprint", "noProof",
       "snapToGrid", "vanish", "webHidden", "color", "spacing", "w", "kern", "position", "sz", "szCs", "highlight", "u", "effect", "bdr", "shd",
       "fitText", "vertAlign", "rtl", "cs", "em", "lang", "eastAsianLayout", "specVanish", "oMath"]


def margin(el, side):
    m = el.find(f"{q('tcMar')}/{q(side)}") if el.tag == q("tcPr") else el.find(f"{q('tblCellMar')}/{q(side)}")
    return None if m is None else int(m.get(q("w")))


def unwrap_figures(body):
    n = 0
    for tbl in body.findall(q("tbl")):
        cells = list(tbl.iter(q("tc")))
        if len(cells) != 1 or not list(cells[0].iter(q("drawing"))) or not any(CAPTION.match(text(p)) and text(p).startswith("Figure") for p in cells[0].findall(q("p"))):
            continue
        for el in [c for c in cells[0] if c.tag != q("tcPr")]:
            if el.tag == q("p") and list(el.iter(q("drawing"))):
                ppr = el.find(q("pPr"))
                if ppr is None: ppr = etree.Element(q("pPr")); el.insert(0, ppr)
                if ppr.find(q("keepNext")) is None:
                    k = etree.Element(q("keepNext")); ps = ppr.find(q("pStyle"))
                    ps.addnext(k) if ps is not None else ppr.insert(0, k)
            tbl.addprevious(el)
        body.remove(tbl); n += 1
    return n


def run_font(r, default_family):
    rpr = r.find(q("rPr"))
    fam = default_family; bold = False; hp = 20
    if rpr is not None:
        rf = rpr.find(q("rFonts"))
        if rf is not None and rf.get(q("ascii")): fam = rf.get(q("ascii"))
        bold = on(rpr.find(q("b")))
        if rpr.find(q("sz")) is not None: hp = int(rpr.find(q("sz")).get(q("val")))
    return fam, bold, hp


def cell_widths(tc, default_family):
    """The one-line text width, the longest word and the paragraph indents of a cell, in twips."""
    line, word, pad = 0.0, 0.0, 0
    for p in tc.findall(q("p")):
        ind = p.find(f"{q('pPr')}/{q('ind')}")
        pad = max(pad, 0 if ind is None else int(ind.get(q("left"), 0) or 0) + int(ind.get(q("right"), 0) or 0))
        w = 0.0
        for r in p.findall(f".//{q('r')}"):
            fam, bold, hp = run_font(r, default_family); s = text(r)
            w += width(s, fam, bold, hp)
            for tok in s.split():
                word = max(word, width(tok, fam, bold, hp))
        line = max(line, w)
    return line, word, pad


def set_indents(data, side):
    """Set the left and right paragraph indents of every cell that has them to side twips."""
    for ind in data.iter(q("ind")):
        for a in ("left", "right"):
            if ind.get(q(a)) is not None: ind.set(q(a), str(side))


PPR = ["pStyle", "keepNext", "keepLines", "pageBreakBefore", "framePr", "widowControl", "numPr", "suppressLineNumbers", "pBdr", "shd", "tabs",
       "suppressAutoHyphens", "kinsoku", "wordWrap", "overflowPunct", "topLinePunct", "autoSpaceDE", "autoSpaceDN", "bidi", "adjustRightInd",
       "snapToGrid", "spacing", "ind", "contextualSpacing", "mirrorIndents", "suppressOverlap", "jc", "textDirection", "textAlignment",
       "textboxTightWrap", "outlineLvl", "divId", "cnfStyle", "rPr", "sectPr", "pPrChange"]


def unwrap_tables(body):
    """Take each data table and its caption out of Quarto's outer table, one cell to a row, the caption inside or, after a
    Word save, just before it. Tables 3 and 4 share one outer table of two rows."""
    n = 0
    for outer in body.findall(q("tbl")):
        rows = outer.findall(q("tr")); cells = outer.findall(f"{q('tr')}/{q('tc')}")
        if len(cells) != len(rows) or not all(c.find(q("tbl")) is not None for c in cells):
            continue
        for el in [c for cell in cells for c in cell if c.tag != q("tcPr")]:
            if el.tag == q("p") and CAPTION.match(text(el)):
                pp = el.findall(q("pPr"))[-1] if el.findall(q("pPr")) else None
                if pp is None: pp = etree.Element(q("pPr")); el.insert(0, pp)
                child(pp, "keepNext", PPR)
            outer.addprevious(el)
        body.remove(outer); n += 1
    return n


def captioned_tables(body):
    """Each top-level table whose nearest paragraph before it is a table caption, with that caption's text."""
    out = []
    for tbl in body.findall(q("tbl")):
        prev = tbl.getprevious()
        while prev is not None and prev.tag != q("p"):
            prev = prev.getprevious()
        if prev is not None and CAPTION.match(text(prev)) and text(prev).startswith("Table"):
            out.append((tbl, text(prev)))
    return out


def text_width_at(el, body):
    """The text width of the section the element sits in, read from the next section break after it."""
    nxt = el.getnext()
    while nxt is not None:
        sp = nxt.find(f"{q('pPr')}/{q('sectPr')}") if nxt.tag == q("p") else (nxt if nxt.tag == q("sectPr") else None)
        if sp is not None: break
        nxt = nxt.getnext()
    sp = sp if nxt is not None else body.find(q("sectPr"))
    return int(sp.find(q("pgSz")).get(q("w"))) - int(sp.find(q("pgMar")).get(q("left"))) - int(sp.find(q("pgMar")).get(q("right")))


def align(data):
    """Centre the header row and put the text of every body row on the left."""
    rows = data.findall(q("tr"))
    head = {i for i, r in enumerate(rows) if r.find(f"{q('trPr')}/{q('tblHeader')}") is not None} or {0}
    for i, r in enumerate(rows):
        for p in r.iter(q("p")):
            pps = p.findall(q("pPr"))
            pp = pps[-1] if pps else None
            if pp is None: pp = etree.Element(q("pPr")); p.insert(0, pp)
            for x in pps:
                for j in x.findall(q("jc")): x.remove(j)
            child(pp, "jc", PPR).set(q("val"), "center" if i in head else "left")


def autofit(body, style_margins, family):
    report = []
    for data, cap in captioned_tables(body):
        caps = [cap]
        avail = text_width_at(data, body)
        align(data)
        tblpr = data.find(q("tblPr"))
        d_l = margin(tblpr, "left"); d_r = margin(tblpr, "right")
        rows = data.findall(q("tr")); ncol = max(len(r.findall(q("tc"))) for r in rows)
        text_w = [0.0] * ncol; word_w = [0.0] * ncol; mar = [0] * ncol; ind = 0
        for r in rows:
            for j, tc in enumerate(r.findall(q("tc"))):
                tcpr = tc.find(q("tcPr"))
                m_l = margin(tcpr, "left") if tcpr is not None else None; m_r = margin(tcpr, "right") if tcpr is not None else None
                mar[j] = max(mar[j], (m_l if m_l is not None else d_l if d_l is not None else style_margins[0]) + (m_r if m_r is not None else d_r if d_r is not None else style_margins[1]))
                lw, ww, pad = cell_widths(tc, family)
                text_w[j] = max(text_w[j], lw); word_w[j] = max(word_w[j], ww); ind = max(ind, pad // 2)
        need = lambda side, w: [x * 1.04 + 30 + mar[j] + 2 * side for j, x in enumerate(w)]  # 4 per cent and 30 twips spare, so that Word's own spacing does not wrap a line
        side = 100 if ind else 0
        for trial in ((100, 80, 60, 40) if ind else (0,)):  # flextable's 100 twips a side, or narrower down to 40 where that keeps every cell on one line
            if sum(need(trial, text_w)) <= avail:
                side = trial; break
        if side != ind:
            set_indents(data, side)
        line = need(side, text_w); word = need(side, word_w)
        one_line = sum(line) <= avail
        if one_line:
            cols = [round(x) for x in line]
        else:
            spare = avail - sum(word); extra = sum(line) - sum(word)
            cols = [round(word[j] + (line[j] - word[j]) * spare / extra) for j in range(ncol)] if spare > 0 else [round(x * avail / sum(word)) for x in word]
        # the table: AutoFit to contents, centred, its grid the measured widths
        for tag, attrs in (("tblW", {"w": "0", "type": "auto"}), ("jc", {"val": "center"}), ("tblLayout", {"type": "autofit"})):
            el = child(tblpr, tag, TBLPR)
            for a in list(el.attrib): del el.attrib[a]
            for a, v in attrs.items(): el.set(q(a), v)
        for c in sorted(tblpr, key=lambda c: TBLPR.index(etree.QName(c).localname) if etree.QName(c).localname in TBLPR else len(TBLPR)):
            tblpr.append(c)  # flextable writes tblLayout before tblW; Word expects the schema order
        grid = data.find(q("tblGrid"))
        if grid is None:
            grid = etree.Element(q("tblGrid")); tblpr.addnext(grid)
        for g in list(grid): grid.remove(g)
        for w in cols:
            etree.SubElement(grid, q("gridCol")).set(q("w"), str(w))
        for r in rows:
            for j, tc in enumerate(r.findall(q("tc"))):
                tcpr = tc.find(q("tcPr"))
                if tcpr is None: tcpr = etree.Element(q("tcPr")); tc.insert(0, tcpr)
                tcw = child(tcpr, "tcW", TCPR); tcw.set(q("w"), str(cols[j])); tcw.set(q("type"), "dxa")
                nw = tcpr.find(q("noWrap"))
                if one_line and nw is None: child(tcpr, "noWrap", TCPR)
                if not one_line and nw is not None: tcpr.remove(nw)
        report.append(f"{caps[0][:8].replace(chr(160), ' ')} {'one line per cell' if one_line else 'wraps, the one-line widths exceed the page'}: {round(sum(cols))} of {avail} twips, cell text indent {side} twips a side")
    return report


def autofit_window(body, data_tables):
    """AutoFit to the window for every other table, keeping its preferred widths."""
    n = 0
    for tbl in body.iter(q("tbl")):
        if tbl in data_tables:
            continue
        tblpr = tbl.find(q("tblPr"))
        el = child(tblpr, "tblLayout", TBLPR)
        for a in list(el.attrib): del el.attrib[a]
        el.set(q("type"), "autofit"); n += 1
    return n


TNR = "Times New Roman"
KEEP_FONTS = {"Consolas", "Cambria Math"}  # the hidden code and the equations, whose math needs a math font
TEMPLATE_SIZES = {  # half points, from the font table of the template and its References style
    "Title": 32, "TitleChar": 32, "Author": 24, "Affiliation": 20, "Correspondence": 20, "Abstract": 20,
    "Heading1": 24, "Heading1Char": 24, "Heading2": 24, "Heading2Char": 24, "Heading3": 22, "Heading3Char": 22,
    "Bibliography": 22, "Compact": 20, "Table": 20}
STYLE = ["name", "aliases", "basedOn", "next", "link", "autoRedefine", "hidden", "uiPriority", "semiHidden", "unhideWhenUsed", "qFormat",
         "locked", "personal", "personalCompose", "personalReply", "rsid", "pPr", "rPr", "tblPr", "trPr", "tcPr", "tblStylePr"]


def tnr(rf):
    for a in list(rf.attrib): del rf.attrib[a]
    for a in ("ascii", "hAnsi", "eastAsia", "cs"): rf.set(q(a), TNR)


def document_fonts(root, styles, data_tables):
    """Times New Roman in every style and run, at the sizes of the template: body 12 pt, title 16, authors 12, affiliation,
    correspondence and abstract 10, headings 12 and 11, references 11, and the table text 10 pt, as in the template's own table."""
    dd = styles.find(f"{q('docDefaults')}/{q('rPrDefault')}/{q('rPr')}")
    tnr(child(dd, "rFonts", RPR))
    for tag in ("sz", "szCs"): child(dd, tag, RPR).set(q("val"), "24")
    for st in styles.findall(q("style")):
        sid = st.get(q("styleId")); rpr = st.find(q("rPr"))
        rf = None if rpr is None else rpr.find(q("rFonts"))
        if rf is not None and rf.get(q("ascii")) not in KEEP_FONTS: tnr(rf)
        if sid in TEMPLATE_SIZES:
            rpr = child(st, "rPr", STYLE)
            for tag in ("sz", "szCs"): child(rpr, tag, RPR).set(q("val"), str(TEMPLATE_SIZES[sid]))
        if sid == "Affiliation" and rpr is not None:  # the template's affiliation line is not italic
            for tag in ("i", "iCs"): child(rpr, tag, RPR).set(q("val"), "0")
        if sid in ("Hyperlink", "VerbatimChar"):  # cross-references, links and the two asset names take the font, size and slant of the text around them
            st.find(q("basedOn")).set(q("val"), "DefaultParagraphFont")
            for tag in ("rFonts", "i", "iCs", "sz", "szCs"):
                for el in rpr.findall(q(tag)): rpr.remove(el)
    runs = 0
    for rf in root.iter(q("rFonts")):
        if rf.get(q("ascii")) not in KEEP_FONTS: tnr(rf); runs += 1
    for tbl in data_tables:
        for tag in ("sz", "szCs"):
            for el in tbl.iter(q(tag)): el.set(q("val"), "20")
    return runs


def caption_fonts(root, styles):
    """Times New Roman at 10 pt, not bold, with the label in bold, in the caption styles and in each caption."""
    def set_rpr(rpr, bold):
        rf = child(rpr, "rFonts", RPR)
        for a in list(rf.attrib): del rf.attrib[a]
        for a in ("ascii", "hAnsi", "eastAsia", "cs"): rf.set(q(a), "Times New Roman")
        for tag in ("b", "bCs"):
            el = child(rpr, tag, RPR)
            if bold: el.attrib.pop(q("val"), None)
            else: el.set(q("val"), "0")
        for tag in ("sz", "szCs"): child(rpr, tag, RPR).set(q("val"), "20")
    for st in styles.findall(q("style")):
        if st.get(q("styleId")) in CAPTION_STYLES:
            rpr = st.find(q("rPr"))
            if rpr is None: rpr = etree.SubElement(st, q("rPr"))
            set_rpr(rpr, False)
            for tag in ("i", "iCs"): child(rpr, tag, RPR).set(q("val"), "0")  # upright as in the template, where Abstract Title, its base here, is italic
    n = 0
    for p in root.iter(q("p")):
        st = {ps.get(q("val")) for ps in p.findall(f"{q('pPr')}/{q('pStyle')}")}
        m = CAPTION.match(text(p))
        nxt = p.getnext()
        table_caption = m and text(p).startswith("Table") and nxt is not None and nxt.tag == q("tbl")
        if not (m and (st & CAPTION_STYLES or table_caption)):
            continue
        if not st & CAPTION_STYLES:  # a table caption Word saved in Body Text takes the caption style of the others
            pp = p.find(q("pPr"))
            if pp is None: pp = etree.Element(q("pPr")); p.insert(0, pp)
            child(pp, "pStyle", PPR).set(q("val"), "ImageCaption")
        runs = list(p.iter(q("r")))
        for r in runs:
            rpr = r.find(q("rPr"))
            if rpr is None: rpr = etree.Element(q("rPr")); r.insert(0, rpr)
            set_rpr(rpr, False)
        first = runs[0]; t = first.find(q("t")); label = m.group(0)
        if t is not None and t.text == label:  # split on an earlier run of this script
            set_rpr(first.find(q("rPr")), True)
        elif t is not None and t.text and t.text.startswith(label):
            lab = etree.fromstring(etree.tostring(first)); lab.find(q("t")).text = label
            set_rpr(lab.find(q("rPr")), True); first.addprevious(lab)
            t.text = t.text[len(label):]; t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
        n += 1
    return n


def main(path):
    with zipfile.ZipFile(path) as z:
        names = z.namelist(); data = {n: z.read(n) for n in names}
    root = etree.fromstring(data["word/document.xml"]); styles = etree.fromstring(data["word/styles.xml"])
    tstyle = next((s for s in styles.findall(q("style")) if s.get(q("styleId")) == "Table"), None)
    sm = [108, 108]  # Word's default left and right cell margins
    if tstyle is not None and tstyle.find(f"{q('tblPr')}/{q('tblCellMar')}") is not None:
        sm = [margin(tstyle.find(q("tblPr")), s) or 0 for s in ("left", "right")]
    body = root.find(q("body"))
    figs = unwrap_figures(body)
    wrapped = unwrap_tables(body)
    runs = document_fonts(root, styles, [t for t, _ in captioned_tables(body)])
    tables = autofit(body, sm, TNR)
    others = autofit_window(body, [t for t, _ in captioned_tables(body)])
    caps = caption_fonts(root, styles)
    data["word/document.xml"] = etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)
    data["word/styles.xml"] = etree.tostring(styles, xml_declaration=True, encoding="UTF-8", standalone=True)
    fd, tmp = tempfile.mkstemp(suffix=".docx", dir=os.path.dirname(os.path.abspath(path))); os.close(fd)
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for n in names: zout.writestr(n, data[n])
    shutil.move(tmp, path)
    print(f"{path}: {figs} figures and {wrapped} tables taken out of their outer tables, {len(tables)} data tables set to AutoFit to contents with the header centred and the body on the left, {others} equation tables set to AutoFit to the window, {runs} run fonts and every style set to Times New Roman at the template's sizes, {caps} captions set in Times New Roman 10 pt")
    for line in tables: print("  " + line)


if __name__ == "__main__":
    for a in sys.argv[1:]: main(a)
