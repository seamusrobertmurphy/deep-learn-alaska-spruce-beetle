"""Proof that every check of audit.py can fail. Each fault is planted in a fresh copy of the set,
and the check must then fail and name the planted fault.

Run from the repository root,
    python3 05.scripts/audit-selftest.py 01.manuscript/manuscript-forestry-new-YYYY-MM-DD.docx SCRATCH_DIR

The copies are made under SCRATCH_DIR, and the set itself is never written. The listed word of
check 1 is read from the same list audit.py reads, so this script names none of those words.
Faults are appended to paragraphs found by their style, so no plant depends on a sentence of the text.
"""
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

from lxml import etree

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SET = ["supplementary", "cover-letter"]
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
w = lambda tag: f"{{{W}}}{tag}"

ms, scratch = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
m = re.search(r"-(\d{4}-\d{2}-\d{2})\.docx$", ms.name)
date, prefix = m.group(1), ms.name[:m.start()]
MS, SRC = f"{prefix}-{date}.docx", f"{prefix}-{date}.qmd"
word_list = next(iter(sorted(ROOT.glob(".*/audit-words.txt"))))
word = next(t.strip() for t in word_list.read_text(encoding="utf8").splitlines() if t.strip() and not t.startswith("#"))


def fresh(name):
    d = scratch / name
    if d.exists():
        shutil.rmtree(d)
    d.mkdir(parents=True)
    for f in [ms, ms.parent / SRC] + [ms.parent / f"{n}-{date}.docx" for n in SET]:
        if f.exists():
            shutil.copy2(f, d)
    return d


def docx_append(path, text, where):
    """Append text to the last run of the first paragraph that where(paragraph, in_table) accepts."""
    tmp = path.with_suffix(".tmp")
    with zipfile.ZipFile(path) as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "word/document.xml":
                root = etree.fromstring(data)
                for p in root.iter(w("p")):
                    runs = list(p.iter(w("t")))
                    if runs and where(p, any(a.tag == w("tbl") for a in p.iterancestors())):
                        runs[-1].text = (runs[-1].text or "") + text
                        break
                else:
                    raise AssertionError(f"no paragraph to plant in {path.name}")
                data = etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)
            zout.writestr(item, data)
    tmp.replace(path)


def style(p):
    s = p.find(f"{w('pPr')}/{w('pStyle')}")
    return s.get(w("val")) if s is not None else ""


abstract = lambda p, t: style(p) == "Abstract"
prose = lambda p, t: not t and style(p) in ("FirstParagraph", "BodyText")
table_cell = lambda p, t: t


def audit(d):
    out = subprocess.run([sys.executable, str(HERE / "audit.py"), str(d / MS)], capture_output=True, text=True).stdout
    blocks, cur = {}, None
    for line in out.splitlines():
        mm = re.match(r"(PASS|FAIL)\s+(\d) ", line)
        if mm:
            cur = mm.group(2)
            blocks[cur] = [mm.group(1), ""]
        elif cur and line.startswith("      "):
            blocks[cur][1] += line + "\n"
    return blocks


def plant_1(d):
    docx_append(d / MS, f" {word}", abstract)
    (d / SRC).write_text((d / SRC).read_text(encoding="utf8") + f"\n{word}\n", encoding="utf8")
    return [f"{MS}: listed word {word!r}", f"{SRC}: listed word {word!r}"]


def plant_2(d):
    docx_append(d / MS, " 98765.4", abstract)
    return ["abstract number 98765.4"]


def plant_3(d):
    docx_append(d / MS, " The three hypotheses held.", prose)
    return ["'three hypotheses'"]


def plant_4(d):
    (d / SRC).write_text((d / SRC).read_text(encoding="utf8") + "\n\nPlanted sentence [@plantedkey2099].\n", encoding="utf8")
    return ["@plantedkey2099"]


def plant_5(d):
    docx_append(d / MS, " (Table 9)", prose)
    return ["Table 9 is cited but absent"]


def plant_6(d):
    docx_append(d / MS, " as in Table 2.4", prose)
    return ["'Table 2.4' outside a citation bracket"]


def plant_7(d):
    (d / SRC).unlink()
    return [f"missing {SRC}"]


def length(path):
    out = subprocess.run([sys.executable, str(HERE / "section-counts.py"), str(path)], capture_output=True, text=True).stdout
    return int(re.search(r"([\d,]+)\s*$", out.strip().splitlines()[-1]).group(1).replace(",", ""))


def plant_8(d):
    clean = length(d / MS)
    docx_append(d / MS, " word" * 13000, prose)
    return [f"length {clean + 13000:,} is over 12,000"]  # the planted words counted exactly, so the proof holds even when the clean copy is already over


def plant_9(d):
    docx_append(d / MS, " XQZ", table_cell)
    return ["XQZ is not defined in its caption"]


plants = [plant_1, plant_2, plant_3, plant_4, plant_5, plant_6, plant_7, plant_8, plant_9]
base = audit(fresh("clean"))
print("clean copy:", ", ".join(f"{k} {v[0]}" for k, v in sorted(base.items())))
proved = 0
for n, plant in enumerate(plants, start=1):
    d = fresh(f"plant-{n}")
    markers = plant(d)
    got = audit(d).get(str(n), ["MISSING", ""])
    named = all(mk in got[1] for mk in markers)
    ok = got[0] == "FAIL" and named
    proved += ok
    state = "passed clean and failed planted" if ok and base[str(n)][0] == "PASS" else \
        "already failing on the clean copy, planted fault named" if ok else ""
    print(f"check {n}: {'proved' if ok else 'NOT PROVED'}, planted fault {'named' if named else 'NOT NAMED'}, {state}")
    if not ok:
        print(got[1])
print(f"{proved} of {len(plants)} checks proved able to fail")
sys.exit(0 if proved == len(plants) else 1)
