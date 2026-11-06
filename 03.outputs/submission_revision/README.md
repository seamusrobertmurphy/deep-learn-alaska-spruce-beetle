# Submission files

Prepared on 4 November 2026 for the Journal of Applied Remote Sensing, on Seamus's instruction of that day to assume that journal without reading its guide for authors. On 5 November 2026 the manuscript and supplement were set in the fonts of the journal's Word template, `journal_Word_template.docx`, read that day. Every part is Times New Roman, at 16 pt for the title, 12 for authors, headings and body, 10 for the affiliation, abstract, captions and tables, and 11 for references. No other requirement of the journal is applied here. Every file is a copy of a render, and a file edited here by hand will be overwritten by the next render.

| File | Source | What it holds |
|---|---|---|
| `manuscript.docx` | `01.manuscript/manuscript-jars.qmd`, code hidden, laid out by `forestry-layout.py --inline`, `landscape-tables.py` and `jars-layout.py` | Title page block, abstract of 248 words, text, six tables and three figures in place, end statements and references |
| `figure1.tif` | chunk `fig-study` | Study area map, 3750 by 4000 pixels at 500 dots per inch |
| `figure2.tif` | chunk `fig-workflow` | Flowchart of the data, steps and tests, 3150 by 3500 pixels at 500 dots per inch |
| `figure3.tif` | chunk `fig-statewide` | Statewide susceptibility map, 3600 by 1950 pixels at 500 dots per inch |
| `supplementary_material.docx` | `01.manuscript/supplementary.qmd`, code hidden, labels closed by `supplement-labels.py`, caption set by `jars-layout.py` | Figure S1, survey damage by year and latitude |
| `figureS1.tif` | chunk of `supplementary.qmd` | Figure S1, 3500 by 1800 pixels at 500 dots per inch |
| `cover_letter.docx` | `01.manuscript/cover-letter.qmd` | Letter to the editor stating what the map is, its accuracy, the comparisons and the declarations, with every number read from `03.outputs/` |
| `title_page.docx` | `01.manuscript/title-page.qmd` | Title, author, affiliation, email and ORCID |

Still Seamus's to enter or confirm are the telephone number on the corresponding author line, the Funding and Acknowledgements wording, and any referees the submission form asks for.
