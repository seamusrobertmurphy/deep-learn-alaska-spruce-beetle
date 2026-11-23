"""Word counts by section for a rendered manuscript, with the Forestry length used by audit.py.

Run from 01.manuscript or the repository root, python3 05.scripts/section-counts.py FILE.docx

Headings count as prose. The abstract, captions, table text and references are counted apart.
Forestry sets an article at twelve pages of 1,000 words, tables, figures and references included,
and its guide gives no word value for a figure, so each figure counts as 300 words here. That
value is an assumption recorded on 2026-11-09, not a rule of the journal.
"""
import re
import sys
import zipfile

from lxml import etree

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
w = lambda tag: f"{{{W}}}{tag}"
WORD = re.compile(r"[A-Za-z0-9À-ɏ][A-Za-z0-9À-ɏ'’.\-/]*")
FIGURE_WORDS = 300
SKIP = {"Title", "Subtitle", "Author", "Affiliation", "Correspondence", "Date", "SourceCode"}
words = lambda t: len(WORD.findall(t))
text = lambda p: "".join(n.text or "" for n in p.iter(w("t")))


def style(p):
    s = p.find(f"{w('pPr')}/{w('pStyle')}")
    return s.get(w("val")) if s is not None else ""


def counts(docx):
    root = etree.fromstring(zipfile.ZipFile(docx).read("word/document.xml"))
    h1, h2, prose, sub = "Front", "", {}, {}
    other = dict(abstract=0, captions=0, tables=0, refs=0, figures=0, tables_n=0)
    for child in root.find(w("body")):
        if child.tag == w("tbl"):  # Quarto wraps each captioned figure and table in a one-cell table that holds its caption
            for p in child.iter(w("p")):
                t = text(p)
                if "aption" in style(p):
                    other["captions"] += words(t)
                    other["figures"] += bool(re.match(r"Fig(?:ure|\.)\s+\d", t))
                    other["tables_n"] += bool(re.match(r"Table\s+\d", t))
                else:
                    other["tables"] += words(t)
            continue
        if child.tag != w("p"):
            continue
        st, t = style(child), text(child)
        if st in SKIP or not t.strip():
            continue
        if st == "Heading1":
            h1, h2 = re.sub(r"^[\d.]+\s*", "", t.strip()), ""
            prose[h1] = prose.get(h1, 0) + words(t)
        elif st == "Heading2":
            h2 = re.sub(r"^[\d.]+\s*", "", t.strip())
            prose[h1] = prose.get(h1, 0) + words(t)
            sub[(h1, h2)] = sub.get((h1, h2), 0) + words(t)
        elif st == "Abstract":
            other["abstract"] += words(t)
        elif st == "Bibliography":
            other["refs"] += words(t)
        elif "aption" in st:
            other["captions"] += words(t)
            other["figures"] += bool(re.match(r"Fig(?:ure|\.)\s+\d", t))
            other["tables_n"] += bool(re.match(r"Table\s+\d", t))
        else:
            prose[h1] = prose.get(h1, 0) + words(t)
            if h2:
                sub[(h1, h2)] = sub.get((h1, h2), 0) + words(t)
    return prose, sub, other


if __name__ == "__main__":
    prose, sub, other = counts(sys.argv[1])
    body = sum(v for k, v in prose.items() if k != "References")
    print(f"Abstract {other['abstract']:,}")
    for k, v in prose.items():
        if k == "References":
            continue
        print(f"{k} {v:,}")
        for (a, b), n in sub.items():
            if a == k:
                print(f"    {b} {n:,}")
    print(f"Prose of the body {body:,}")
    print(f"Captions {other['captions']:,} on {other['figures']} figures and {other['tables_n']} tables, "
          f"table text {other['tables']:,}, references {other['refs']:,}")
    total = (other["abstract"] + body + other["captions"] + other["tables"] + other["refs"]
             + FIGURE_WORDS * other["figures"])
    print(f"Journal count, abstract, prose, captions, table text and references plus {FIGURE_WORDS} for each figure {total:,}")
