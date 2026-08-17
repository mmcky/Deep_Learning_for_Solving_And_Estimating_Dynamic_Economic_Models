# Validation

How faithful is this MyST rendering to the printed script, and how was that established?

The conversion is mechanical — `lecture_script/…​.tex` in, `mystmd/*.md` out — so its failure modes are *systematic* rather than random. A macro that drops, an environment that mis-converts, or a numbering rule that differs will do so everywhere it occurs. Validation therefore works by class: find a defect, fix it at the converter or config level, then confirm the whole class is gone.

That process ran over 28 rounds between May and August 2026. This file records the resulting state and the method. The full round-by-round history — every pin bump, every regression, every upstream issue filed — is kept for provenance in the [conversion fork](https://github.com/mmcky/Deep_Learning_for_Solving_And_Estimating_Dynamic_Economic_Models/blob/mystmd-conversion/mystmd/VALIDATION.md) rather than reproduced here.

## Current state

Pins: converter [`182214f`](https://github.com/QuantEcon/claude-latex-to-myst/commit/182214f860132e7447d0ec40bc0fba9ffb9136be), renderer [`qe-v10`](https://github.com/QuantEcon/mystmd/releases/tag/qe-v10) (QuantEcon mystmd fork).

| Check | Result |
|---|---|
| `myst build --html` | **2 warnings, 0 errors** |
| Equation numbers vs the printed PDF | **272 / 272** |
| Section numbers vs the PDF's table of contents | **127 / 127** |
| Cross-references resolving | **813 / 813** |
| Figures rendering | **88 / 88** |
| KaTeX errors | **0** |
| Confirmed prose content losses | **0** |

Both remaining build warnings are kept deliberately: two `\paragraph` commands are preserved as depth-4 headings without a depth-3 parent (`sec-irbc_fischer_burmeister` in ch03, `sec-matern` in ch09). Suppressing the warning would mean dropping content the PDF shows.

Content converted: 88 `{figure}`, 87 `{exercise}`, 57 `{prf:remark}`, 46 tables, 159 `{math}`, 14 `{prf:definition}`, 5 `{code-block}`, 3 `{prf:algorithm}`, across 23 pages (5 front matter, 12 chapters, 6 appendices). All 88 figures render, including 78 TikZ diagrams compiled to SVG by [`scripts/render_tikz.py`](scripts/render_tikz.py).

## How numbering was checked

Numbering is where a conversion most easily drifts unnoticed, because nothing errors — the page simply disagrees with the book.

**Equations.** Every numbered equation in the built document was compared *positionally* against the printed PDF, chapter by chapter, not merely counted. An earlier round found a genuine 265-vs-272 discrepancy: multi-row `align` environments were collapsing to a single number, while ch11 over-numbered in the other direction because `\tag*`-named loss components were being numbered where the PDF leaves them bare. Both directions are fixed and the output now matches the PDF exactly.

**Sections.** The PDF's table of contents yields 131 numbered entries. 127 match a heading by title, and all 127 carry the same number. The 4 unmatched are artefacts of parsing the TOC's dot leaders, not missing sections.

**Unnumbered sections.** `\section*` is unnumbered in LaTeX. All 24 starred sections — `Further Reading`, `Exercises`, and ch03's `Validation Protocol` — render without a number and without advancing the section counter, matching the PDF.

## How content fidelity was checked

Structural counts prove nothing about prose, so the text was compared directly against the printed book.

**Method.** Extract the 331-page PDF with `pdftotext`. For every sentence, take the longest run of consecutive plain words — ASCII letters only, three or more characters, which excludes maths variables and reference numbers — keep runs of eight words or more, and test whether that run appears in the *rendered HTML*. Both sides are normalised to `[a-z0-9]`, so hyphenation, line-break joins, smart quotes and markup cannot cause a false mismatch.

**Result.** 2,223 sentences were testable — **39% of the book** — and every one was tested rather than sampled. 2,096 matched verbatim. All 127 remaining were triaged and explained: 124 are artefacts of the comparison itself (citations are stored as `{cite:t}` roles and maths as LaTeX, so the printed glyphs cannot match — and none of those 124 match their own LaTeX source either, which is what proves the fault is the method rather than the conversion), and 3 are runs that ended inside maths whose interior fragment does render.

**Zero confirmed content losses remain.** The census found two real gaps, both since fixed: the Abstract page and epigraph were absent — they sit before the first `\chapter`, outside the converter's declared scope, and are now carried on the landing page — and one figure lost its legend, because `fig:attention` pairs a TikZ diagram with a sibling `minipage` and the figure override replaced both.

**What this does not cover.** The other 61% of sentences — too short or too maths-dense to compare as text — rest on the structural gates above rather than on direct comparison. Two traps are worth recording for anyone repeating the exercise: compare against the *rendered HTML* and not the markdown, because cross-references, citations and the deliberate doubled-noun strips only materialise at render time; and strip KaTeX's MathML subtree first, or every symbol appears twice and breaks any run crossing inline maths.

## Accepted differences from the PDF

Internally consistent in both outputs, and not defects:

| | Printed PDF | MyST |
|---|---|---|
| Algorithm numbering | global (`Algorithm 1`) | per chapter (`Algorithm 6.1`) |
| Exercise numbering | chapter-local (`Exercise 3`) | chapter-prefixed (`Exercise 9.7`) |
| Remark boxes | unnumbered coloured boxes | numbered (`Remark N.M`) |
| Table captions | below the table | above |
| Citations | `Author and Author, 2018` | `Author & Author, 2018` |

## Known follow-ups

None blocks use of the rendering.

- **Ten enumerate markers are escaped as literal text** (`(a)`, `(i)`, …) in `appF_solutions.md` and `ch02_deqns.md`. The stock MyST book theme drops the `style` and `delimiter` attributes on fancy ordered lists and would render them `1./2./3.`, losing the labels entirely. Tracked as [QuantEcon/mystmd#74](https://github.com/QuantEcon/mystmd/issues/74); the escape is dropped once a theme honouring those attributes is adopted.
- **One figure legend is carried in its caption** rather than beside the diagram (`fig:attention`, ch01), because the figure override replaces the whole `figure` environment. Of 88 figures only this one has that structure, so a general fix was not judged worthwhile on the evidence.
- **`config.yaml` carries nine local `postprocess.rewrites`.** Each is documented in place with the upstream issue it waits on. Five earlier ones have already been retired as fixes landed upstream, which is the intended direction of travel.
