"""Audit of a rendered Forestry submission set, run after every render of the manuscript.

Run from the repository root,
    python3 05.scripts/audit.py 01.manuscript/manuscript-YYYY-MM-DD.docx [--words LIST]

The manuscript names the set. Its source, the supplement and the cover letter are looked for
beside it under the same date. The script exits with status 1 if any of ten checks fails.
  1. A word or phrase from the list in the repository's hidden, untracked settings folder appears in the set or its source.
  2. A number in the abstract is not printed in the Results.
  3. A count named in the charter's glossary is used another way, such as three hypotheses.
  4. A work cited in the source is missing from references.bib, or the reference list holds another number of works.
  5. A figure or table is first cited out of order, cited and absent, or present and never cited.
  6. A borrowed table or figure number sits outside its citation bracket.
  7. The set and the source do not share the manuscript's date.
  8. The length is over Forestry's twelve pages of 1,000 words, counted by section-counts.py.
  9. An abbreviation in a table, its header or its caption is not defined in that caption or header.
 10. A repository folder, local path, data or code file name, or the word skill sits in the reader-facing text of a Word file.
The list of check 1 is read from a file and never written here, so this script names none of its words.
The checks were copied on 2026-11-09 from the audit of canada-emissions-disaggregated and adapted.
"""
import argparse
import html
import importlib.util
import re
import sys
import zipfile
from pathlib import Path

from lxml import etree

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BIB = ROOT / "04.references" / "references.bib"
WORD_LIST = next(iter(sorted(ROOT.glob(".*/audit-words.txt"))), ROOT / "audit-words.txt")
LIMIT = 12_000
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
w = lambda tag: f"{{{W}}}{tag}"

SET = ["supplementary", "cover-letter"]  # beside the manuscript and its source, under the same date; the supplement renders from supplementary-DATE.qmd, the letter from cover-letter-DATE.qmd
CANON = {"hypotheses": "two", "steps": "five", "regions": ("three", "four"), "survey regions": "three", "test regions": "three",
         "plot regions": "four", "comparisons": "four", "reference datasets": "three"}  # charter item 7 of the revision brief; three survey and four plot regions since decision J of 2026-11-19, so a bare count of regions may be either
COUNT_WORDS = "one|two|both|three|four|five|six|seven|eight|nine|ten"
NAMES = {"ArcticDEM", "GLO", "DeLong", "WorldView"}  # product, sensor and person names written with two capitals, not abbreviations
UNITS = ["dB"]  # unit abbreviations with one capital, which the capital pattern misses
NUM = re.compile(r"(?<![\d.,])(?:\d{1,3}(?:[,  ]\d{3})+|\d+)(?:\.\d+)?(?!\d)")
BORROWED = re.compile(r"\b(?:Tables?|Figs?\.|Figures?|Box(?:es)?)\s+[A-Z]?\d+(?:[.\-–]\d+)+")
MENTION = re.compile(r"\b(Tables?|Figs?\.|Figures?)\s+(\d+)(?![.\-–]\d)((?:\s*(?:,|and|to|–)\s*\d+(?![.\-–]\d))*)")
CAPTION = re.compile(r"(Table|Figure|Fig\.)\s+(\d+)\b")
KEY = re.compile(r"(?<![\w.@])@([A-Za-z0-9_][\w:.#$%&\-+?<>~/]*)")
ABBR = re.compile(r"(?<![A-Za-z])[A-Za-z]*[A-Z][a-z]*[A-Z][A-Za-z]*(?![a-z])")
DATED = re.compile(r"-(\d{4}-\d{2}-\d{2})\.docx$")
READER = re.compile(r"word/(document|footnotes|endnotes|comments|header\d*|footer\d*)\.xml$")  # the parts a reader sees
WEB = re.compile(r"https?://\S+|www\.\S+")  # public addresses, removed before check 10 reads the text
PATH = re.compile(r"\b0[1-6]\.[A-Za-z][\w-]*/|/Volumes/|/Users/|~/|(?<![\w.])\.[a-z][\w-]*/|library-science|\b05\.tasks\b"
                  r"|[\w-]+\.(?:csv|tif|tiff|qmd|R|py|gpkg|json|md|docx|pptx|zip|rds|txt|lua)\b")  # Earth Engine asset ids carry no extension and stay allowed
SKILL = re.compile(r"(?<![A-Za-z])skill", re.I)  # priority N3 of 2026-11-15


def style(p):
    s = p.find(f"{w('pPr')}/{w('pStyle')}")
    return s.get(w("val")) if s is not None else ""


def ptext(p):
    return "".join(n.text or "" for n in p.iter(w("t")))


def body(docx):
    return etree.fromstring(zipfile.ZipFile(docx).read("word/document.xml")).find(w("body"))


def paragraphs(docx):
    """Every paragraph of a Word file in reading order, table cells included, as (style, text)."""
    return [(style(p), ptext(p)) for p in body(docx).iter(w("p"))]


def all_text(docx):
    """The text of every XML part of a Word file, properties and comments included."""
    z = zipfile.ZipFile(docx)
    parts = []
    for name in z.namelist():
        if name.endswith(".xml") or name.endswith(".rels"):
            x = z.read(name).decode("utf8", "ignore").replace("</w:p>", "\n")
            parts.append(html.unescape(re.sub(r"<[^>]+>", "", x)))
    return "\n".join(parts)


def sections(paras):
    """Paragraph texts grouped by first-level heading, with the Abstract style as its own section."""
    out, h1 = {}, "Front"
    for st, t in paras:
        if st == "Heading1":
            h1 = re.sub(r"^[\d.]+\s*", "", t.strip())
            continue
        out.setdefault("Abstract" if st == "Abstract" else h1, []).append((st, t))
    return out


def in_citation(text, pos):
    """True if pos lies inside parentheses that hold a year, the form of an author-year citation."""
    open_ = text.rfind("(", 0, pos)
    if open_ < 0 or text.rfind(")", open_, pos) >= 0:
        return False
    close = text.find(")", pos)
    return close >= 0 and re.search(r"\b(?:19|20)\d{2}[a-z]?\b", text[open_:close]) is not None


def numbers_in(first, rest):
    found = [int(first)]
    nums = [int(n) for n in re.findall(r"\d+", rest or "")]
    if re.search(r"\bto\b|–", rest or "") and nums:
        return list(range(found[0], nums[-1] + 1))
    return found + nums


def strip_source(src):
    """A Quarto source without its front matter, code and comments, keeping the caption options of its chunks."""
    caps = "\n".join(re.findall(r"^#\|\s*(?:fig|tbl)-(?:cap|alt):\s*(.*)$", src, flags=re.M))
    src = re.sub(r"\A---\n.*?\n---\n", "", src, flags=re.S)
    src = re.sub(r"^```.*?^```", "", src, flags=re.S | re.M)
    src = re.sub(r"`[^`\n]*`", "", src)
    return re.sub(r"<!--.*?-->", "", src, flags=re.S) + "\n" + caps


def keys_in(text):
    keys = set()
    for m in KEY.finditer(text):
        k = m.group(1).rstrip(".:#$%&-+?<>~/")
        if not re.match(r"(fig|tbl|eq|sec|lst)-", k):
            keys.add(k)
    return keys


def check_words(files, word_list):
    terms = [t.strip() for t in Path(word_list).read_text(encoding="utf8").splitlines()
             if t.strip() and not t.startswith("#")]
    pats = []
    for t in terms:
        bodytxt = re.escape(t).replace(r"\ ", r"\s+")
        pats.append(re.compile(r"(?<![A-Za-z])" + bodytxt + r"s?(?![A-Za-z])", 0 if t.isupper() else re.I))
    bad = []
    for f in files:
        text = all_text(f) if f.suffix == ".docx" else f.read_text(encoding="utf8")
        for t, p in zip(terms, pats):
            n = len(p.findall(text))
            if n:
                bad.append(f"{f.name}: listed word {t!r} {n} time(s)")
    return bad, f"{len(terms)} listed words in {len(files)} files"


def check_abstract(sec):
    abstract = " ".join(t for _, t in sec.get("Abstract", []))
    results = " ".join(t for _, t in sec.get("Results", []))
    if not abstract or not results:
        return ["abstract or Results not found"], ""
    nums = sorted(set(NUM.findall(abstract)), key=lambda x: float(re.sub(r"[,  ]", "", x)))
    norm = lambda s: re.sub(r"(?<=\d)[,  ](?=\d{3})", "", s)
    res = norm(results)
    bad = [f"abstract number {n} is not printed in the Results" for n in nums
           if not re.search(r"(?<![\d.])" + re.escape(norm(n)) + r"(?!\d|\.\d)", res)]
    return bad, f"{len(nums)} numbers in the abstract"


def check_glossary(texts):
    bad = []
    allowed = {k: v if isinstance(v, tuple) else (v,) for k, v in CANON.items()}
    terms = "|".join(re.escape(k) for k in sorted(CANON, key=len, reverse=True))
    for name, text in texts:
        for m in re.finditer(rf"(?i)\b({COUNT_WORDS})\s+({terms})\b", text):
            used, term = m.group(1).lower(), m.group(2).lower()
            if used == "both" and "two" in allowed[term]:
                continue
            if used not in allowed[term]:
                s = max(text.rfind(".", 0, m.start()), text.rfind("\n", 0, m.start())) + 1
                bad.append(f"{name}: {m.group(0)!r} in {text[s:m.end() + 40].strip()!r}")
    return bad, ", ".join(f"{' or '.join(v)} {k}" for k, v in allowed.items())


def check_citations(ms_src, paras):
    src = ms_src.read_text(encoding="utf8")
    in_bib = set(re.findall(r"^@\w+\{([^,\s]+),", BIB.read_text(encoding="utf8"), re.M))
    read = [ROOT / f for f in re.findall(r"read\.csv\(\"([^\"]+)\"", src) if (ROOT / f).exists()]  # tables the source reads may carry citation keys, as the attribute table does
    cited = keys_in(strip_source(src)) | (set().union(*[keys_in(f.read_text(encoding="utf8", errors="ignore")) for f in read]) & in_bib)
    listed = sum(st == "Bibliography" and bool(t.strip()) for st, t in paras)
    bad = [f"cited in {ms_src.name} but not in {BIB.name}: @{k}" for k in sorted(cited - in_bib)]
    if listed != len(cited):
        bad.append(f"the reference list holds {listed} works and the source cites {len(cited)}")
    return bad, f"{len(cited)} works cited, {listed} listed"


def captions(paras):
    """The numbers of the table and figure captions, read from caption paragraphs wherever they sit, inside Quarto's wrapper tables too."""
    out = {"Table": [], "Figure": []}
    for st, t in paras:
        c = CAPTION.match(t)
        if c and "aption" in st:
            out["Table" if c.group(1).startswith("Table") else "Figure"].append(int(c.group(2)))
    return out


def check_items(paras):
    bad, captions, first = [], {"Table": [], "Figure": []}, {"Table": [], "Figure": []}
    kind_of = lambda s: "Table" if s.startswith("Table") else "Figure"
    for st, t in paras:
        c = CAPTION.match(t)
        if c and "aption" in st:
            captions[kind_of(c.group(1))].append(int(c.group(2)))
            continue
        for m in MENTION.finditer(t):
            if in_citation(t, m.start()):
                continue
            for n in numbers_in(m.group(2), m.group(3)):
                if n not in first[kind_of(m.group(1))]:
                    first[kind_of(m.group(1))].append(n)
    for kind in captions:
        if captions[kind] != sorted(captions[kind]):
            bad.append(f"{kind} captions placed out of order: {captions[kind]}")
    for kind, seq in first.items():
        if seq != list(range(1, len(seq) + 1)):
            bad.append(f"{kind} first cited in the order {seq}")
        bad += [f"{kind} {n} is cited but absent" for n in seq if n not in captions[kind]]
        bad += [f"{kind} {n} is present but never cited" for n in captions[kind] if n not in seq]
    return bad, "; ".join(f"{k} {v}" for k, v in first.items())


def check_borrowed(paras):
    bad = []
    for _, t in paras:
        for m in BORROWED.finditer(t):
            if not in_citation(t, m.start()):
                bad.append(f"{m.group(0)!r} outside a citation bracket in {t[max(0, m.start() - 60):m.end() + 20]!r}")
    return bad, ""


def check_dates(ms):
    m = DATED.search(ms.name)
    if not m:
        return [f"{ms.name} does not carry a date"], ""
    d, prefix = m.group(1), ms.name[:m.start()]
    want = [ms.parent / f"{prefix}-{d}.qmd"] + [ms.parent / f"{n}-{d}.docx" for n in SET]
    return [f"missing {p.name}" for p in want if not p.exists()], f"date {d}"


def check_count(ms):
    spec = importlib.util.spec_from_file_location("section_counts", HERE / "section-counts.py")
    sc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sc)
    prose, _, o = sc.counts(ms)
    n = (o["abstract"] + sum(v for k, v in prose.items() if k != "References") + o["captions"] + o["tables"]
         + o["refs"] + sc.FIGURE_WORDS * o["figures"])
    bad = [f"length {n:,} is over {LIMIT:,}"] if n > LIMIT else []
    figs = len(captions(paragraphs(ms))["Figure"])
    if o["figures"] != figs:  # on 2026-11-18 the count added no figure, because each sat in a wrapper table
        bad.append(f"{o['figures']} figures counted against {figs} figure captions")
    return bad, f"length {n:,} of {LIMIT:,}, with {o['figures']} figures at {sc.FIGURE_WORDS} words"


def defined(abbr, legend):
    """True if the legend defines the abbreviation, as "(NDVI)", "NDVI, the", "NDVI is", "NDVI the", "PALSAR-2 is" or "HV and HH the"."""
    a = re.escape(abbr) + r"(?:-\d+)?"  # a numbered name, such as PALSAR-2, defines its stem
    return re.search(rf"\({a}\)|(?<![A-Za-z]){a},\s+(?:the\s+)?[a-z]|(?<![A-Za-z]){a}(?:\s+and\s+[A-Za-z][\w-]*)?\s+(?:is|are|the|means|denotes|stands for)\s|(?<![A-Za-z]){a}\s*=", legend) is not None


TABLE_CAP = re.compile(r"Table\s+(S\s?\d+|\d+)\b")  # Table 1 of the manuscript and Table S1 of the supplement, before or after supplement-labels.py closes "Table S 1"


def check_abbreviations(files):
    """Each data table follows its Table N or Table SN caption in the same cell of a wrapper table, as Quarto writes it,
    with two tables of adjacent chunks sharing one wrapper of two rows, or follows the caption in the body once a layout
    script has unwrapped it. Figure and equation tables carry no Table caption. The supplement is read since 2026-11-19."""
    bad, n_read, n_caps = [], 0, 0
    for f in files:
        read, pairs = [], []
        kids = list(body(f))
        for i, el in enumerate(kids):
            if el.tag != w("tbl"):
                continue
            inside = [p for p in el.iter(w("p")) if "aption" in style(p) and TABLE_CAP.match(ptext(p))]
            if inside:
                pairs += [(ptext(p), next((s for s in p.itersiblings() if s.tag == w("tbl")), None)) for p in inside]
            else:
                pairs.append((next((ptext(k) for k in reversed(kids[max(0, i - 3):i]) if k.tag == w("p") and ptext(k).strip()), ""), el))
        for cap, data in pairs:
            c = TABLE_CAP.match(cap)
            if not c or data is None:
                continue
            num = re.sub(r"\s", "", c.group(1))
            read.append(num)
            rows = data.findall(w("tr"))
            header = " ".join(ptext(p) for p in rows[0].iter(w("p"))) if rows else ""
            cells = " ".join(ptext(p) for p in data.iter(w("p")))
            found = set(ABBR.findall(cells + " " + cap)) - NAMES
            found |= {u for u in UNITS if re.search(rf"(?<![A-Za-z]){u}(?![A-Za-z])", cells + " " + cap)}
            missing = sorted(a for a in found if not defined(a, cap + " " + header))
            bad += [f"Table {num}: {a} is not defined in its caption" for a in missing]
        caps = [re.sub(r"\s", "", TABLE_CAP.match(t).group(1)) for st, t in paragraphs(f) if "aption" in st and TABLE_CAP.match(t)]
        bad += [f"Table {n} has a caption but its table was not read" for n in caps if n not in read]  # on 2026-11-18 the check read no table and passed
        n_read, n_caps = n_read + len(read), n_caps + len(caps)
    return bad, f"{n_read} tables read of {n_caps} table captions in {len(files)} Word files"


def check_paths(files):
    """Readers see no repository path, local path or file name, the rule Seamus set on 2026-11-15 as priority N2."""
    bad = []
    for f in files:
        z = zipfile.ZipFile(f)
        for name in (n for n in z.namelist() if READER.match(n)):
            x = z.read(name).decode("utf8", "ignore").replace("</w:p>", "\n")
            text = WEB.sub(" ", html.unescape(re.sub(r"<[^>]+>", "", x)))
            for m in list(PATH.finditer(text)) + list(SKILL.finditer(text)):
                bad.append(f"{f.name}: {m.group(0)!r} in {text[max(0, m.start() - 50):m.end() + 20].strip()!r}")
    return bad, f"{len(files)} Word files"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("manuscript")
    ap.add_argument("--words", default=str(WORD_LIST))
    a = ap.parse_args()
    ms = Path(a.manuscript).resolve()
    m = DATED.search(ms.name)
    d, prefix = (m.group(1), ms.name[:m.start()]) if m else ("", ms.stem)
    src = ms.parent / f"{prefix}-{d}.qmd"
    paras = paragraphs(ms)
    sec = sections(paras)
    present = [ms] + [p for p in [src] + [ms.parent / f"{n}-{d}.docx" for n in SET] if p.exists()]
    gloss = [(f.name, "\n".join(t for _, t in paragraphs(f))) for f in present if f.suffix == ".docx"]
    checks = [
        ("1 listed words", lambda: check_words(present, a.words)),
        ("2 abstract numbers in Results", lambda: check_abstract(sec)),
        ("3 glossary counts", lambda: check_glossary(gloss)),
        ("4 citations and reference list", lambda: check_citations(src, paras)),
        ("5 display item order", lambda: check_items(paras)),
        ("6 borrowed numbers in brackets", lambda: check_borrowed(paras)),
        ("7 one date", lambda: check_dates(ms)),
        ("8 length", lambda: check_count(ms)),
        ("9 table abbreviations defined", lambda: check_abbreviations([f for f in present if f.suffix == ".docx"])),
        ("10 no repository paths", lambda: check_paths([f for f in present if f.suffix == ".docx"])),
    ]
    failed = 0
    for name, run in checks:
        try:
            bad, note = run()
        except Exception as e:  # a check that cannot run counts as failed
            bad, note = [f"check could not run, {type(e).__name__}, {e}"], ""
        print(f"{'FAIL' if bad else 'PASS'}  {name}" + (f"  ({note})" if note else ""))
        for b in bad:
            print(f"      {b}")
        failed += bool(bad)
    print(f"{failed} of {len(checks)} checks failed" if failed else f"all {len(checks)} checks passed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
