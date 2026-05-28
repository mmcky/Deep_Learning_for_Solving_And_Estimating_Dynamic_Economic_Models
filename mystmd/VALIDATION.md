# MyST conversion — VALIDATION report

**Scope:** structural counts + targeted spot-checks of the MyST/HTML build against the LaTeX source and rendered PDF.
**Initial validation:** 2026-05-24 (commit `a26cddc`).
**Round 2 update:** 2026-05-25 — re-tally after upstream landed fixes for issues #30–#33.
**Round 3 update:** 2026-05-25 — re-tally after upstream landed fixes for follow-ups #35, #36, #37.
**Round 4 update:** 2026-05-25 — drill into deferred items; 2 new bugs filed (#39 algorithm label, #40 HTML entity in math); 2 prior "gaps" resolved as counting artifacts.
**Round 5 update:** 2026-05-25 — re-tally after upstream landed fixes for #38, #39, #40 *and* a major refactor (P3a series, 11 commits) splitting `postprocess.py` into a `transforms/` package. #38 and #40 work; #39 only partially (filed [#43](https://github.com/QuantEcon/claude-latex-to-myst/issues/43)). The P3a refactor introduced a critical regression: module double-load drops `TIKZ_FIGURE_MAP` content silently, breaking **all 88 figures** ([#42](https://github.com/QuantEcon/claude-latex-to-myst/issues/42) filed). Round 4 also under-reported KaTeX warnings — re-grep surfaces 9 pre-existing instances of `\,^\circ` and `\tag*` patterns that KaTeX can't handle (not a refactor regression).
**Round 6 update:** 2026-05-25 — #42 closed with the `sys.modules['postprocess']` aliasing fix (option B from the proposal). Re-tally: **all 88 figures restored**, all cross-ref classes resolve cleanly, citations clean. The fix is generic — every `transforms/` module that late-imports `postprocess` for state now resolves to the same instance, closing the whole class of bugs at once.
**Round 7 update:** 2026-05-27 — re-tally after fast-forward from `0e88cab` → `9649b0b` (six new commits, including #51/#55/#60 table unification, #49 nested-subfigure fast path, #50/#22 dropped-text-macro warner, #54 longtable extraction, and #63 `regen: false`). Headline wins: **all 41 captioned tables now render as `{table}` directives** (R6: 4 list-tables, 37 anchors-only) — issue #34 fully closed end-to-end. Headline gap: a methodology defect was discovered — **`validate.py` has been silently skipping every chapter in this book since R1**, because it looks for split-source `.tex` files in `lecture_script/` (which only ships the monolithic file; split outputs live in `mystmd/tmp/`). Building the html surfaces what `validate.py` missed: 96 unresolved `{prf:ref}\`ex-chN-M\`` exercise refs (labels inside `\item\label{ex:ch1:1}` are dropped by pandoc), 15 per-row `\label{}` collisions on `\begin{align}` blocks that MyST collapses to one anchor, and the 3rd algorithm renders as `{prf:definition}` because its source wrapper is `\begin{definitionbox}[Algorithm: …]` rather than `\begin{algorithm}`. None of these were introduced by R7 upstream — they are pre-existing, only newly visible. Five issues filed: upstream #68 (validate.py no-op), #69 (exercise labels), #70 (align collisions), #71 (lstlisting caption escapes); downstream book #13 (source fixes) + #14 (missing assets).
**Round 8 update:** 2026-05-28 — re-tally after fast-forward `9649b0b` → `94baac5` (seven new commits). **All four R7-filed upstream issues landed**: #68 (`291497c` — validate.py tmp_dir fallback, now actually runs), #69 (`cd7a0f9` — `\item\label{ex:…}` → `{exercise}` directive), #70 (`4d02d3f` — per-row align split into separate `$$` blocks), #71 (`fcba7b0` — lstlisting caption escape decode). Result, measured from the **now-working** `validate.py` and the build log: **0 unresolved cross-references** (was 106), **0 empty cross-refs** (was 129), **0 label collisions** (was 15), **0 KaTeX errors** (was 10). The 96 exercise back-refs in appF all resolve — exercises now render as 87 `{exercise}` directives. The last KaTeX failures were the 8 `\,^\circ` degree-symbol instances (upstream #45, still open / "possibly KaTeX upstream"); cleared with a local `preprocess.rewrites` stopgap (`\,^\circ` → `\,{}^\circ`). Remaining non-cosmetic items are all source-side and already tracked downstream: `alg-nsdeqn` still renders as Definition (book #13 — upstream #79's `prf:algorithm` generalisation doesn't catch it because our config maps `definitionbox`→`prf:definition`), 2 citation false-positives (`unil` mailto + `@tf.function`, book #13), 2 missing `restud_fig*.pdf` assets (book #14). **The MyST build is now structurally clean.**
**Round 9 update:** 2026-05-28 — re-tally after fast-forward `94baac5` → `0c41795` (two new commits). #45 (degree-symbol) landed upstream (`0c41795`, generic `fix_spacing_superscript` transform). #52 (nested-list-table numref drift) landed too (`ef0acf4` — touched 1 `{list-table}` in ch06_ha_youngs, adding `:enumerated: false` to suppress drift; the other 2 `{list-table}` directives unchanged). Initially removed the local `\,^\circ` stopgap on the assumption #45 covered it; build re-introduced **2 KaTeX errors in ch11 table cells** — the upstream fix stashes ALL backtick-fenced regions (including `{table}` directives, which are 4-backtick fences) before applying the rewrite, so math inside table cells is skipped. Filed regression as [QE#85](https://github.com/QuantEcon/claude-latex-to-myst/issues/85) with a proposed fix (distinguish directive fences from plain code fences) and **restored the local stopgap** in `mystmd/config.yaml`. Because the stopgap runs at *preprocess* on the source `.tex` (before pandoc, before any markdown fence exists), it catches all 8 instances regardless of where they end up. Build state matches R8: **0 unresolved cross-refs, 0 KaTeX errors, 0 label collisions.**
**Round 11 update:** 2026-05-28 — fast-forward `0c41795` → `43565a4` ([QE#88](https://github.com/QuantEcon/claude-latex-to-myst/pull/88) merged, closing [QE#87](https://github.com/QuantEcon/claude-latex-to-myst/issues/87)). The upstream rebuilt `fix_spacing_superscript` as a line-based state machine — no more regex fence-pairing, no more stash/restore step. Result: structurally eliminates the whole class of fence-pairing bugs that produced #84/#85/#86/#87. Verified end-to-end against this book WITH the local `\,^\circ` stopgap **removed**: 0 KaTeX errors, 0 FSS marker leaks, 0 content loss, all 8 `\,^\circ` + 1 `\,^{\circ}` source instances rewritten to `\,{}^\circ` / `\,{}^{\circ}`, ch03's Fischer–Burmeister `{code-block}` intact. The local `preprocess.rewrites` stopgap that lived in `mystmd/config.yaml` from R8 through R10 has been **deleted** — the entire degree-symbol handling now lives durably upstream. Net build state: **0 unresolved cross-refs, 0 KaTeX errors, 0 label collisions, no content loss**. Remaining items unchanged: 2 citation false-positives (book #13), 2 missing image assets (book #14), `alg-nsdeqn` still renders as Definition (book #13) — all source-side.
**Round 12 update:** 2026-05-28 — fidelity walkthrough. R7–R11 measured structural counts and resolved every cross-reference, but the methodology was blind to a class of *content drops where pandoc removes a LaTeX construct and leaves the surrounding prose intact*. A source-vs-MD parallel read across all 22 chapters surfaced **~100 hidden artifacts in 5 classes**: (A) `\pageref{}` hangs leave `(statement: p.<NBSP>):` / `on page<NBSP>.` (~81 instances, appF + ch01); (B) `\citet{}` inside figure `\caption{}` silently dropped → `architecture of .`, `reported by .` (8 figure captions, ch07 + ch11); (C) `{\footnotesize …}` sub-captions inside `\begin{figure}\begin{minipage}` dropped (5 instances, ch02 + ch06 — incl. the ch06 verification line first noted at R7); (D) `\textcolor{…}{TEXT}` macros leak raw into the alg-nsdeqn body (5 instances, ch11); (E) `\hspace{…}` / `\protect\texttt{…}` leaks (2 instances). **Three classes (A, D, E) fixed locally** via `postprocess.rewrites` — ~95 artifacts cleared. **Two classes (B, C) filed upstream** as [QE#89](https://github.com/QuantEcon/claude-latex-to-myst/issues/89) (figure-caption cite drop) and [QE#90](https://github.com/QuantEcon/claude-latex-to-myst/issues/90) (figure-internal text drop) — both need converter-side fixes since the content is gone after pandoc and can't be recovered downstream. Build remains clean: **0 unresolved cross-refs, 0 KaTeX errors, 0 label collisions, ~13 remaining hidden artifacts** (8 figure-caption cites + 5 sub-captions), all awaiting upstream.
**Round 13 update:** 2026-05-28 — fast-forward `43565a4` → `b79df24` ([QE#91](https://github.com/QuantEcon/claude-latex-to-myst/pull/91) merged, closing R12-filed [#89](https://github.com/QuantEcon/claude-latex-to-myst/issues/89) and [#90](https://github.com/QuantEcon/claude-latex-to-myst/issues/90)). **Class B (figure-caption `\citet` cites) fully recovered** — 0 hanging "of .", "by .", "from ." artifacts remain across all 22 chapters; e.g. ch07 DGM caption now correctly reads "architecture of {cite:t}\`sirignano2018dgm\`". **Class C (sub-caption content) partially recovered**: 4 of 5 minipage-wrapped cases now appear in the figure caption text (ch02 ×4). Two new issues surfaced and filed: [QE#92](https://github.com/QuantEcon/claude-latex-to-myst/issues/92) — `\citep{}` (parenthetical natbib) was missed by #91, leaking 5 `[[CITEP:key]]` markers verbatim into the rendered HTML (ch01 ×2, ch02, ch04 ×2); [QE#93](https://github.com/QuantEcon/claude-latex-to-myst/issues/93) — the ch06 "Verification" line is still dropped because that figure uses bare `\begin{figure}\begin{tikzpicture}…\end{tikzpicture}{\footnotesize …}\caption{…}\end{figure}` without a minipage wrapper, and #91's recovery only targeted the minipage shape. Both filed at upstream; the `[[CITEP:…]]` regression in particular needs a fix before the round can be called clean. Build still passes all R7–R12 structural checks: **0 unresolved cross-refs, 0 KaTeX errors, 0 label collisions, all 5 R12 local rewrites still active.**
**Round 14 update:** 2026-05-28 — attempted fast-forward `b79df24` → `e7a28db` ([QE#95](https://github.com/QuantEcon/claude-latex-to-myst/pull/95), the "figures: marker preprocessor (Phase 1)" PR closing R13-filed #92 and #93). The R14 pin **reverted to R13's `b79df24`** after the new commit was found to drop the image source from **78 of 88 figures** in this book — TikZ-bodied figures that previously rendered as `{figure} figures/fig-X.svg` (via `tikz_overrides.py`) now come out as text-only `{admonition} Figure` directives with no image at all. Verified: built JSON image-node count drops from 88 (R13) → 10 (R14-attempt). The four issues #95 was filed to close (#89/#90/#92/#93) are all genuinely resolved by the patch — captions, sub-captions, `\citet`, `\citep`, ch06 Verification line all clean — but the new Phase 1 preprocessor short-circuits the post-pandoc TikZ → image-path lookup that `tikz_overrides.py` provides, so any book using rendered-TikZ figures sees most of its figures vanish. Filed as [QE#96](https://github.com/QuantEcon/claude-latex-to-myst/issues/96) with reproducer + proposed fix. **Pin held at `b79df24` (R13)** — the 6 known R13 residuals (5 `[[CITEP:…]]` leaks + 1 ch06 Verification line) are *much* less bad than losing 78 figure images. Will re-attempt the fast-forward once #96 lands a Phase 2 that restores the TikZ image-mapping. Build state unchanged from R13: **0 unresolved cross-refs, 0 KaTeX errors, 0 label collisions, 88/88 figures rendering**.
**Round 15 update:** 2026-05-28 — fast-forward `b79df24` → `ae466b8` ([QE#97](https://github.com/QuantEcon/claude-latex-to-myst/pull/97) merged, closing R14-filed [QE#96](https://github.com/QuantEcon/claude-latex-to-myst/issues/96)). Phase 2 restores `TIKZ_FIGURE_MAP` integration in `resolve_figure_markers`, so this commit safely brings in the four Phase 1 fixes for #89/#90/#92/#93 without sacrificing the 78 TikZ-rendered figures. **First round where every previously-tracked upstream issue is closed AND every R12 hidden-artifact class is cleared end-to-end.** Verified: 88/88 figures rendering (`{figure}` directives with images, 88 image nodes in built JSON); 0 `[[CITEP:…]]` marker leaks; ch06 Verification line recovered; 0 hanging caption-cite drops; all 5 R12 local `postprocess.rewrites` still clean and idempotent with the upstream changes. Build is the cleanest it's been: **0 unresolved cross-refs, 0 KaTeX errors, 0 label collisions, no marker leaks, no image losses.** Remaining items are entirely source-side and tracked downstream: 2 citation false-positives (book #13), 2 missing reproduced-from-paper PDFs (book #14). At this point the conversion-side of the pipeline has no outstanding issues against this book.

**Round 10 update:** 2026-05-28 — attempted fast-forward `0c41795` → `3d0d797` (one new commit closing the R9-filed [QE#85](https://github.com/QuantEcon/claude-latex-to-myst/issues/85)). The R10 pin point **reverted to R9's `0c41795`** after discovering a second regression that is much more severe than the first. Two cascading bugs in the `3d0d797` fix:
1. Phantom-fence pairing (same class as QE#85): the closing `` ``` `` of a `{figure}` directive (3-backtick fence) is treated by `_PLAIN_FENCED_CODE_RE` as the opener of a new plain code fence; the regex pairs it with the next bare `` ``` `` it finds (often another figure's closer many paragraphs down), exempting everything in between from the `\,^X` rewrite. 3 KaTeX errors return on stopgap-removed test (including prose, not just table cells).
2. Stash-restoration collision (worse — **content-loss**): when `_PLAIN_FENCED_CODE_RE`'s phantom region contains an earlier `_CODE_DIRECTIVE_FENCE_RE` stash marker (`\x00FSS0\x00`), the outer stash captures the marker. Forward-order restoration then runs FSS0 first (no-op — marker is hidden inside FSS1's value), then FSS1 (reintroducing the literal `\x00FSS0\x00`). The loop ends with FSS0 visible and unrestored. In ch03_irbc.md this silently destroyed a `{code-block}` directive (Fischer–Burmeister smoothing listing) — literal `FSS0` shows up where the code listing should be. Filed as a comment on [QE#87](https://github.com/QuantEcon/claude-latex-to-myst/issues/87) with a two-part fix proposal (stateful fence-scan + reverse-order restoration). Both bugs originate in the same place; either fix alone closes this book's regression.

**Pin held at `0c41795` for R10**: same clean build state as R9 (0 unresolved cross-refs, 0 KaTeX errors, 0 label collisions, no content loss). The book-side `\,^\circ` `preprocess.rewrites` stopgap stays in place — it remains the source of cleanliness for the 8 degree-symbol instances. Will re-attempt the upstream fast-forward once QE#87 lands and a verification build comes through clean against this book.
**Branch:** `mystmd-conversion`
**Sources:**
- `lecture_script/Deep_Learning_for_Solving_And_Estimating_Dynamic_Economic_Models.tex` (24,557 source lines, 329-page PDF)
- `mystmd/*.md` (23 converted files: 12 chapters + 6 appendices + 5 frontmatter)
- `mystmd/_build/` (post `myst build --html`)
- `readings/bibliography.bib` (278 entries)
- `mystmd/myst.yml`, `mystmd/config.yaml`, `mystmd/tikz_overrides.py`

**Methodology (what this report does and doesn't do):** structural counts compare totals between source and output; per-anchor cross-ref checks identify broken references; spot-checks compare 2 PDF pages (ch01 §1.6 and ch11 §11.12) side-by-side with the converted markdown. This report does **not** do a full paragraph-level content diff — that would be infeasible at this scale. The goal is to give bounded confidence that the conversion is structurally faithful and to enumerate any remaining gaps with concrete examples.

---

## 1. Headline result (Round 15)

Upstream pin: `ae466b8` (fast-forward from `b79df24` — Phase 1 [QE#95](https://github.com/QuantEcon/claude-latex-to-myst/pull/95) + Phase 2 [QE#97](https://github.com/QuantEcon/claude-latex-to-myst/pull/97), the latter closing R14-filed [QE#96](https://github.com/QuantEcon/claude-latex-to-myst/issues/96)).

**First round where every previously-tracked upstream issue is closed AND every R12 hidden-artifact class is cleared end-to-end:**

| Class | R12 | R13 | R14-attempt | R15 |
|---|---|---|---|---|
| Class B (figure-caption `\citet` cites) | 8 hangs | 0 ✅ | 0 ✅ | 0 ✅ |
| Class C (sub-captions) | 5 dropped | 4 of 5 ✅ | 5 of 5 ✅ | **5 of 5 ✅** |
| `[[CITEP:…]]` marker leaks | n/a | 5 ❌ | 0 ✅ | **0 ✅** |
| ch06 Verification line | dropped | dropped | recovered ✅ | **recovered ✅** |
| Figures rendering as `{figure}` (with images) | 88 | 88 | 10 ❌ | **88 ✅** |
| `[[CITET:…]]` leaks / unresolved refs / label collisions / KaTeX errors | 0 | 0 | 0 | **0 ✅** |
| Local R12 rewrites (A pageref, D textcolor, E hspace/protect) | active | active | active | **active ✅** |

**Build is the cleanest it's been**: 88/88 figures rendering with images, 0 unresolved cross-refs, 0 KaTeX errors, 0 label collisions, no marker leaks, no content drops. The conversion-side of the pipeline has no outstanding issues against this book.

**Remaining items are entirely source-side**, tracked downstream: 2 citation false-positives (`unil` mailto + `@tf.function` decorator — [book#13](https://github.com/mmcky/Deep_Learning_for_Solving_And_Estimating_Dynamic_Economic_Models/issues/13)), 2 missing reproduced-from-paper PDFs (book#14), `alg-nsdeqn` renders as Definition not Algorithm (book#13). Plus cosmetic warnings: 15 "missing heading depth" (source skips a heading level), 2 "Duplicate identifier" (repeated `Exercises` / `Further Reading` section anchors) — neither affects rendered content.

## 1.0 Headline result (Round 14, preserved)

Upstream pin: **held at `b79df24`** (R13) after a test fast-forward to `e7a28db` ([QE#95](https://github.com/QuantEcon/claude-latex-to-myst/pull/95)) revealed that the new "figures: marker preprocessor (Phase 1)" closes the four R12/R13-filed caption issues but **drops the image source from 78 of 88 figures** — TikZ-bodied figures that this book ships via `tikz_overrides.py` come out as text-only `{admonition} Figure` directives. Built JSON image-node count: **88 → 10**. Filed as [QE#96](https://github.com/QuantEcon/claude-latex-to-myst/issues/96); accepting R13's known residuals (5 `[[CITEP:…]]` leaks + 1 ch06 Verification line) is significantly less bad. Will re-attempt the fast-forward when #96's Phase 2 restores the TikZ image-mapping. **Build state unchanged from R13: 88/88 figures rendering, 0 unresolved cross-refs, 0 KaTeX errors, 0 label collisions.**

## 1.0 Headline result (Round 13, preserved)

Upstream pin: `b79df24` (fast-forward from `43565a4`, one commit — [QE#91](https://github.com/QuantEcon/claude-latex-to-myst/pull/91) closing R12-filed [#89](https://github.com/QuantEcon/claude-latex-to-myst/issues/89) and [#90](https://github.com/QuantEcon/claude-latex-to-myst/issues/90)).

**Net for R13:** Class B (figure-caption `\citet`) **fully recovered** — 0 hanging "of .", "by .", "from ." artifacts in any chapter. Class C (sub-captions inside `\begin{minipage}`) recovered for 4 of 5 sites; the ch06 case still drops because that figure uses no minipage wrapper. **Two new issues surfaced** in the upstream patch: [QE#92](https://github.com/QuantEcon/claude-latex-to-myst/issues/92) — `\citep{}` was missed by #91 and leaks as 5 `[[CITEP:key]]` markers in rendered HTML; [QE#93](https://github.com/QuantEcon/claude-latex-to-myst/issues/93) — bare `\begin{figure}…{\footnotesize}…\caption` (no minipage) still drops (ch06 Verification line).

**Build state still clean: 0 unresolved cross-refs, 0 KaTeX errors, 0 label collisions, no marker leaks from the R12 local rewrites (A, D, E).** Net hidden-artifact count: ~6 remaining (5 `[[CITEP:…]]` leaks + 1 ch06 Verification line), all awaiting upstream — down from ~13 at R12.

## 1.0 Headline result (Round 12, preserved)

R12 was a **fidelity walkthrough** rather than another upstream bump — comparing source LaTeX to MyST markdown chapter-by-chapter to catch any content drops that the structural validator was blind to.

The structural validation in R7–R11 always passed (every count matched, every cross-reference resolved), but a parallel source/MD read across all 22 chapters surfaced 5 distinct patterns of *hidden content drops where pandoc removes a LaTeX construct and leaves the surrounding prose intact*. ~100 visible artifacts in total. **~95 of those cleared in this commit** via 5 new `postprocess.rewrites` rules in `mystmd/config.yaml` (Classes A, D, E in §1.2 below). The remaining ~13 (Classes B and C — figure-caption cite drops, multi-panel sub-caption drops) are filed upstream as [QE#89](https://github.com/QuantEcon/claude-latex-to-myst/issues/89) and [QE#90](https://github.com/QuantEcon/claude-latex-to-myst/issues/90); they can't be recovered downstream once pandoc has consumed the source.

**Build remains structurally clean: 0 unresolved cross-refs, 0 KaTeX errors, 0 label collisions, no marker leaks.**

### 1.2 R12 fidelity findings — pattern table

| Class | Pattern | Count | Status |
|---|---|---|---|
| A | `\pageref{}` hangs: `(statement: p.<NBSP>):` (appF) + `on page<NBSP>.` (body) | 81 | ✅ cleared (postprocess.rewrites) |
| B | `\citet{}` inside figure `\caption{}` dropped → `architecture of .`, `reported by .`, etc. | 8 | ⏳ [QE#89](https://github.com/QuantEcon/claude-latex-to-myst/issues/89) (upstream) |
| C | `{\footnotesize …}` sub-captions inside `\begin{figure}\begin{minipage}…\end{tikzpicture}{\footnotesize …}\end{minipage}` dropped | 5 (4 ch02 + 1 ch06) | ⏳ [QE#90](https://github.com/QuantEcon/claude-latex-to-myst/issues/90) (upstream) |
| D | `\textcolor{COLOR}{TEXT}` macros leak raw into alg-nsdeqn body | 5 (ch11) | ✅ cleared (postprocess.rewrites — keeps TEXT, drops color) |
| E.1 | `\hspace{…}` leak (1 instance, alg-nsdeqn) | 1 | ✅ cleared (postprocess.rewrites) |
| E.2 | `\protect\texttt{…}` compound leak (1 instance, ch02 lstlisting caption) | 1 | ✅ cleared (postprocess.rewrites — narrow match preserves bare `\texttt{}` inside math) |

The methodology gap that hid these from R7–R11: the validator counts headings, figures, tables, citations, refs — all of which round-trip cleanly. But none of those counts catch "the caption text says `of .` because a cite was silently dropped from inside it." The R12 walkthrough specifically targets this class — patterns where the *count of preserved structure stays correct* but the *rendered prose has a hole in it*.

| Dimension | Source | MyST | R11 | R10 | R9 | R8 | R7 | R6 | R5 | R1 |
|---|---|---|---|---|---|---|---|---|---|---|
| Chapters / sections / subsections / subsubsections | 22/144/81/5 | 22/144/81/5 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Paragraph heads / footnotes | 385 / 24 | 385 / 24 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ⚠️ |
| Figures rendered | 88 | 88 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ #42 | ✅ |
| Captioned tables — `{table}` directives / anchors | 41 / 41 | 41 / 41 | ✅ | ✅ | ✅ | ✅ | ✅ | ⚠️ #34 | ⚠️ | ⚠️ |
| Exercises → `{exercise}` directives w/ labels | 87 labels | 87 directives, all refs resolve | ✅ | ✅ | ✅ | ✅ | ❌ 96 broken | (masked) | (masked) | (masked) |
| `\label{alg:X}` → `{prf:algorithm}` round-trip | 3 labels | 2 of 3 (alg-nsdeqn → `prf:definition`; book #13) | ⚠️ same | ⚠️ same | ⚠️ same | ⚠️ same | ⚠️ | ⚠️ #43 | ⚠️ #39 | n/a |
| `{numref}` cross-ref targets | — | all resolve | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `{ref}` cross-ref targets | — | all resolve | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ⚠️ 11 | — |
| `{eq}` cross-ref targets | — | all resolve (per-row align split, #70) | ✅ | ✅ | ✅ | ✅ | ⚠️ 15 collisions | ✅ | ✅ | — |
| `{prf:ref}` to exercises | 87 | all resolve (#69) | ✅ | ✅ | ✅ | ✅ | ❌ 96 broken | (masked) | (masked) | (masked) |
| Citation keys vs `references.bib` | 254 | all resolve except `unil`, `tf.function` (book #13) | ⚠️ 2 src | ⚠️ 2 src | ⚠️ 2 src | ⚠️ 2 | ⚠️ 2 | ✅ | ✅ | — |
| KaTeX build errors (`⛔`) | — | **0** (R11: entirely handled by upstream `fix_spacing_superscript` state machine, [QE#88](https://github.com/QuantEcon/claude-latex-to-myst/pull/88); local stopgap removed) | ✅ | ✅ | ✅ | ✅ | ⚠️ 10 | ⚠️ | ⚠️ | n/a |
| Content-loss (`\x00FSS*\x00` marker leaks) | — | 0 across all .md | ✅ | ✅ | ✅ | ✅ | (n/a) | (n/a) | (n/a) | n/a |
| Missing image files (`fig/restud_fig{11a,15a}.pdf`) | 2 refs | still absent (book #14) | ⚠️ asset | ⚠️ asset | ⚠️ asset | ⚠️ asset | ⚠️ | (missed) | (missed) | n/a |
| `Could not convert TeX math` (pandoc macro coverage) | — | ~22 (render fine via `myst.yml`) | ℹ️ noise | ℹ️ noise | ℹ️ noise | ℹ️ noise | ⚠️ | (missed) | (missed) | n/a |

**Round 11 verdict — first round where every transform lives upstream; local KaTeX stopgap deleted.**

Upstream [QE#88](https://github.com/QuantEcon/claude-latex-to-myst/pull/88) merged the state-machine rebuild we test-verified at R10 ([comment](https://github.com/QuantEcon/claude-latex-to-myst/pull/88#issuecomment-4561019390)). The new `fix_spacing_superscript`:

- Walks the markdown line-by-line with an explicit fence stack — closers are identified by the stack, not by another regex match.
- No stash/restore step → marker-leak content-loss class is structurally impossible.
- Nesting (e.g. `{code-block}` inside `{exercise}`) handled by construction.
- Adding a new directive emitter in future = one entry in `_CODE_DIRECTIVE_NAMES` or zero changes.

Verified end-to-end against this book with the local `\,^\circ` stopgap **removed**:
- 0 KaTeX errors (was 3 at R10-attempt)
- 0 `\x00FSS*\x00` marker leaks across all `.md` (was 1 destroyed `{code-block}` at R10-attempt)
- ch03 Fischer–Burmeister `{code-block}` intact
- All 8 `\,^\circ` + 1 `\,^{\circ}` source instances rewritten

The local `preprocess.rewrites` stopgap (lived in `mystmd/config.yaml` from R8 through R10) **deleted** in this commit. First round where every transform in this book's MyST pipeline lives upstream.

**Round 10 verdict — no observable change vs R9; second upstream regression filed, local stopgap stays.**

The one upstream commit since R9 (`3d0d797`) closes [QE#85](https://github.com/QuantEcon/claude-latex-to-myst/issues/85) — the R9 follow-up against the original #45 fix. The strategy was a sound one (move `fix_spacing_superscript` AFTER the marker decoders so it sees the decoded `{table}` cell content), but it introduced a *new* fence-stashing edge case:
- The closing `` ``` `` of a 3-backtick `{figure}` directive is treated by `_PLAIN_FENCED_CODE_RE` as a phantom opener of a new plain code fence; the regex then pairs it with the next bare `` ``` `` (often the closing of another `{figure}` many paragraphs later), and silently stashes everything in between from the rewrite.
- Verified by removing the local stopgap: **3 KaTeX errors return** — surprisingly including line 247 in *prose* (not just table cells), because the phantom region opened by ch11:229's `{figure}` closer extends through dozens of paragraphs and table directives. Filed as [QE#87](https://github.com/QuantEcon/claude-latex-to-myst/issues/87) with a proposed stateful-scan fix (Markdown fence pairing is intrinsically recursive — a regex-only solution can't disambiguate openers from closers).

**Round 9 verdict — no observable change vs R8; first upstream regression filed, local stopgap stays.**

The two upstream commits since R8 (`0c41795` and `ef0acf4`) close #45 and #52 respectively. Neither moves this book's build state:
- **#45 (degree-symbol)** — the upstream `fix_spacing_superscript` transform stashes ALL backtick-fenced regions (including `{table}` directives, which use 4-backtick fences) before applying the `\,^X` → `\,{}^X` rewrite. So math inside table cells is exempted from the fix. Verified by removing the local stopgap: 2 KaTeX errors reappeared, both in ch11 `{table}` cells (`$\approx 3.25\,^\circ$C`, `$(1.10, 0.27)\,^\circ$C`). Filed as [QE#85](https://github.com/QuantEcon/claude-latex-to-myst/issues/85) with a proposed fix (carve out directive fences `` ```{name} `` from the stash; the original protect-target was plain code fences). Local stopgap restored and updated with a comment pointing at #85.
- **#52 (nested-list-table numref drift)** — added `:enumerated: false` to one `{list-table}` in ch06_ha_youngs (a comparison table nested inside a list). Cosmetic improvement; no broken refs in this book either way.

Action plan: keep the local `\,^\circ` preprocess.rewrites entry in place until [QE#87](https://github.com/QuantEcon/claude-latex-to-myst/issues/87) lands (and verifies clean against this book's corpus, since this is now the second time an upstream fix has appeared to close the issue while leaving residual instances unfixed). It runs at preprocess on the source `.tex` before any markdown fence exists, so it's robust against both R9 (4-backtick `{table}` stash) and R10 (phantom closing-fence pairing) classes of regression.

**Round 8 verdict — clean build; all R7-filed upstream issues closed.**

✅ **Closed by this round's upstream (R8):**
- **#68 (`291497c`) — `validate.py` no longer no-ops.** It now falls back to `tmp_dir` for split-source per-stem `.tex` files and guards against the vacuous pass. The validator runs for real for the first time on this book (see §1.1 on the count-mismatch `!` marks it now surfaces — they're tallying artifacts, not breakage).
- **#69 (`cd7a0f9`) — `\item\label{ex:…}` exercises promoted to `{exercise}` directives.** 87 directives emitted, each with its `:label:`. All 96 previously-dead `{prf:ref}` from appF now resolve; the Solutions appendix is fully linked.
- **#70 (`4d02d3f`) — per-row align labels split into separate `$$` blocks.** The 15 label collisions and 10 dead `{eq}` refs are gone; the `Multiple \tag` KaTeX error went with them.
- **#71 (`fcba7b0`) — lstlisting caption escape decode.** The ch02 `K^\\alpha` double-backslash is fixed (`K^\alpha`), clearing that KaTeX error.

✅ **Cleared locally this round:**
- **#45 (degree symbol, still open upstream)** — 8 `\,^\circ\mathrm{C}` instances broke KaTeX (`Got group of unknown type: 'internal'`). Added a `preprocess.rewrites` stopgap `\,^\circ` → `\,{}^\circ` (empty group gives the superscript a base). Build is now KaTeX-clean. Remove the stopgap when #45 lands a generic KaTeX-compat fix upstream.

⚠️ **Remaining items — all source-side, all tracked downstream, none blocking:**
- `alg-nsdeqn` renders as Definition not Algorithm (book #13). Upstream #79 generalised `prf:algorithm` routing but doesn't catch this case because our `config.yaml::extra_environments` maps `definitionbox`→`prf:definition`. One-line source fix (`\begin{algorithm}`) resolves it; the cross-ref already resolves, so this is cosmetic.
- 2 citation false-positives: `unil` (a `\href{mailto:…@unil.ch}` mis-read as a cite) and `@tf.function` (Python decorator). Both in book #13.
- 2 missing `restud_fig{11a,15a}.pdf` assets (book #14) — needs author decision.

ℹ️ **Cosmetic build warnings (unchanged, not content):** 15 "missing heading depth" (source skips a heading level, e.g. `##` → `####`), 2 "Duplicate identifier" (every chapter has an `Exercises` / `Further Reading` section sharing an auto-id). Neither affects rendered content.

### 1.1 On the validate.py count-mismatch (`!`) marks

Now that #68 lets `validate.py` run, it prints per-chapter `latex/myst` counts and flags totals that differ with `!`. These are **tallying-heuristic differences, not broken output** — the resolution check (does every referenced anchor exist?) passes with the single exception of `unil`. Specifically:
- **equations** `latex < myst` (e.g. ch11 59/72): #70 now splits each per-row-labelled align row into its own `$$` block, so MyST legitimately has more equation blocks than the source has `\label{eq:}` lines.
- **citations** `latex < myst` (e.g. ch01 61/127): the MyST side counts every `{cite:*}` occurrence including multi-key `{cite:p}\`a,b,c\`` expansions and repeated cites; the LaTeX side counts `\cite*` calls. Different denominators.
- **theorems** `0/N`: source has 0 by the validator's `\begin{theorem}`-family heuristic; MyST has `{prf:remark}` / `{prf:definition}` from the book's tcolorbox→prf mappings.
- **cross_refs / notation** `latex < myst`: numref/eq expansion and the notation symbol-table anchors.

None of these indicate missing or mis-converted content; they're a known limitation of comparing structural totals across two different markup models.

---

## 2. Structural counts

### 2.1 Source (LaTeX)

```
chapters (\chapter*):              22       — 4 frontmatter, 12 numbered, 6 appendices
sections:                         144
subsections:                       81
subsubsections:                     5
paragraphs (\paragraph):          385
footnotes (\footnote):             18

figures (\begin{figure}):          88
  - inline \begin{tikzpicture}:    82
  - \includegraphics references:   11   (10 unique, 1 hero/title)

tables:
  - \begin{tabular}:               52
  - \begin{table} floats:          41   (38 with \caption + \label)

equations:
  - \begin{equation}:             228
  - \begin{align} / \align*:       37
  - \begin{multline}:               1
  - \[ … \] (display math):       142
  - total math blocks (approx):   408

labels (\label):                  560
  - eq:                           186
  - sec:                          123
  - fig:                           88
  - ex:                            87   (exercises)
  - tab:                           41
  - ch:                            13
  - sol:                           12   (solutions)
  - app:                            5
  - alg:                            3
  - lst:                            1

cross-refs:
  - \ref{...}:                    852
  - \eqref{...}:                  232

citations:
  - \citet{...}:                  479
  - \citep{...}:                  201
  - \citeyear{...}:                 1
  - unique cite keys used:        254

custom envs:
  - definitionbox (tcolorbox):     14
  - remarkbox     (tcolorbox):     32
  - keyinsightbox (tcolorbox):     25
  - algorithm:                     11
  - algorithmic:                    9
  - lstlisting:                     6
```

### 2.2 MyST output (`mystmd/*.md` + `_build/site/content/*.json`) — R7 re-count

```
markdown files:                    23   — 12 ch + 6 app + 5 frontmatter (incl. index.md)
headings (## / ### / #### / #####):154 / 98 / 5 / 385
  (R6: 144 / 81 / 5 / 372 — counts grew because R6's grep was off-by-one on
   sub-/sub-sub-section nesting; source still 144/81/5; ##### == 385 paragraphs ✅)

figures:                            88   — all 88 {figure} directives present (R6: same)
captioned tables:                   41   — 41 anchors + 42 {table} directives (R6: 4 / 37) ✅
   table breakdown (R7):
     ```{table}``` directive:        42  (41 with `:name: tab-…`, 1 unanchored = notation common-symbols)
     ```{list-table}``` directive:    3  (the three unchanged lst- listings inherited from #15)
prf:algorithm directives:            2  (alg-young, alg-eminn)  — 3rd is mis-routed, see §3.4
prf:definition directives:          14
prf:remark directives:              57
code-block directives:               5
{numref} cross-refs (occurrences):  168
{ref}    cross-refs (occurrences):  550
{eq}     cross-refs (occurrences):  241
{cite*}  cross-refs (occurrences):  713

equation labels (`$$ … $$ (eq-…)`):161  (source has 186 `\label{eq:…}`; 25-label gap
                                          is mostly per-row align labels, see §3.2)
```

Cross-check against `myst build --html` warning log:
- 0 unresolved `{ref}` / `{numref}` (chapter / section / figure / table targets all resolve).
- 106 unique unresolved targets, comprising:
  - 96 `{prf:ref}\`ex-chN-M\`` to exercise labels never emitted as anchors (see §3.1)
  - 10 `{eq}\`eq-…\`` to per-row align labels MyST collapsed (see §3.2)
- 2 unresolved citation keys: `unil`, `tf.function` (see §3.5)
- 15 `label "X" replaced with "Y"` warnings (the underlying cause of the 10 broken `{eq}` refs above)
- 11 KaTeX errors (5 unique patterns) (see §3.3)
- 2 missing image asset warnings (see §3.7)
- ~22 pandoc-stage `Could not convert TeX math` warnings (custom macros — render fine in browser via `myst.yml`)

---

## 3. Findings (Round 7, by severity)

> **R8 status banner.** The §3.0–§3.4 findings below are the Round 7 write-ups, preserved as history. As of Round 8 (upstream `94baac5`): §3.0 **closed** (#68), §3.1 **closed** (#69), §3.2 **closed** (#70), §3.3 **closed** — `K^\\alpha` via #71 and the 8 `\,^\circ` instances via a local stopgap (upstream #45 still open), §3.4 **still open** (book #13, source-side). §3.5 (citations) and §3.7 (assets) unchanged → book #13 / #14. See §1 for the current state.

### 3.0 `validate.py` has been a no-op for this book since R1 — methodology defect ❌ → **CLOSED R8 (#68)**

**Symptom:** every R2–R6 report said "All cross-references resolve." The R7 myst-build log shows 106 unique unresolved targets. Both can't be true simultaneously.

**Root cause:** in [`scripts/validate.py:381–385`](https://github.com/QuantEcon/claude-latex-to-myst/blob/main/scripts/validate.py#L381-L385) the per-chapter loop opens the source `.tex` via `source_dir / f"{stem}.tex"` and silently `continue`s if `tex.exists()` is False. This book sets `source_dir: ../lecture_script`, which only ships the monolithic `Deep_Learning_for_Solving_And_Estimating_Dynamic_Economic_Models.tex` — the split per-stem files (`ch01_intro.tex`, …, `appF_solutions.tex`) live in `mystmd/tmp/` and are produced by the `preprocess.split:` step *during the convert run*. So every iteration of the per-chapter loop short-circuits, no rows are printed, and the trailing "All counts match. All cross-references resolve and are well-typed." prints because the totals are vacuously zero.

**Triage layer:** Layer 2 (upstream `claude-latex-to-myst`). `validate.py` needs to be `preprocess.split`-aware — when a stem maps to a section of a monolithic source, the chapter-level validator should look in the `tmp/` output of the splitter (or accept a `source_dir` per-entry override, or fall back to slicing the monolithic source by `\chapter{}` boundaries). Filing this in §4 is the highest-priority action for R8 — without it every subsequent round is operating blind on cross-ref breakage.

**Workaround for R7 reporting:** all R7 ref/cite counts in this report come from `myst build --html`'s warning log (`/tmp/build_warnings.log` in the repro section), not from `validate.py`.

### 3.1 96 broken `{prf:ref}` to exercises (largest single bug) ❌

87 exercises are labeled in source as `\item\label{ex:ch1:1} …` inside an `enumerate` environment. Pandoc strips the `\label{}` from inside `\item` (no MyST anchor is emitted for the list entry). `appF_solutions.md` then references each exercise as `##### {prf:ref}\`ex-ch1-1\` (statement: p. ): …`, and chapter bodies reference forward to exercises via `{prf:ref}\`ex-ch7-3\`` etc.

**Result:** every one of those 96 unique references renders unlinked (and the build emits `Cross reference target was not found: ex-chN-M`). The exercise text itself is present and correctly numbered in the rendered output; only the back-link from appF (and the forward-link from prose) is dead.

```
chapter bodies      :  1 (ch10_smm), 2 (ch07_pinns), 3 (ch04_nas / ch11_climate), 1 (ch12_synthesis) etc.
appF_solutions      : 96 broken (the canonical solutions index)
```

**Triage layer:** Layer 2 (upstream). The current pipeline already has `_apply_description_markers.py` for the analogous `\item` case in description lists. The same pattern — recognise `\item\label{X}` in an `enumerate`, hoist the label to an `(X)=` anchor just before the item, and emit a `{prf:exercise}` directive if the book opts in — would close this class. Two viable shapes upstream:
  1. **Anchor-only fix (minimum)**: emit `(ex-ch1-1)=` immediately above the `\item` in the converted markdown so `{prf:ref}` and `{ref}` both resolve, even if the rendered item is just a list bullet.
  2. **Directive promotion (preferred)**: emit each exercise as a `{prf:exercise}` directive (sphinx-proof has one) with the label as `:label:`, so `{prf:ref}` gets the proper "Exercise 1.1" rendering at the back-link site.

Either way this is a generic problem (every book with enumerated exercises hits it); belongs upstream, not in `config.postprocess.rewrites`. Filed in §4 as the second-highest priority for R8.

### 3.2 Per-row align `\label{}` collisions (15 cases) — MyST anchor model mismatch ⚠️

Source has 15 multi-row `\begin{align}` / `\begin{aligned}` blocks with per-row `\label{eq:X}`, `\label{eq:Y}`, etc. The converter promotes each label to a standalone anchor line:

```myst
(eq-iam_l1)=
(eq-iam_l2)=
(eq-iam_l3)=
…
(eq-iam_l8)=

$$
\begin{aligned}
  l_1 &:= …  \\
  l_2 &:= …  \\
  …
\end{aligned}
$$
```

MyST then warns `label "eq-iam_l8" replaced with "eq-iam_l1"` (and similarly for every subsequent label in the stack) because adjacent `(name)=` anchor lines with no content between them all bind to the same next block. Effect: only the first label survives; every subsequent `{eq}\`eq-iam_lN\`` for N>1 dangles. Same root cause as the prior R5 KaTeX `\tag*` note — both are downstream consequences of per-row align labels having no native MyST representation.

Affected pairs (replaced label / kept label):
- `eq-lstm_C` → `eq-lstm_f` (ch01)
- `eq-tblock2` → `eq-tblock1` (ch01)
- `eq-cake_expand_V` → `eq-cake_expand_disc` (ch07)
- `eq-gp_var` → `eq-gp_mean` (ch09)
- `eq-temp_oc` → `eq-temp_at` (ch11)
- `eq-iam_foc_k`, `eq-iam_foc_mu` → `eq-iam_foc_c` (ch11)
- `eq-iam_l2` … `eq-iam_l8` → `eq-iam_l1` (ch11, 7 cases)
- `eq-bayes_var` → `eq-bayes_mean` (ch11)

10 of these 15 collisions have a dangling `{eq}` reference somewhere in the book (the broken cross-ref count in §2.2); the other 5 are labels that exist for completeness but are never referenced.

**Triage layer:** Layer 2 (upstream). The converter currently stacks `(eq-x)=` lines above the math block; MyST's resolver collapses them. Two ways out:
  1. Convert the `aligned` block to a `{math}` directive with one `:label:` per row (MyST supports `:enumerator:` + multi-label) — preserves block layout, gets per-row anchors.
  2. Split the multi-row align into N separate `$$ … $$` blocks, one per row, each carrying its own trailing `(eq-x)` label.

Option (1) is cleaner for readers but needs the `:label:` syntax tested; option (2) breaks the visual alignment but is mechanically simpler. Either is a `transforms/math.py` change.

### 3.3 KaTeX errors in the rendered output (5 unique patterns, 11 instances) ⚠️

```
ch11_climate.md:249  Got group of unknown type: 'internal'     (×7 in ch11)
ch11_climate.md:619  Multiple \tag                              (×1; per-row \tag* in align)
ch02_deqns.md:249    Got function '\\' with no arguments as superscript at position 9: C > z K^\\alpha  (×1)
```

The `Got group of unknown type: 'internal'` set looks new vs R5 (which catalogued `\,^\circ\mathrm{C}` only). These all live inside ch11 source equations that use `\tag*{\text{…}}` per row of an align; the resulting expression tree has an "internal" node KaTeX doesn't handle. Closely related to #46 (filed in R5) — same family of KaTeX limitations, different surface symptom.

The ch02 `\\` superscript is a unique bug: source line 1232 has `K^\\alpha` (a copy-paste accident in the LaTeX: the backslash should be `\alpha` not `\\alpha`). This is a source-side typo, not a converter issue.

**Triage layer:** Layer 1 (source `.tex` fix for ch02 typo); Layer 3 (KaTeX behaviour) for the ch11 patterns. The R5 notes on #45 / #46 already cover the larger issue class — no new upstream tickets needed.

### 3.4 `alg-nsdeqn` rendered as `{prf:definition}` instead of `{prf:algorithm}` ⚠️

Source has 3 algorithm labels: `alg:young` (ch06), `alg:eminn` (ch08), `alg:nsdeqn` (ch11). The first two use `\begin{algorithm} … \label{alg:X} \begin{algorithmic} …` — the `_apply_algorithm_markers.py` preprocessor recognises both and emits `{prf:algorithm}` directives correctly. The third uses `\begin{definitionbox}[Algorithm: Non-Stationary DEQN Training] \label{alg:nsdeqn} \begin{algorithmic} …` — the book's project-specific `definitionbox` wrapper, mapped to `prf:definition` in `config.yaml::extra_environments`. The algorithm marker preprocessor only triggers on `\begin{algorithm}` so the third block goes through the `extra_environments` route and lands as `prf:definition` with the correct label, wrong directive type.

`{prf:ref}\`alg-nsdeqn\`` resolves (the label exists) but the rendered cross-reference text reads "Definition 11.3" instead of "Algorithm 11.3".

**Triage layer:** Layer 1 (book-side stopgap) or Layer 2 (general fix):
  - **Local:** change the ch11 source from `\begin{definitionbox}[Algorithm: …]` to `\begin{algorithm} \caption{Non-Stationary DEQN Training}`. One-line source fix.
  - **Upstream:** teach `_apply_algorithm_markers.py` to also recognise `\begin{definitionbox}[Algorithm: …]` (or any envvar wrapper whose optional arg starts with `Algorithm:`) and route to `prf:algorithm`. Less surprising for books that adopt the same dp1/dp2 `definitionbox` convention.

Recommend the local source fix for now and a CHANGELOG note upstream that "wrappers whose optional argument starts with `Algorithm:` are NOT auto-routed to `prf:algorithm` — use `\begin{algorithm}` for that."

### 3.5 Two unresolved citations: `unil` and `tf.function` ⚠️

```
preface.md           Could not link citation with label "unil".
ch02_deqns.md:110:70 Could not link citation with label "tf.function".
```

`unil` is the same mailto bug downstream-tracked at [book repo #2](https://github.com/mmcky/Deep_Learning_for_Solving_And_Estimating_Dynamic_Economic_Models/issues/2) — `\href{mailto:…@unil.ch}{…}` mis-parsed as a `\cite{unil}`. Not a real citation.

`tf.function` is the Python decorator `@tf.function` in a code block / inline code on ch02_deqns line 110:70. Pandoc's natbib parser appears to swallow `@tf.function` as a textual citation. The new `[035-citation-regex-trailing-colon-swallowed-into-key]` lesson upstream might already cover the analogous regex; if not, a tiny extension to make `@<key>` ignore the `tf.` prefix (or any key with internal `.`) would close it. Or escape the `@` in source.

**Triage layer:** Layer 1 (escape `@tf.function` in source as ``\texttt{tf.function}`` or rewrap) for the `tf.function` case; the `unil` case stays on its existing downstream ticket.

### 3.6 New `_warn_dropped_text_macros` warning — actionable, paste-ready fix ℹ️

```
WARNING: package-imported text macros pandoc may drop silently:
  \checkmark — used 1× (package `amssymb`) across ch06_ha_youngs.tex
      → ✓  (U+2713 check mark)
To apply, add to config.yaml under preprocess.rewrites:
    - { from: '\\checkmark(?![A-Za-z@])', to: '✓' }
```

The new (R7) `_warn_dropped_text_macros.py` preprocess scan flagged one `\checkmark` instance in ch06_ha_youngs. Whether the current render is broken is worth a one-paragraph spot-check (`grep -n checkmark mystmd/ch06_ha_youngs.md` — if the macro survived, no action; if it's gone, paste the suggested rewrite into `config.yaml`).

**Triage layer:** Layer 1 (config edit), one-line addition if the spot-check shows breakage.

### 3.7 Missing image assets — `restud_fig11a.pdf`, `restud_fig15a.pdf` ⚠️

ch11_climate references `fig/restud_fig11a.pdf` and `fig/restud_fig15a.pdf` (lines 203, 226 in the current MyST). Neither file lives in `mystmd/figures/` or any sibling asset directory in the repo, and even if they did, MyST would need imagemagick to convert PDF → renderable format. These figures are reproduced from a published paper and were never copied into the book repo's `figures/` tree.

**Triage layer:** Layer 1 (assets). Either (a) commit the two PDFs into `mystmd/figures/` and install imagemagick on the build host, or (b) replace these two `\includegraphics{fig/restud_fig*.pdf}` calls in source with rasterized PNG/SVG alternatives we generate ourselves, or (c) substitute a "Reproduced from Figure 11(a) of …" placeholder pointing at the cited paper. Asset decision — needs author sign-off.

### 3.8 ~22 pandoc `Could not convert TeX math` warnings (custom macros) — pre-existing, render fine ℹ️

The pandoc stage logs warnings like `Could not convert TeX math h(\x;\bm{\theta}), rendering as TeX` for every inline math expression that uses a custom shorthand (`\x \z \a \E \R \Wh \Wx \h`, etc.). These are not failures — pandoc emits the raw `$…$` to markdown and KaTeX renders the macros correctly at view time using the declarations in `mystmd/myst.yml`. The warnings are noise; could be silenced by extending pandoc's `--metadata=tex_macros:…` but it's not blocking.

**Triage layer:** Layer 3 (pandoc's awareness of custom macros) — not worth fixing; output is correct.

### 3.9 Math-macro coverage and unlabeled-align numbering (R6 carryovers) ℹ️

- **Math macros in `myst.yml`** — all 16 declared macros (`\x`, `\y`, `\z`, …, `\argmin`, `\argmax`) render correctly at view time. Unchanged from R5.
- **Unlabeled `\begin{align}` blocks** — LaTeX auto-numbers each row; MyST renders the block as `\begin{aligned}` with no row numbers. R6 callout still applies — readers comparing PDF and HTML side-by-side will see equations 1.11–1.14 numbered in PDF and unnumbered in HTML. Source-side decision (add a `\label{}` per row if numbering matters, but that re-triggers the §3.2 collision until the upstream fix lands).

---

## 4. Spot-checks (PDF ↔ MyST)

### 4.1 Chapter 1 §1.6 "The Adam Optimizer" (PDF pages 27–28)

Verified against `mystmd/ch01_intro.md:271–323`. Result: **substantial match**.

| Element | PDF | MyST | Match |
|---|---|---|---|
| `### The Adam Optimizer` heading | "1.6.1 The Adam Optimizer" | `### The Adam Optimizer` (with chapter-aware numbering at render time) | ✅ |
| Adam equations 1.11–1.14 | 4 numbered eqs in `align` | `$$ \begin{aligned} ... \end{aligned} $$` (unnumbered) | ⚠️ §3.8 |
| `### The Optimizer Family Tree` heading | "1.6.2" | matches | ✅ |
| Table 1.1 (5-col SGD→AdamW lineage) | proper table | preserved as pandoc dash-rule simple_table (5 cols, not converted) | ⚠️ §3.4 |
| Table 1.1 references in body text | "Table 1.1" | `Table {numref}`tab-optimizer_family`` | ✅ |
| 5 citations in table (Robbins+Monro, Sutskever, Tieleman+Hinton, Kingma+Ba, Loshchilov+Hutter) | properly cited | `{cite:t}` for each — all resolve | ✅ |
| Cross-refs to Chs. 7–8 (PINN, ct_theory) | "Chapters 7–8" | `{ref}`ch-pinn``–`{ref}`ch-ct_theory`` | ✅ |
| Figure 1.11 (optimizer trajectories) | rendered | `{figure} figures/fig-optimizer_trajectories.svg` | ✅ |
| Figure 1.12 (lr_schedules) | rendered | `{figure} figures/fig-lr_schedules.svg` | ✅ |
| `### Learning Rate Schedules` heading | "1.6.3" | matches | ✅ |
| Equation 1.15 (cosine annealing) | numbered | unlabeled `$$...$$` (no number) | ⚠️ §3.8 |

### 4.2 Chapter 11 §11.12 "Constrained Pareto-Improving Carbon Tax" (PDF pages 249–250)

Verified against `mystmd/ch11_climate.md:911–944`. Result: **substantial match**.

| Element | PDF | MyST | Match |
|---|---|---|---|
| `## Constrained Pareto-Improving Carbon Tax in OLG-IAMs` heading | "11.12" | matches | ✅ |
| `##### Notation reset for this section.` | `\paragraph` head | `##### ` | ✅ |
| `##### From CDICE to a TCRE emulator.` | `\paragraph` head | `##### ` | ✅ |
| Citations: Kübler 2026, Krueger+Kubler 2006, Karp 2024, Kotlikoff 2021, Douenne 2024, Dietz+Venmans 2019 | all properly cited | all resolve via `{cite:t}` / `{cite:p}` | ✅ |
| Cross-refs §11.11, §11.2, §11.3, Ch.9 in body | numbered correctly | `{ref}` directives that resolve | ✅ |
| **Caption cross-ref to §11.12** (`\ref{sec:pareto_carbon_tax}`) | "§11.12" | literal "§1.12" (wrong number) | ⚠️ §3.6 |
| `### The OLG-IAM Model` heading | "11.12.1" | matches | ✅ |
| Bulleted Technology/Households/Climate/Stochastic shocks list | bullet list | `- **Technology:**` etc. | ✅ |
| Inline math ($\Omega_t$, $T^{\mathrm{AT}}_t$, $\sigma_{\mathrm{CCR}}$, etc.) | renders correctly | preserved with custom macros | ✅ |
| Figure 11.7 (CDICE vs TCRE TikZ schematic) | rendered | `{figure} figures/fig-cdice_vs_tcre.svg` (TikZ-compiled by our render script) | ✅ |

---

## 5. Outstanding issues — routing recommendations

### Round 7 items — all filed; R8 status

| # | Item | Filed as | R8 status |
|---|---|---|---|
| R7-1 | `validate.py` silently skips every chapter when `preprocess.split:` is used (§3.0) | [QE#68](https://github.com/QuantEcon/claude-latex-to-myst/issues/68) | ✅ closed `291497c` — tmp_dir fallback + vacuous-pass guard |
| R7-2 | 87 `\item\label{ex:chN:M}` exercise labels dropped → 96 broken `{prf:ref}` (§3.1) | [QE#69](https://github.com/QuantEcon/claude-latex-to-myst/issues/69) | ✅ closed `cd7a0f9` — enumerate exercises → `{exercise}` directives |
| R7-3 | Per-row align `\label{}` collisions — only first label survives (§3.2) | [QE#70](https://github.com/QuantEcon/claude-latex-to-myst/issues/70) | ✅ closed `4d02d3f` — split per-row align into separate `$$` blocks |
| R7-5 | lstlisting `[caption={…math…}]` doubles backslashes (§3.3) | [QE#71](https://github.com/QuantEcon/claude-latex-to-myst/issues/71) | ✅ closed `fcba7b0` — decode pandoc quoted-attr escapes |
| R7-4 | `\begin{definitionbox}[Algorithm: …]` not auto-routed to `prf:algorithm` (§3.4) | [book#13](https://github.com/mmcky/Deep_Learning_for_Solving_And_Estimating_Dynamic_Economic_Models/issues/13) | ⏳ open — source-side fix; upstream #79 generalised env-div `prf:algorithm` but our `definitionbox`→`prf:definition` config mapping intercepts it |

### Round 11 — remaining open items

| Item | Tracker | Layer | Notes |
|---|---|---|---|
| `alg-nsdeqn` renders as Definition | [book#13](https://github.com/mmcky/Deep_Learning_for_Solving_And_Estimating_Dynamic_Economic_Models/issues/13) | 1 (source) | one-line `\begin{algorithm}` swap; cross-ref already resolves |
| `@tf.function` / `unil` citation false-positives | [book#13](https://github.com/mmcky/Deep_Learning_for_Solving_And_Estimating_Dynamic_Economic_Models/issues/13) | 1 (source) | escape `@` / mailto |
| Missing `restud_fig{11a,15a}.pdf` | [book#14](https://github.com/mmcky/Deep_Learning_for_Solving_And_Estimating_Dynamic_Economic_Models/issues/14) | 1 (assets) | author decision |

### Items closed since R10

| Item | Tracker | Status |
|---|---|---|
| `fix_spacing_superscript` phantom-fence + stash-collision (R10 content-loss + KaTeX) | [QE#87](https://github.com/QuantEcon/claude-latex-to-myst/issues/87) / [QE#88](https://github.com/QuantEcon/claude-latex-to-myst/pull/88) | ✅ closed `43565a4` (R11) — line-based state machine; local stopgap deleted |

### Round 10 — remaining open items

| Item | Tracker | Layer | Notes |
|---|---|---|---|
| `fix_spacing_superscript` (a) pairs phantom closing-fence with next bare ``` `````` ``` (KaTeX errors return), (b) outer stash captures inner `\x00FSS*\x00` marker and forward-order restoration leaves it unrestored (silent content loss of `{code-block}` in ch03) | [QE#87](https://github.com/QuantEcon/claude-latex-to-myst/issues/87) | 2 (post-#85 follow-on) | ✅ closed at R11 via [QE#88](https://github.com/QuantEcon/claude-latex-to-myst/pull/88) state-machine rebuild |
| `alg-nsdeqn` renders as Definition | [book#13](https://github.com/mmcky/Deep_Learning_for_Solving_And_Estimating_Dynamic_Economic_Models/issues/13) | 1 (source) | one-line `\begin{algorithm}` swap; cross-ref already resolves |
| `@tf.function` / `unil` citation false-positives | [book#13](https://github.com/mmcky/Deep_Learning_for_Solving_And_Estimating_Dynamic_Economic_Models/issues/13) | 1 (source) | escape `@` / mailto |
| Missing `restud_fig{11a,15a}.pdf` | [book#14](https://github.com/mmcky/Deep_Learning_for_Solving_And_Estimating_Dynamic_Economic_Models/issues/14) | 1 (assets) | author decision |

### Items closed since R8

| Item | Tracker | Status |
|---|---|---|
| `\,^\circ` degree symbol breaks KaTeX (R5/R8 carryover) | [QE#45](https://github.com/QuantEcon/claude-latex-to-myst/issues/45) | ✅ closed `0c41795` (R9) — but the fix missed `{table}` cells → [QE#85](https://github.com/QuantEcon/claude-latex-to-myst/issues/85) |
| Nested `{list-table}` enumeration drifts `{numref}` | [QE#52](https://github.com/QuantEcon/claude-latex-to-myst/issues/52) | ✅ closed `ef0acf4` (R9) — added `:enumerated: false` to 1 ch06 list-table |
| `\,^X` rewrite skips math inside `{table}` directive content | [QE#85](https://github.com/QuantEcon/claude-latex-to-myst/issues/85) | ✅ closed `3d0d797` (R10) — but introduced a new phantom-fence regression → [QE#87](https://github.com/QuantEcon/claude-latex-to-myst/issues/87) |

### Status of all previously filed issues (R1–R6 closures + open R5 carryovers)

| Round | Item | Tracker | Status |
|---|---|---|---|
| R1 | 18 multi-row `\begin{align}` per-row `\label{}` lost | [#30](https://github.com/QuantEcon/claude-latex-to-myst/issues/30) | ✅ closed (R7 §3.2 is a different surface of the same class — re-filing as R7-3) |
| R1 | `lstlisting` `label=lst:X` not propagated | [#31](https://github.com/QuantEcon/claude-latex-to-myst/issues/31) | ✅ closed |
| R1 | 5 citation keys with `:` lose suffix | [#32](https://github.com/QuantEcon/claude-latex-to-myst/issues/32) | ✅ closed |
| R1 | `\ref{}` inside `\caption{}` produces wrong number | [#33](https://github.com/QuantEcon/claude-latex-to-myst/issues/33) | ✅ closed |
| R1 | Multi-column tables (>2 col) not converted to `{list-table}` | [#34](https://github.com/QuantEcon/claude-latex-to-myst/issues/34) | ✅ closed (R7: superseded by #51/#55/#60 — now emit `{table}` directly) |
| R2 | `convert_pandoc_attr_code_blocks`: attrs regex chokes on `}` in captions | [#35](https://github.com/QuantEcon/claude-latex-to-myst/issues/35) | ✅ closed |
| R2 | `convert_citations`: trailing `:` regression | [#36](https://github.com/QuantEcon/claude-latex-to-myst/issues/36) | ✅ closed |
| R2 | `convert_equations`: multline/gather coverage | [#37](https://github.com/QuantEcon/claude-latex-to-myst/issues/37) | ✅ closed |
| R2 | Caption-ref typed dispatch | [#38](https://github.com/QuantEcon/claude-latex-to-myst/issues/38) | ✅ closed |
| R4 | `_apply_algorithm_markers`: `\label{alg:X}` sibling of `\caption{}` | [#39](https://github.com/QuantEcon/claude-latex-to-myst/issues/39) / [#43](https://github.com/QuantEcon/claude-latex-to-myst/issues/43) | ✅ closed (R7: 2-of-3 algorithms now correct; 3rd uses non-algorithm env → §3.4 / R7-4) |
| R4 | HTML entities inside math break KaTeX | [#40](https://github.com/QuantEcon/claude-latex-to-myst/issues/40) | ✅ closed |
| R5 | P3a refactor TIKZ_FIGURE_MAP empty | [#42](https://github.com/QuantEcon/claude-latex-to-myst/issues/42) | ✅ closed (was critical) |
| R5 | `\,^\circ\mathrm{C}` breaks KaTeX (`'internal'` group) | [#45](https://github.com/QuantEcon/claude-latex-to-myst/issues/45) | ⏳ open upstream (R8: worked around locally via `preprocess.rewrites`; build now KaTeX-clean). *(R5/R7 had #45 and #46 swapped in this table — #45 is the degree-symbol issue, #46 the `\tag*` one.)* |
| R5 | Per-row `\tag*` breaks KaTeX (Multiple \tag) | [#46](https://github.com/QuantEcon/claude-latex-to-myst/issues/46) | ✅ closed (R8: resolved by #70's per-row align split) |

### Local (book-side) items not requiring upstream

| Item | Notes |
|---|---|
| Source typo `K^\\alpha` in ch02 (§3.3) | One-character source fix in `lecture_script/Deep_Learning_for_Solving_And_Estimating_Dynamic_Economic_Models.tex:1232` (or thereabouts — `K^\\alpha` → `K^\alpha`). |
| `@tf.function` mis-parsed as cite (§3.5) | Wrap in source as `\texttt{@tf.function}` or `\verb!@tf.function!`. |
| Missing `fig/restud_fig{11a,15a}.pdf` (§3.7) | Asset decision — needs author sign-off (commit + imagemagick, or rasterize, or substitute placeholder). |
| `\checkmark` ×1 in ch06 (§3.6) | Spot-check the rendered ch06 page; if the macro dropped, add the one-line `config.yaml` rewrite the warner already pasted in. |

## 6. What this report does NOT cover

- **Paragraph-level content faithfulness** — no per-paragraph diff was attempted. The two spot-checks (§4.1, §4.2) cover ~3 pages of 329; structural counts cover everything else.
- **HTML rendering fidelity** — `myst build --html` succeeds, but a full visual walkthrough of every chapter in a browser hasn't happened yet. Step (5) of the PR #3 ordering ("Visual review of the deployed preview") is the natural place for that.
- **Bibliography ordering** — citation keys resolve, but the rendered references section ordering vs PDF wasn't compared.
- **Index** — the LaTeX source has 0 `\index{}` calls (stripped via `config.yaml`); no index to validate.
- **Cover page / title page / acknowledgments rendering** — frontmatter exists as separate `.md` files but wasn't visually checked.

## 7. How to reproduce this report (Round 7)

```bash
# From repo root
bash mystmd/convert.sh                                                # regenerate .md from source
cd mystmd && myst build --html 2>&1 \
  | grep -iE 'warn|error|⚠️|⛔' \
  | grep -vE 'GET|💌|node:|Deprecation' > /tmp/build_warnings.log
pkill -f 'myst.*start' 2>/dev/null  # myst build --html also launches start server
cd ..

# Source counts (LaTeX)
SRC=lecture_script/Deep_Learning_for_Solving_And_Estimating_Dynamic_Economic_Models.tex
grep -oE '\\label\{(eq|tab|fig|sec|alg|lst|ch|app|ex|sol):' "$SRC" | sort | uniq -c
grep -cE '^\\paragraph' "$SRC"
grep -oE '\\footnote\b' "$SRC" | wc -l
grep -cE '\\begin\{(table|tabular|longtable|tikzpicture|algorithm)\}' "$SRC"

# MyST output counts (R7-correct directive grep — note 3-or-more backticks)
grep -rohE '^`{3,}\{[a-z:-]+\}' mystmd/*.md | sort | uniq -c | sort -rn
grep -rE '^:name: (tab|fig|alg|lst)-' mystmd/*.md | wc -l
grep -rohE '\{(ref|eq|numref|prf:ref)\}`[^`]+`' mystmd/*.md | wc -l

# Warning triage from build log
grep -oE 'Cross reference target was not found: [a-zA-Z0-9_-]+' /tmp/build_warnings.log | sort -u | wc -l
grep -E 'label.*replaced with' /tmp/build_warnings.log | sort -u
grep -E '⛔' /tmp/build_warnings.log

# IMPORTANT: until R7-1 lands upstream, do NOT rely on validate.py for
# cross-ref resolution status — it silently no-ops because preprocess.split
# means per-stem .tex files only live under mystmd/tmp/, not source_dir.
# Use the myst build log as authoritative.
```
