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
**Round 16 update:** 2026-06-02 — first round driven by **upstream source changes**, not a tool-version bump (pin held at `ae466b8`/R15). Syncing `main` (`6363c56` → `c7f1762`, 5 commits) brought four source-side edits that propagate into the MyST output: (1) a **Ch 9/10 restructure** (`a81cf80` + `c7f1762`) splitting Gaussian processes (now Ch 9, retitled **"Gaussian Processes"**) from the deep-surrogate material (now Ch 10, **"Deep Surrogate Models and Structural Estimation"**) — `config.yaml` chapter titles updated to track the new `\chapter{}` headings, stems kept stable to avoid churning output filenames + the TOC; (2) `alg:nsdeqn` rewrapped in a real `\begin{algorithm}` env (`4b70424`) so it now renders as **`{prf:algorithm}`** instead of the mis-mapped `{prf:definition}` — closes the long-standing `alg-nsdeqn` item under book#13; (3) PNG rasters added for `restud_fig11a/15a` with the `.pdf` extension dropped from `\includegraphics` (`6cdec62`) — the book#14 (missing-asset) fix; (4) `@` escaped as `\texttt{{@}…}` (`4b70424`). Three landed cleanly; two needed local handling, each classified before fixing:
- **`{@}` escaping is context-dependent.** Inside the algorithm boxes the `\texttt` leaks verbatim and a bare `@tf.function` makes MyST misparse `[NEW: … @tf.function …]` as a parenthetical citation `[@tf.function]` (the R15 build warning tracked under book#13); the source's `{@}` form suppresses that (`@}` is not a valid citation key) and is **kept as-is**. But in flowing prose pandoc renders `\texttt{{@}foo}` as two *adjacent* code spans, leaving the broken token `` `@``foo` ``. Added a `postprocess` rewrite (**Class F**) that collapses the prose double-backtick only — the two contexts are separable after pandoc (prose carries backticks, the leaked box does not). Prose `@tf.function` / `@jax.jit` / `@tf.custom_gradient` now render clean; the box citation warning is gone. Converter root cause filed upstream as [QE#105](https://github.com/QuantEcon/claude-latex-to-myst/issues/105).
- **The book#14 figure fix only half-landed in this pipeline.** The PNGs copy into `mystmd/figures/` but the tool emits the `{figure}` directive with the raw, extensionless source path `fig/restud_fig11a`, which MyST cannot resolve (`⛔️ Cannot find image`). Added a ch11-scoped `postprocess` rewrite (**Class G**) mapping the raw `fig/<name>` → `figures/<name>.png`; both restud figures now resolve. Converter root cause (extensionless `\includegraphics` not resolved to the copied raster) filed upstream as [QE#104](https://github.com/QuantEcon/claude-latex-to-myst/issues/104).
Build is clean: **0 unresolved cross-refs, 0 KaTeX errors, 0 label collisions, 0 figure-resolution errors, 0 citation false-positives.** The two book#13 citation false-positives and the alg-nsdeqn item are now **resolved** (source + Class F); book#14 is **resolved** (source + Class G). Remaining warnings are the same pre-existing cosmetic pair (2 "Duplicate identifier" on repeated `Exercises`/`Further Reading` anchors, ~15 "missing heading depth"). One residual artifact left unfixed and filed upstream as [QE#106](https://github.com/QuantEcon/claude-latex-to-myst/issues/106): inline macros (`\eqref`, `\texttt`) leak verbatim inside algorithm-body environments — 3 `\eqref` leaks (ch04 ×1 new in the restructured BO box, ch06 ×2 pre-existing); no clean local stopgap (the `eq:`→`eq-` anchor remap makes a postprocess rewrite awkward), so it awaits the converter fix. New follow-up noted: 3 TikZ figures (`fig-bayesopt`, `fig-ergodic_vs_grid`, `fig-surrogate_outer_loop`) render nondeterministically (unseeded scatter) — their source blocks are byte-identical R15→R16 but `render_tikz.py`'s mtime cache re-renders on any `.tex` change, so they churn; **reverted to the committed SVGs** this round since the source did not change.
**Round 17 update:** 2026-06-09 — second source-driven round (pin held at `ae466b8`/R15). Syncing `main` (`c7f1762` → `fd51356`, 1 commit: *"Address Lukas Frank's annotations on Ch 6 / Ch 8 and reported code issues"*) brought a set of **prose-only** source edits — no structural changes (no new sections, math envs, figures, or tables). Nine Ch 6 edits (unpack "Monte Carlo panel" at first mention; forecasting rule is for aggregate prices; rename the consistency bullet; the equispacing-not-unit-value clarification on the bracket weight; split the Young-update linearity vs. sparsity claim; recast the "approximates higher moments" drawback as discretization bias vs. MC sampling noise; drop "$\mathcal{O}(1)$ in expectation" → "$\mathcal{O}(1)$ per state"; typo "one" → "two" state variables per agent in the Maliar KS variant; define `\varrho` locally), four Ch 8 edits (correct the chapter opener — HJB+KFE is the CT analogue of *Aiyagari*, the master equation of *Krusell–Smith*; tighten the two "Why continuous time?" bullets; the Brownian-path caption is an approximate visualization; the Dirac-atom KFE is valid distributionally, the `g_ac`+`α(n)` split is the numerical device), and one front-matter line (add Lukas Frank to Acknowledgments). **All 14 passages propagated 1:1** into `ch06_ha_youngs.md`, `ch08_ctime_ha.md`, and `preface.md`; cross-references introduced by the edits (`{ref}`sec-master_eq``, `{ref}`ch-deqn``) resolve cleanly. **PDF cross-check:** all 14 distinctive new phrases located in the rendered PDF (`fd51356`), confirming `.tex` → `.md` and `.tex` → PDF agree. Build is clean — **0 unresolved cross-refs, 0 KaTeX errors, 0 label collisions, 0 figure-resolution errors**; only the unchanged cosmetic pair remains (2 "Duplicate identifier", ~15 "missing heading depth"). The same 3 TikZ figures (`fig-bayesopt`, `fig-ergodic_vs_grid`, `fig-surrogate_outer_loop`) re-rendered with geometry drift from `render_tikz.py`'s mtime cache (the `.tex` mtime changed); their source TikZ is untouched by this commit, so — as in R16 — they were **reverted to the committed SVGs**.

**Round 18 update:** 2026-06-10 — first tool bump since R15: fast-forward `ae466b8` → `0bda217` (5 commits, headlined by [QE#103](https://github.com/QuantEcon/claude-latex-to-myst/pull/103), the **architecture-evolution phases 1–6** — validation gate + CI, marker shared base, ConversionContext, subfigure markers, book-side `project_overrides`, and a **Deep-Learning parity pass (Phase 6) run against this very book**). Source pin unchanged (`fd51356`/R17); no TikZ churn (mtime cache held). The output diff (322 ins / 285 del across 14 files) decomposes **entirely into 8 upstream-intentional classes**, each verified: (1) 105 × doubled-noun strip — prose "Figure␣" before `{numref}` dropped, fixing the rendered "Figure Figure N" doubling (QE#110 class); (2) 71 × `prf:` directives now carry their source optional titles (`{prf:remark} Chapter Summary`, …); (3) 11 × unnumbered `$$\begin{aligned}…$$` → `{math}` + `:enumerated: false` (stops MyST numbering equations the PDF leaves unnumbered); (4) algorithm-box fidelity — the 3 `\eqref` leaks convert to `{eq}` roles and `\texttt{{@}tf.function}` to clean code spans (**closes R16-filed [QE#105](https://github.com/QuantEcon/claude-latex-to-myst/issues/105) + [QE#106](https://github.com/QuantEcon/claude-latex-to-myst/issues/106)**), plus `for … do`/`end` loop markers; (5) `:width:` restored on the 10 `\includegraphics` figures, and extensionless `fig/restud_*` now resolves to the copied raster in the converter (**closes [QE#104](https://github.com/QuantEcon/claude-latex-to-myst/issues/104)**); (6) 5 leaked TikZ node-text lines dropped (ch01 ×3, ch06 ×2 — the text lives in the rendered SVGs; Phase-6 documented); (7) duplicate-`\label{}` aliases deduped — alias anchors dropped and their refs remapped to the primary (`sec-olg_setup`, `sec-olg_benchmark`, `sec-carbon_tax` anchors removed, 6 ch11 refs `sec-dice_lagrangian`→`sec-dice_deqn`; all verified unreferenced or resolving); (8) pandoc `[X]{.smallcaps}` spans → plain uppercase. With #104/#105/#106 landed, **both R16 local rewrites were deleted**: Class F matched nothing (verified by grep) and Class G was verified redundant by reconverting ch11 without it. Config migrated to the Phase-5 `project_overrides:` key (the `tikz_overrides:` alias is one-release). Two NEW fixes this round, both at the designed config surfaces: **Class H** — upstream's cleaner code-span output re-exposed a *mystmd* parser bug where `[NEW: … `@tf.function` …]` is scanned for citations *through the code span*, swallowing the bracket into an unresolved-cite node ("Could not link citation 'tf.function'", ch02 ×1); a postprocess rewrite escapes the opening bracket (root cause filed as [QE-mystmd#46](https://github.com/QuantEcon/mystmd/issues/46), with a minimal reproducer; related upstream [mystmd#1618](https://github.com/jupyter-book/mystmd/issues/1618) covers the link shape only); and **`doubled_noun_refs:` extras** for this book's `tab-`/`alg-` prefixes — a *rendered-text* check (new to this round's methodology) found 62 "Table Table N" + 4 "Algorithm Algorithm N" doublings that pre-date R18 and were never measured before; `('Table', 'tab-')` proposed as an upstream default in [QE#131](https://github.com/QuantEcon/claude-latex-to-myst/issues/131). The now marker-aware `validate.py` also newly *flags* the pre-existing `{cite:t}`unil`` mailto artifact in `preface.md` (book[#2](https://github.com/mmcky/Deep_Learning_for_Solving_And_Estimating_Dynamic_Economic_Models/issues/2), unchanged since the scaffold). Upstream's own count-baseline gate (`tests/baselines/deep-learning.json`) was diffed against this regen: all 16 drift entries are explained by the upstream fixture lagging this book's source (cloned pre-R16, before the Ch 9/10 restructure) — no drift of ours. Build state: **0 unresolved cross-refs (the `unil` book#2 artifact aside), 0 KaTeX errors, 0 label collisions, 0 marker leaks, 88/88 figures, 87 exercises**; cosmetic pair unchanged (2 "Duplicate identifier", ~15 "missing heading depth"). Residual nits, both upstream-side and cosmetic: `\texttt{Pi}` rides raw inside ch02's lstlisting `:caption:` (pre-existing since R16, newly noted), and the prf-title extraction leaves a single leading space on the directive body's first line (zero render impact).

**Round 19 update:** 2026-06-18 — tool bump `0bda217` → `9d8367b` (24 commits; "improvements just released" sync). Source pin unchanged (`fd51356`/R17); no TikZ churn (mtime cache held). Output diff is 803 ins / 1130 del across 21 files — heavily deletion-weighted because the dominant class merges a heading line + its blank line into the start of the following paragraph. **Every changed line decomposes into intended upstream classes; no regressions.** Headline fix: **[QE#164](https://github.com/QuantEcon/claude-latex-to-myst/pull/164) (#158B) recovers 11 corrupted exercises** (ch02 ×2, ch03 ×3, ch06, ch08, ch11 ×2, ch12 ×2) that R18's committed output silently shipped — each began `**\{eq}…` / `**\{ref}…` with the exercise title and opening sentence *swallowed* by `convert_cross_references` matching on an escaped `\[` bracket, and the cross-ref left escaped (rendering as literal `{eq}`/`{ref}`). These slipped past every R18 gate because **an escaped-brace role is never resolved, so it raises no unresolved-cross-ref warning** — it just shows broken markup; a direct `grep -E '\\\{(ref|eq|prf:ref)\}'` drops **11 → 0**. The remaining classes, each verified: **387 × `\paragraph` → bold run-in** ([QE#163-series](https://github.com/QuantEcon/claude-latex-to-myst/pull/163)/#160B) matching LaTeX run-in semantics — this is what eliminates **13 "missing heading depth" level-skip warnings** (#166 re-baseline); **2 labelled+referenced `\paragraph`s kept as headings** (#165 — `sec-matern` in ch09, `sec-irbc_fischer_burmeister` in ch03; both `\ref`'d, both resolve, and are the 2 heading-depth warnings that remain by design); **~453 dash ligatures** `--`→`–` / `---`→`—` (#1, prose-only — **0 leaked into code/math**, confirmed by 0 KaTeX errors; Brock–Mirman ×79, Gauss–Hermite ×34, …); **31 algorithm control keywords bolded** (#161/#163, matching the algorithm2e PDF); **custom-label enumerate** `\(a\)`→`(a)` unescaped (#111, appF); **Section/Table doubled-noun strips** (#150/#131 — 0 "Table Table"/"Section Section" in output); `\not`→`\neq` a **no-op** here (the book already used `\neq`); and **Stage-4 figure copy now copies only referenced assets** (#154 — 88/88 figures, **0 untracked-file churn**, down from the old blanket copy). Structural integrity: **every directive count is byte-for-byte identical before/after** — 700 `$$`, 88 figures, 44 tables, 87 exercises, 14 definitions, 57 remarks, 3 algorithms, 11 `{math}`, 5 code blocks — and 0 marker leaks (`[[CITE`/`FSS`/`smallcaps`/`:::`). Build state: **5 warnings / 0 errors (was 18 / 0)** — the 5 are all pre-existing (2 kept-paragraph heading-depth, 2 "Duplicate identifier", 1 `unil` book#2 citation). Config note: upstream #131 now ships `Table`/`Tables`+`tab-` as `doubled_noun_refs` defaults, so the book's local Table/Tables entries are now redundant (idempotent — left in place; the `Algorithm`/`alg-` entries are still book-local). One pre-existing cosmetic artifact persists, **not introduced this round**: appF's `(statements: p. , p. )` `\pageref` hangs — #158A's new orphan-pageref stripping requires an `on`/`from` locator and doesn't cover this `(statements: p.~\ref, …)` multi-ref parenthetical form. **No regressions → no upstream issue filed.**

**Round 20 update:** 2026-07-06 — combined source + tool round. **Source:** synced `main` (`fd51356` → `1a123b9`, 2 commits) — `6b18c3a` resolves the two e-book conversion source issues we filed (book[#1](https://github.com/mmcky/Deep_Learning_for_Solving_And_Estimating_Dynamic_Economic_Models/issues/1): the non-standard `L{<width>}` table column type, inline-expanded across all 20 usages to `>{\RaggedRight\arraybackslash}p{...}`; book[#2](https://github.com/mmcky/Deep_Learning_for_Solving_And_Estimating_Dynamic_Economic_Models/issues/2): the preface mailto, wrapped in `\nolinkurl{}`), and `1a123b9` rebuilds Lecture 13 NB08 (a `lectures/` notebook, outside the `lecture_script/*.tex` → MyST source path — no conversion effect). **Tool bump:** `9d8367b` → `89960a2` (5 commits). Every changed line in the 15-file output diff (1276 ins / 172 del) decomposes into intended classes — **no regressions**: (1) **[QE#171](https://github.com/QuantEcon/claude-latex-to-myst/pull/171)** plain `$$…$$` / `\[…\]` display math → `{math}` `:enumerated: false` — **142 blocks** reshaped (appF-heavy; also ch01/02/06/08/09/10/12), **total display-equation count conserved exactly 418 → 418** (407 `$$` blocks + 11 `{math}` → 265 `$$` blocks + 153 `{math}`), matching the PDF's unnumbered inline display math; (2) **[QE#175](https://github.com/QuantEcon/claude-latex-to-myst/pull/175)** dash ligatures now convert inside `{prf:*}` titles/bodies (ch03 *Fischer–Burmeister*, ch11 *Gauss–Hermite*, + the appF `{prf:ref}` exercise-solution headers: Brock–Mirman, Krusell–Smith, …); (3) **[QE#173](https://github.com/QuantEcon/claude-latex-to-myst/pull/173)** `multicols` paired columns → `{grid}` — **N/A** (book has no `multicols`); (4) **[QE#172](https://github.com/QuantEcon/claude-latex-to-myst/pull/172)** inline `$…$` spanning a hard line break no longer leaks raw LaTeX — **0 leaks** in this book (0 `\begin`/`\end` leaks confirmed by grep); (5) **#176** `setup_fixtures` / count re-baseline — tool-internal, no output effect. **Local config deltas:** (a) **removed** the now-dead `L{…}`→`p{…}` preprocess stopgap — book#1's source fix migrated every usage to `>{\RaggedRight\arraybackslash}p{…}`, so the rewrite matches nothing (0 `L{<width>}` occurrences remain in source); (b) **added Class I** — the book#2 source `\nolinkurl` attempt did **not** clear the artifact through this pipeline: pandoc still misparses `@unil` as a natbib citation inside **both** the `mailto:` URL and the `\nolinkurl` display text, emitting `{cite:t}`unil`` in each (2 occurrences, preface only). Class I (`stems: [preface]`) restores the literal `@unil`, rendering a clean monospace mailto link; the converter root cause (pandoc should not scan `mailto:` hrefs / `\nolinkurl` bodies for `@`-citations) is filed upstream as [QE#179](https://github.com/QuantEcon/claude-latex-to-myst/issues/179) (downstream tracker book#2) — drop Class I once it lands. **Structural integrity:** every directive count byte-for-byte identical to R19 — 88 figures, 43 tables, 87 exercises, 14 definitions, 57 remarks, 3 algorithms, 5 code blocks; 0 escaped-role leaks (`\{ref}`/`\{eq}`/`\{prf:ref}`), 0 marker leaks (`[[CITE`/`FSS`/`smallcaps`), 0 KaTeX errors, 0 unresolved cross-refs, 0 image-resolution errors. **Build: 4 warnings / 0 errors (was 5 / 0)** — the `unil` citation warning is gone; the 4 remaining are all pre-existing (2 kept-`\paragraph` heading-depth [#165], by design: `sec-matern` in ch09, `sec-irbc_fischer_burmeister` in ch03; 2 "Duplicate identifier": `exercises` / `further-reading`). The same 3 nondeterministic TikZ SVGs (`fig-bayesopt`, `fig-ergodic_vs_grid`, `fig-surrogate_outer_loop`) re-rendered from `render_tikz.py`'s mtime cache (the merge touched the `.tex`); their source TikZ is untouched by `6b18c3a`, so — as in R16–R19 — they were **reverted to the committed SVGs**.

**Round 21 update:** 2026-07-06 — tool bump `89960a2` → `7536261` (4 commits); the round that lands the fix for the mailto artifact we filed in R20. Source pin unchanged (`1a123b9`/R20); no TikZ churn (the `.tex` is untouched, so `render_tikz.py`'s mtime cache held — no SVG re-render). **[QE#181](https://github.com/QuantEcon/claude-latex-to-myst/pull/181) closes [QE#179](https://github.com/QuantEcon/claude-latex-to-myst/issues/179)** (the R20-filed root cause): pandoc no longer misparses the `@` in `mailto:` URLs / `\nolinkurl` / `\url` bodies as a citation, so the preface author-email converts **natively** to a clean `` [`simon.scheidegger@unil.ch`](mailto:simon.scheidegger@unil.ch) `` monospace mailto link. **The R20 local Class I stopgap is therefore deleted** — verified redundant by reconverting `preface` with the rewrite removed (0 `{cite:t}`unil`` left, 2 clean `@unil`), resolving book#2 end-to-end at the converter layer. The other three commits are **no-ops for this book**: [QE#180](https://github.com/QuantEcon/claude-latex-to-myst/pull/180) (`itemize` with custom `\item[...]` labels — none of the book's 77 `itemize` blocks had dropped labels), `#182` (deep-learning count re-baseline after #179 — tool-internal fixtures), `#183` (test locking the #177 inline-math / blockquote-continuation shape). **Output diff is empty** — all 23 `.md` files are byte-for-byte identical to R20 (the converter fix reproduces exactly what Class I produced), every structural count unchanged (88 figures, 43 tables, 87 exercises, 14 definitions, 57 remarks, 3 algorithms, 5 code blocks, 418 display equations), 0 escaped-role / marker leaks, and a full reconvert is idempotent. **Build: 4 warnings / 0 errors** (unchanged from R20) — 2 kept-`\paragraph` heading-depth ([#165](https://github.com/QuantEcon/claude-latex-to-myst/pull/165), by design), 2 "Duplicate identifier" (`exercises` / `further-reading`); the `unil` citation warning, cleared locally in R20, is now cleared at its source (the converter). **No regressions → no upstream issue filed.**

**Round 22 update:** 2026-07-06 — **visual-parity audit**: the first round to compare *rendered pixels*, not structural counts. Method: served the built HTML, drove headless Chrome (Playwright) to screenshot **10 seeded-random sampled locations** (2 TikZ figures, 1 raster figure, 2 tables, 2 numbered equations, 1 algorithm, 1 exercise + its appF solution, 1 section heading), rasterized the matching PDF pages (`pdftoppm`, 110 dpi), and read each pair side-by-side. Tool/source pins unchanged (`7536261` / `1a123b9`). **Core parity is strong**: figure numbers/captions/content identical (Figure 1.11, 9.5, 11.2 incl. the raster + its `{cite:t}` caption credit); tables exact to the cell (Table 2.2, 6.1, 5.1); section numbers match everywhere sampled (1.6.3, 2.6.4, 5.3, 6.6, 9.5, 11.2.6); exercise ex-ch9-7 and its appF solution are **word-for-word** vs. the PDF; algorithm bodies line-for-line with bold control keywords; equation *content* renders flawlessly (0 KaTeX issues). **Three defects found and triaged** (all layer-2, filed upstream): (1) **"Chapter Chapter N" doubling, 190 sites** — under this book's qe-v8 `numbering.book` mode a `{ref}` to a chapter renders "Chapter N", doubling the prose noun; upstream's strip deliberately omits Chapter for the `{ref}` role (stale qe-v5 assumption) and the `doubled_noun_refs:` config extras can't reach the `{ref}` role → [QE#184](https://github.com/QuantEcon/claude-latex-to-myst/issues/184) + local **Class J** rewrite (190 → 0, all 12 targets verified chapter labels; NBSP + plain-space separators both covered); (2) **lstlisting option leak** — ch06's Young-update listing rendered its `[language=Python, …, escapeinside={(*}{*)}]` option group as the code block's first line (the `escapeinside` braces break the option scan; 1 site book-wide) → [QE#185](https://github.com/QuantEcon/claude-latex-to-myst/issues/185) + local **Class K** rewrite (block now opens at `import numpy as np`, matching the PDF); (3) **equation-number drift vs the PDF** — filed as [QE#186](https://github.com/QuantEcon/claude-latex-to-myst/issues/186); root cause **corrected post-filing** (see the issue thread): unlabelled `\begin{equation}` envs *are* numbered by mystmd under `numbering.book` (ch01 AST: 35 numbered nodes, 20 of them label-less), so the drift is **not** a demotion of unlabelled envs — it is **multi-row `align` collapse**: an `align` with <2 labels converts to a single `\begin{aligned}` block that mystmd numbers *once*, where LaTeX numbers each non-`\nonumber` row. ch01's 5 collapsed aligns (rows 4,2,2,4,2; one `\nonumber`) predict a deficit of exactly **8** = the observed PDF 43 vs HTML 35 numbered; the first collapsed 4-row align sits just before the cosine equation, producing the measured (1.12)@HTML vs (1.15)@PDF −3 offset. ch07's −3 has the same shape. ch02/ch09/ch11 sampled points all match (no collapsed aligns early), which is why 21 structural rounds never caught it. **No local stopgap practical**; the upstream decision is editorial — per-row split (parity, loses `&` alignment) vs keep collapse (documented drift) vs per-row `aligned` enumerators in mystmd itself (both, longest path). Documented deviation until a direction is picked. **Three accepted style deviations documented** (internally consistent in both outputs, no action): PDF numbers algorithms globally ("Algorithm 1/2/3") vs MyST per-chapter ("Algorithm 6.1"); PDF renders exercises chapter-locally ("Exercise 3") vs MyST chapter-prefixed ("Exercise 9.7"); PDF remark boxes are unnumbered colored boxes vs MyST numbered `Remark N.M (title)`; plus table captions above (MyST theme) vs below (PDF). Post-fix build: **4 warnings / 0 errors** (unchanged); no TikZ churn.

**Round 23 update:** 2026-07-06 — tool bump `7536261` → `cfbe3e9` (2 commits), landing the converter-side fixes for 2 of the 3 R22 visual-parity findings. **[QE#188](https://github.com/QuantEcon/claude-latex-to-myst/pull/188) (issue [#184](https://github.com/QuantEcon/claude-latex-to-myst/issues/184))** adds the `role: ref` key to `doubled_noun_refs` — the exact config surface the R22 audit found missing — so the book's Chapter/Chapters entries now live at the designed surface (`{noun: Chapter, prefix: ch-, role: ref}` ×2, opt-in because the noun-doubling depends on the book's `myst.yml` numbering mode) and the **R22 Class J raw-regex rewrite is deleted**; verified 0 "Chapter Chapter N" in output, byte-identical to Class J's effect. **[QE#187](https://github.com/QuantEcon/claude-latex-to-myst/pull/187) (issue [#185](https://github.com/QuantEcon/claude-latex-to-myst/issues/185))** fixes the `escapeinside={(*}{*)}` option-scan break in the converter, so **Class K is deleted** too — and the converter fix is *better* than the stopgap: R22's output (fence conversion broken by the leak) fell back to a plain indented block, while the ch06 Young-update listing now emits a proper ```` ```python ```` fence and gains syntax highlighting (`lang: python` confirmed in the built AST; the only .md diff vs R22, +1/−1 lines shape). [#186](https://github.com/QuantEcon/claude-latex-to-myst/issues/186) (align-collapse numbering drift) remains open as the retitled design item — documented deviation, unchanged. Build: **4 warnings / 0 errors** (unchanged set); all other output byte-identical to R22; no TikZ churn. **The local rewrite ledger is now back to the 5 R12 classes + Class H only** — every stopgap added since (F, G, I, J, K) has been retired by an upstream fix, each verified redundant before deletion.

**Round 24 update:** 2026-07-16 — **source sync + a corrected TikZ-cache diagnosis**. **Source:** merged `main` `1a123b9` → `8c37a8b` (1 commit) — `8c37a8b` redraws Ch 11's Figure 11.3 (CDICE climate topology) on a wider canvas: 2.1 cm row pitch, the radiative-forcing relation as a two-line label above its arrow, the damage feedback routed orthogonally above the top row to terminate at `E_t`, edge labels `\scriptsize` → `\footnotesize`, and one content addition (an "emissions" label on `E_t → M^AT`). Caption, label and colors are untouched, so **0 `.md` churn** — every structural count is conserved *by construction* (88 `{figure}`, 153 `{math}`, 169 `{numref}`, 191 `{prf:*}`; 0 escaped roles, 0 marker leaks, 0 doubled nouns; build **4 warnings / 0 errors**, the same 4 pre-existing). Old/new rasterized and read side-by-side: the redraw resolves the cramping exactly as its commit message claims. **The headline finding is a correction to R16–R20.** Those rounds each saw the same 3 SVGs (`fig-bayesopt`, `fig-ergodic_vs_grid`, `fig-surrogate_outer_loop`) re-render whenever a merge touched the `.tex`, labelled them "nondeterministic", and **reverted them to the committed bytes**. That diagnosis was wrong for 2 of the 3. `render_tikz.py` is **deterministic** (two consecutive full renders → byte-identical output). Rendering at `20991fd` (the commit that committed those SVGs) reproduces `fig-bayesopt` and `fig-surrogate_outer_loop` **byte-for-byte on this machine** — so their drift is not noise but a **genuine source change never re-rendered**: `a81cf80` ("Ch 9/10 restructure: split GPs from deep surrogates") retitled bayesopt's legend `GP mean $\mu(h)$` → `$\bar f(h)$` and moved surrogate_outer_loop's right-hand title (`right=3.2cm` → `2.4cm`). **The committed `fig-bayesopt` has therefore shipped a legend reading μ(h) that contradicts its own caption and Ch 9's `\bar f` notation since `a81cf80`** — confirmed visually, not just by diff. Only `fig-ergodic_vs_grid` is genuinely environment-dependent: it is *not* reproducible at its own commit, its TikZ contains no randomness, and its 18 differing dots all sit on a `plot[smooth, tension=0.7]` Bézier — i.e. pgf-version curve interpolation, stable run-to-run here. **Root cause:** the cache skipped a figure when its SVG's mtime beat the *whole* `.tex`'s mtime. Git does not preserve mtimes, so after any clone or checkout every SVG looks newer than the source and **all 78 skip forever** — drift could never surface except by the accident of a merge rewriting the `.tex`, which is precisely the "churn" R16–R20 kept reverting. **Fix (local, layer 1):** the cache now keys on `sha256` of the exact standalone document compiled for each figure, stamped into the SVG as a trailing XML comment (valid: `document ::= prolog element Misc*`). Per-figure, not whole-file; immune to checkout mtime churn. Verified: stamp → 78 skipped; `touch` the `.tex` → still 78 skipped (the old cache would have re-rendered all 78); tamper one digest → **exactly** that figure re-renders. Cost: all 78 SVGs gain a 1-line digest (74 marker-only, 4 real content changes — 1 from `8c37a8b`, 3 the pre-existing drift, all **kept**, reversing the R16–R20 revert). **Deploy:** PR [#3](https://github.com/mmcky/Deep_Learning_for_Solving_And_Estimating_Dynamic_Economic_Models/pull/3) had been red since 2026-07-06 — **not a content failure**: MyST built and the 18.5 MB artifact uploaded cleanly every time; only `actions/deploy-pages` failed with the generic "Deployment failed, try again later", and the last-success → first-failure delta was a **2-line `VALIDATION.md` edit**, which cannot affect a Pages deploy. Branch policy already allowed `mystmd-conversion`. Re-running the identical commit `b0881ca` unchanged **succeeded** → transient Pages backend fault, since cleared. Workflow actions bumped off the deprecated Node 20 runtime (`checkout` v4→v7, `configure-pages` v3→v6, `setup-node` v4→v7, `upload-pages-artifact` v3→v5, `deploy-pages` v4→v5). **Known skew, flagged not changed:** CI builds the fork at tag `qe-v6` while local validation (R22/R23 included) runs `qe-v8`. Verified benign for the R23 `doubled_noun_refs` strip — the live qe-v6 site renders "Chapter 2"/"Chapter 3" correctly, because the noun comes from `myst.yml`'s `chapters: label: "Chapter %s"` book-mode numbering (qe-v4+), not the qe tag — but validating on a different engine than we deploy is a latent gap worth closing deliberately.

**Round 25 update:** 2026-07-16 — **CI upgraded qe-v6 → qe-v8**, closing the R24-flagged skew: validation (R22/R23 included) had been running `qe-v8` locally while the deploy shipped `qe-v6`. Because the live site and the local build were the *same commit* (`d317837`) on different engines, the upgrade's blast radius was measured directly rather than estimated: rendered text compared across **all 22 pages**, live-qe-v6 vs local-qe-v8. **18 pages identical**; the delta is exactly two classes. **(1) Improvement — Program numbering becomes per-chapter** (`Program 1` → `Program 4.1`, `1` → `3.1`, `2` → `2.2`; 4 sites in ch02/ch03/ch04). These are `lstlisting` captions; qe-v6 numbered them globally, qe-v8 per-chapter, matching how the book already numbers figures, tables and algorithms — accepted, no action. **(2) Regression — 10 custom enumerate labels silently eaten.** [QuantEcon/mystmd#50](https://github.com/QuantEcon/mystmd/pull/50) (fancy ordered lists) landed **between** qe-v6 and qe-v8 (verified by ancestry: `qe-v6` does *not* contain #50's merge commit, `qe-v8` does). With #50, a line-leading `(a) ` is *parsed* as an ordered-list marker where qe-v6 left it as literal paragraph text. The **parse is correct** — the AST carries `style: lower-alpha` / `delimiter: parens` — but the **HTML renderer drops both** and emits a bare `<ol start="1">`, so the markers render `1./2./3.`. Net: `(a)`,`(b)`,`(c)`,`(i)`,`(ii)`,`(iii)` in appF (×6) and `(a)`,`(b)` in ch02 (×4) vanish from the output. Triaged as **layer 3 (mystmd), renderer not parser**; the converter is blameless (its #111 `\(a\)`→`(a)` unescape was safe on a publisher without #50, and `postprocess.enumerate_style` — the *designed* surface for this — explicitly depends on #50 rendering correctly). **Local stopgap: Class L** re-escapes the parens (`^\((iii|ii|i|a|b|c)\) ` → `\(…\) `, scoped to `appF_solutions`/`ch02_deqns`, 10 sites). Escape strategies were tested empirically against qe-v8 before choosing: bare `(a)` → `<ol>` (the bug); `\(a\)` → literal `<p>(a) …` **and not inline math**; `&#40;` → works but unreadable; `<span>` → works but injects markup. **Verified:** appF and ch02 now render **identical to the qe-v6 baseline** (appF `<ol start=` count 4 → 0), leaving the Program renumbering as the only intended delta. Structural counts unchanged (88 `{figure}`, 153 `{math}`, 169 `{numref}`, 191 `{prf:*}`; 0 escaped roles, 0 marker leaks, 0 doubled nouns). Root cause filed upstream as [QuantEcon/mystmd#74](https://github.com/QuantEcon/mystmd/issues/74) (HTML renderer, not the parser); drop Class L once the renderer honours `style`/`delimiter`.

**Round 26 update:** 2026-08-14 — **the coupled pin bump** (book[#17](https://github.com/mmcky/Deep_Learning_for_Solving_And_Estimating_Dynamic_Economic_Models/issues/17)): tool `cfbe3e9` → `c4debe3` **and** CI renderer `qe-v8` → `qe-v9` in the same commit, because since [QE#201](https://github.com/QuantEcon/claude-latex-to-myst/pull/201) the converter emits non-starred `align` verbatim and depends on the fork's per-row numbering ([QuantEcon/mystmd#81](https://github.com/QuantEcon/mystmd/pull/81)) — bumping either alone silently reverts the fix. Source pin unchanged (`8c37a8b`). **Closes [QE#186](https://github.com/QuantEcon/claude-latex-to-myst/issues/186)**, the align-collapse drift that had been the one open design item since R22: HTML equation numbers now match the printed PDF **272/272 in every chapter** (live qe-v8 site: 265, wrong in 5 of 11 chapters — −17 from collapsed aligns in ch01/03/07/10, **+10** from ch11 over-numbering the `\tag*`-named `l_1`–`l_8` loss components and a `\nonumber`-split block). 5 files change; every line decomposes into three intended upstream classes — 10 `align` blocks passed through (QE#201), `\nonumber`/`\notag`/`\tag*` now modelled rather than leaked (**`\tag*` 8 → 0**, **`\nonumber` 2 → 0**, [QE#195](https://github.com/QuantEcon/claude-latex-to-myst/pull/195)), and depth-aware row splitting ([QE#196](https://github.com/QuantEcon/claude-latex-to-myst/pull/196), no book effect). Renderer blast radius measured live-vs-local across 4 unchanged pages: 2 word-for-word identical, 2 differing only in KaTeX 0.15.2 → 0.16.21 delimiter span structure ([QuantEcon/mystmd#80](https://github.com/QuantEcon/mystmd/pull/80)) plus one genuine cross-reference correction (appF → ch03 consumption sharing, (3.12) → **(3.13)**, PDF says 3.13). `align*` → unnumbered in qe-v9 is inert here (the converter already emits the book's starred aligns as forced-unnumbered `{math}`; 0 `\begin{align*}` in output). Class L still required — [QuantEcon/mystmd#74](https://github.com/QuantEcon/mystmd/issues/74) is unfixed in qe-v9 and the stopgap survives the bump (all 10 markers render). Structural counts byte-identical to R25; **813 cross-refs, 0 unresolved**; 0 escaped roles, 0 marker leaks, 0 KaTeX errors, 0 TikZ churn; build **4 warnings / 0 errors** (the same 4 pre-existing).

**Round 27 update:** 2026-08-14 — **converter-only bump `c4debe3` → `b01fa92` (1 commit); renderer stays `qe-v9`.** This is the "available now" half of book[#19](https://github.com/mmcky/Deep_Learning_for_Solving_And_Estimating_Dynamic_Economic_Models/issues/19), deliberately split from the qe-v10 coupling in the same issue — **that half stays blocked**: it depends on [QE#160](https://github.com/QuantEcon/claude-latex-to-myst/issues/160) emitting `{.unnumbered}` on starred sections, which is still open, and on qe-v9 an unstarred `{.unnumbered}` attribute block leaks as literal braces into both the heading text and its auto-slug. Unlike R26's coupling (a silently forfeited improvement), bumping the renderer alone here would be *visible corruption*, so the pins deliberately do **not** move together this round. Source pin unchanged (`8c37a8b`). **[QE#205](https://github.com/QuantEcon/claude-latex-to-myst/pull/205) (issue [#194](https://github.com/QuantEcon/claude-latex-to-myst/issues/194)) stops promoting pandoc-derived heading slugs to `(slug)=` anchors.** Output effect is exactly what the issue predicted and nothing else: **24 anchor-line deletions, 0 additions** — 12 `(exercises)=`, 11 `(further-reading)=`, 1 `(validation-protocol)=`, across all 12 chapters. **Build 4 warnings → 2 / 0 errors**: the two `Duplicate identifier in project` lines (`exercises`, `further-reading`) are gone, because those explicit anchors registered as *project-wide* named targets and collided across 12 pages, where an auto-generated heading id is page-scoped. Verified the anchors did not carry anything: **0 references** to any of the 3 slugs anywhere in the book, all 24 headings survive as headings, and `id="exercises"` / `id="further-reading"` are still present per page in the built HTML, so deep links are unaffected. The 2 remaining warnings are the by-design kept-`\paragraph` heading-depth pair ([#165](https://github.com/QuantEcon/claude-latex-to-myst/pull/165): `sec-irbc_fischer_burmeister` in ch03, `sec-matern` in ch09) — the first time this book has had **no** warning that is merely tolerated. **Regression gates all hold:** equation enumerators are **byte-identical to the deployed R26 site** in every chapter (272/272 vs the PDF preserved, 280 including ch11's 8 named `:enumerator:` blocks); **813 cross-references, 0 unresolved**; structural counts unchanged (88 `{figure}`, 87 exercises, 14 definitions, 57 remarks, 3 algorithms, 161 `{math}`, 10 `align`); Class L intact (appF 175 markers, `<ol start=` 0); 0 escaped roles, 0 marker leaks, 0 KaTeX errors, 0 TikZ churn. **Not fixed this round, by design:** 234 headings carry an enumerator and **24 of them still should not** — the `\section*{Further Reading}` / `\section*{Exercises}` pair at the end of nearly every chapter plus ch03's `\subsection*{Validation Protocol}`. Those are the spurious *numbers*; this round removes only the spurious *anchors*. They stay until QE#160 lands and the qe-v10 coupling in book#19 can be executed as one commit.

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

## 1. Headline result (Round 27)

Tool pin **`c4debe3` → `b01fa92`** (1 commit). **Renderer pin deliberately unchanged at `qe-v9`** — see below. Source pin unchanged (`8c37a8b`). [QE#205](https://github.com/QuantEcon/claude-latex-to-myst/pull/205) (issue [#194](https://github.com/QuantEcon/claude-latex-to-myst/issues/194)) stops promoting pandoc-derived heading slugs to `(slug)=` anchors, and the build reaches **2 warnings / 0 errors** — the first round in which every remaining warning is one this book keeps *by design*.

| | R26 | R27 |
|---|---|---|
| build warnings | 4 | **2** |
| — `Duplicate identifier` (`exercises`, `further-reading`) | 2 | **0** |
| — kept-`\paragraph` heading depth (by design, [#165](https://github.com/QuantEcon/claude-latex-to-myst/pull/165)) | 2 | 2 |
| `(slug)=` anchors emitted from heading text | 24 | **0** |
| equation numbers vs printed PDF | 272/272 | 272/272 |

**Output diff is 24 deletions and 0 additions**, across all 12 chapters: 12 `(exercises)=`, 11 `(further-reading)=`, 1 `(validation-protocol)=`. Nothing else changed in any `.md`.

**Why the duplicate-identifier warnings were real.** An explicit `(slug)=` anchor registers a **project-wide** named target. Twelve chapters each ending in `## Exercises` therefore declared the same project target twelve times, so only the first won and the rest were shadowed. An auto-generated heading id is page-scoped instead, which is why removing the anchors *fixes* addressability rather than costing it. Verified rather than assumed: **0 references** to any of the three slugs exist anywhere in the book, all 24 headings survive as headings, and `id="exercises"` / `id="further-reading"` are still emitted per page in the built HTML — deep links are unaffected.

**Regression gates.** Equation enumerators are **byte-identical to the deployed R26 site** in all 11 numbered chapters, so R26's 272/272 PDF match is preserved intact. 813 cross-references, 0 unresolved. Structural counts unchanged: 88 `{figure}`, 87 exercises, 14 definitions, 57 remarks, 3 algorithms, 161 `{math}`, 10 `align`. Class L intact (appF 175 markers, `<ol start=` 0). 0 escaped roles, 0 marker leaks, 0 KaTeX errors, 0 TikZ churn.

**The pins do *not* move together this round — deliberately.** book[#19](https://github.com/mmcky/Deep_Learning_for_Solving_And_Estimating_Dynamic_Economic_Models/issues/19) records a second, *stricter* coupling for `qe-v10`, and it is **blocked**: it needs [QE#160](https://github.com/QuantEcon/claude-latex-to-myst/issues/160) to emit `{.unnumbered}` on starred sections, which is still open. On qe-v9 and earlier that attribute block leaks into both the rendered heading text and its auto-slug, so bumping the renderer alone would be **visible corruption on every affected heading** — strictly worse than R26's failure mode, which merely forfeited an improvement silently. R26's rule was "these two pins move together"; the correct reading of it here is that *neither* moves until both can, and a converter change with no renderer dependency is free to ship on its own. This round is that.

**Still outstanding, by design:** 234 headings carry an enumerator and **24 should not** — `\section*{Further Reading}` and `\section*{Exercises}` at the end of nearly every chapter, plus ch03's `\subsection*{Validation Protocol}`. This round removes the spurious *anchors*; the spurious *numbers* wait for QE#160 and the qe-v10 coupled bump. The four `\chapter*` front-matter pages are excluded from that future fix on purpose — their heading is absorbed into frontmatter and suppressing at that level would strip the page `label:`.

## 1.0 Headline result (Round 26, preserved)

Tool pin **`cfbe3e9` → `c4debe3`** (7 commits) **and** CI renderer **`qe-v8` → `qe-v9`**, bumped in the *same commit* — the coupling that book[#17](https://github.com/mmcky/Deep_Learning_for_Solving_And_Estimating_Dynamic_Economic_Models/issues/17) exists to enforce. Source pin unchanged (`8c37a8b`). **[QE#186](https://github.com/QuantEcon/claude-latex-to-myst/issues/186), the last open design item from R22/R23, is closed**: the book's HTML equation numbers now match the printed PDF **exactly — 272/272, every chapter**.

The R25 column is measured from the **deployed site**, not estimated: the live mdast (`…github.io/<page>.json`) is the qe-v8 + `cfbe3e9` pair currently serving readers.

| Chapter | R25 (live, qe-v8) | R26 (qe-v9) | PDF | R25 verdict |
|---|---|---|---|---|
| ch01 | 35 | **43** | 43 | ❌ −8 |
| ch02 | 24 | 24 | 24 | ✅ |
| ch03 | 20 | **21** | 21 | ❌ −1 |
| ch04 | 11 | 11 | 11 | ✅ |
| ch05 | 18 | 18 | 18 | ✅ |
| ch06 | 13 | 13 | 13 | ✅ |
| ch07 | 28 | **31** | 31 | ❌ −3 |
| ch08 | 14 | 14 | 14 | ✅ |
| ch09 | 17 | 17 | 17 | ✅ |
| ch10 | 14 | **19** | 19 | ❌ −5 |
| ch11 | 71 | **61** | 61 | ❌ **+10** |
| **Total** | **265** | **272** | **272** | 6 of 11 chapters agreed |

Note the ch11 row runs the *other* way. Two distinct defects were cancelling in the headline total: the align collapse cost 17 numbers across ch01/03/07/10, while ch11 **over**-numbered by 10 — the eight `l_1`–`l_8` loss components carried `\tag*{(capital Euler)}`-style named tags that the PDF leaves unnumbered but qe-v8 numbered anyway (11.40–11.47), plus 2 phantom numbers from the `\nonumber`-split `eq-iam_foc_k` block. R26 fixes both directions.

**Method.** Enumerators are read from the built mdast, taking `rows[].enumerator` where qe-v9 numbers an `align` per row and the node-level `enumerator` otherwise; the PDF side is every right-aligned `(N.M)` tag from `pdftotext -layout`. Both sides are contiguous `1…max` per chapter, no gaps, no duplicates. **Verified positionally, not just by count** — the LSTM forget gate is (1.25) in both (live renders it 1.21); the bias/variance decomposition is (1.22) in both, with its first row's `\notag` honoured; the DGM gates are (7.11)–(7.14) in both; the IRBC consumption-sharing condition is (3.13) in both (live: 3.12). Matching **by label identity** across the two builds, **71 of 187 labelled equations change number** — ch01 ×10, ch03 ×11, ch07 ×8, ch10 ×4, ch11 ×38 — which is the expected size of a correction, not a warning sign: the previous build is the thing being corrected.

**One real cross-reference correction.** appF's link to the IRBC consumption-sharing condition rendered **(3.12)** on the live site and reads **(3.13)** in the PDF; ch03's worked steady state is a 2-row `align` that R25 collapsed to one number, so everything after it was off by one. R26 renders (3.13). This is the concrete form of the "forfeited fix plus a false claim" book#17 warned about: the converter CHANGELOG asserts PDF-matching numbering, and on qe-v8 that assertion would have been false.

**Output diff: 5 files, all decomposing into three intended classes — no regressions.**

1. **[QE#201](https://github.com/QuantEcon/claude-latex-to-myst/pull/201) (#186) — 10 multi-row `align` blocks pass through verbatim** instead of collapsing to `aligned` (ch01 ×5, ch03, ch07, ch10 ×3). `\begin{align}` 0 → 10, `\begin{aligned}` 29 → 21 (−10 converted, +2 new in ch11 from class 2). This is the entire +17.
2. **[QE#195](https://github.com/QuantEcon/claude-latex-to-myst/pull/195) (#192) — `\nonumber`/`\notag`/`\tag*` are now modelled** rather than leaked. ch11's eight loss components `l_1`–`l_8` become `{math}` directives carrying `:enumerator:` (capital Euler, budget, atm. carbon, …), and the two-`$$`-block `\nonumber` hack for `eq-iam_foc_k` merges into one `aligned` block. Book-wide **`\tag*` 8 → 0** and **`\nonumber` 2 → 0** — both were long-standing KaTeX-unsupported artifacts (R7 §3.3 class). `{math}` 153 → 161, `$$` block lines 530 → 510; all accounted for.
3. **[QE#196](https://github.com/QuantEcon/claude-latex-to-myst/pull/196) (#193) depth-aware row splitting** — no book effect (no nested-brace rows split incorrectly before or after).

**qe-v8 → qe-v9 renderer blast radius, measured live-vs-local** (same method as R25): rendered text of 4 unchanged pages compared between the deployed qe-v8 site and the local qe-v9 build. `ch05_olg` and `ch09_surrogates_gps` are **word-for-word identical** (ratio 1.00000); `ch02_deqns` and `appF_solutions` differ only in KaTeX **0.15.2 → 0.16.21** ([QuantEcon/mystmd#80](https://github.com/QuantEcon/mystmd/pull/80)) stretchy-delimiter span structure — `∥`, `∣`, `⎝⎛` glyph pairs that text extraction picks up differently — plus the one genuine (3.12)→(3.13) correction above. The 0.16 line keeps the 0.15-era CSS class vocabulary, so theme markup is unaffected. **`align*` becomes unnumbered in qe-v9** (matching amsmath): inert here, because the converter already emits the book's 8 starred aligns as forced-unnumbered `{math}` directives — `\begin{align*}` count in the output is **0**, before and after.

**Class L still required and still working.** [QuantEcon/mystmd#74](https://github.com/QuantEcon/mystmd/issues/74) (fancy-list renderer drops `style`/`delimiter`) is unfixed in qe-v9, and the R25 stopgap survives the bump unchanged: all 10 custom enumerate markers render — appF `(a)`/`(b)`/`(c)`/`(i)`/`(ii)`/`(iii)` present, `<ol start=` count **0**; ch02's single `<ol start="1">` is a genuine numbered list, not an eaten marker.

**Structural integrity:** 88 `{figure}`, 3 `{list-table}`, 87 exercises, 14 definitions, 57 remarks, 3 algorithms, 5 code blocks — every count byte-identical to R25. **813 cross-references, 0 unresolved**; 0 escaped-role leaks (`\{ref}`/`\{eq}` — the 4 grep hits are prose in this file), 0 marker leaks, 0 KaTeX errors, 0 TikZ/figure churn. Build **4 warnings / 0 errors**, the same 4 pre-existing (2 kept-`\paragraph` heading-depth by design, 2 "Duplicate identifier": `exercises`/`further-reading`).

**One known cosmetic gap, surfaced by the PR review and filed upstream as [QE#207](https://github.com/QuantEcon/claude-latex-to-myst/issues/207).** The converter drops a *bridging* trailing `,`/`;` when a labelled align row becomes a standalone `$$` block, but keeps it when the row fuses with a `\nonumber` continuation into one `aligned` block. That rule is deliberate and test-locked upstream (`_make_row_group`; `tests/test_transforms.py:3741`) — a bridging comma has nothing to bridge to once the row stands alone — and a sentence-ending `.` is always kept. Book-wide it is applied consistently: of the 25 labelled rows inside non-starred aligns, 8 comma-terminated rows drop it, the 1 fused row keeps it, and all 4 period-terminated rows keep theirs. It is only *visible* where fused and non-fused rows sit side by side, which in this book is Ch 11's three key FOCs — source `= 0,` / `= 0,` / `= 0.` renders as `= 0` / `= 0,` / `= 0.`, since `eq-iam_foc_k` fuses and its two siblings do not. R26 improves this from R25's 1-of-3 to 2-of-3; the residual is upstream's editorial call, not a local fix (these `.md` files are conversion output). No stopgap added.

**Pin coupling, going forward.** `mystmd/.tool-version` and `deploy-myst.yml`'s `git checkout` tag now move together: from QE#201 onward the converter emits non-starred `align` verbatim and depends on the fork's per-row numbering ([QuantEcon/mystmd#81](https://github.com/QuantEcon/mystmd/pull/81)), so bumping the converter alone silently reverts to R25's numbering while claiming R26's. The workflow checks out by **tag name**; if it is ever repinned by SHA, qe-v9 is `24f6ae8009961bcfb5f38d24f35c470405e869ee` (`git rev-parse qe-v9` returns the annotated tag object, not the commit).

## 1.0 Headline result (Round 23, preserved)

Upstream pin: **`cfbe3e9`** (fast-forward from `7536261` — 2 commits, the converter-side fixes for R22's [QE#184](https://github.com/QuantEcon/claude-latex-to-myst/issues/184) and [QE#185](https://github.com/QuantEcon/claude-latex-to-myst/issues/185)). Source pin unchanged (`1a123b9`). **Both R22 stopgaps retired at the designed surfaces**: Class J → two `doubled_noun_refs` entries with the new `role: ref` key (#188); Class K → deleted outright (#187 fixes the `escapeinside` option-scan in the converter, and upgrades the ch06 listing from a plain indented block to a highlighted ```` ```python ```` fence — the round's only output diff). Verified: 0 "Chapter Chapter N" (190 in R22 pre-fix), 0 option leaks, everything else byte-identical to R22, build **4 warnings / 0 errors** (unchanged). [#186](https://github.com/QuantEcon/claude-latex-to-myst/issues/186) (align-collapse drift) remains the one open design item — documented deviation. Local rewrite ledger back to R12's five classes + Class H; every stopgap since has been upstreamed and retired.

## 1.0 Headline result (Round 22 — visual-parity audit, preserved)

First **rendered-pixel** round: 10 seeded-random sampled locations screenshot-compared between the built HTML (headless Chrome / Playwright) and the rasterized PDF (`pdftoppm`). Pins unchanged (tool `7536261`, source `1a123b9`). Verdict: **content fidelity is excellent; three converter-layer defects found, filed, and (where possible) stopgapped**; build **4 warnings / 0 errors** after fixes.

| Pair (sampled) | HTML vs PDF | Verdict |
|---|---|---|
| Figure 1.11 optimizer trajectories (TikZ) | number, caption, plot identical; §1.6.3 matches | ✅ |
| Figure 9.5 inducing points (TikZ) | identical incl. (9.4) eq-ref match | ✅ |
| Figure 11.2 BAU emissions (raster PNG) | caption + `{cite:t}` credit intact; (11.13)–(11.16) all match | ✅ |
| Table 2.2 quadrature costs | exact to the cell; (2.18)/(2.19) match | ✅ |
| Table 6.1 HA methods landscape | exact to the cell | ✅ |
| Table 5.1 + Figure 5.2 + §5.3 (ch05) | all match | ✅ |
| Algorithm (alg-young) body | line-for-line, bold keywords | ✅ (numbering style deviation noted) |
| Exercise ex-ch9-7 + appF solution | **word-for-word** | ✅ |
| eq-cake_value (ch07) | content identical; **numbers drift (7.14)@HTML vs (7.17)@PDF** | ❌ → QE#186 |
| ch06 code cheatsheet | first line was leaked lstlisting options | ❌ → QE#185, fixed via Class K |

**Defects (all claude-latex-to-myst layer, filed):**
1. **[QE#184](https://github.com/QuantEcon/claude-latex-to-myst/issues/184)** — "Chapter Chapter N" doubled noun, **190 sites** (every `Chapter~\ref{ch:X}` in the book, incl. appF headings/TOC). Upstream's `{ref}`-role strip table deliberately omits Chapter on a stale numbering-mode assumption, and the config surface can't reach the `{ref}` role. **Local Class J** rewrite clears all 190 (targets verified = the 12 chapter labels).
2. **[QE#185](https://github.com/QuantEcon/claude-latex-to-myst/issues/185)** — lstlisting `escapeinside={(*}{*)}` breaks the option scan; the option group leaks as the code block's first line (1 site, ch06). **Local Class K** rewrite drops it; block now opens at `import numpy as np` like the PDF.
3. **[QE#186](https://github.com/QuantEcon/claude-latex-to-myst/issues/186)** — equation numbers drift from the PDF: ch01 −3 by (1.12), ch07 −3 across the HJB run; ch02/ch09/ch11 sampled points match — invisible to all 21 structural rounds. Root cause **corrected post-filing** (issue thread + R22 update line): not a demotion of unlabelled envs (those *are* numbered under `numbering.book`) but **multi-row `align` collapse** — an `align` with <2 labels becomes one `aligned` block with one number where LaTeX numbers every non-`\nonumber` row; ch01's 5 collapsed aligns predict the observed deficit of exactly 8 (PDF 43 vs HTML 35). **No practical local stopgap**; upstream call is editorial (per-row split vs keep-collapse vs mystmd per-row enumerators) — documented deviation meanwhile.

**Accepted style deviations** (internally consistent, no action): algorithm numbering global@PDF vs per-chapter@MyST; exercises "Exercise 3"@PDF vs "Exercise 9.7"@MyST; remark boxes unnumbered@PDF vs "Remark N.M"@MyST; table captions below@PDF vs above@MyST.

## 1.0 Headline result (Round 21, preserved)

Upstream pin: **`7536261`** (fast-forward from `89960a2`/R20 — 4 commits). Source pin unchanged (`1a123b9`/R20); no TikZ churn. This is the round that lands **[QE#181](https://github.com/QuantEcon/claude-latex-to-myst/pull/181)**, the fix for **[QE#179](https://github.com/QuantEcon/claude-latex-to-myst/issues/179)** we filed in R20 — `@` in `mailto:` / `\nolinkurl` / `\url` is no longer misparsed as a citation. **The output is byte-for-byte identical to R20** (empty `.md` diff): the converter now reproduces natively the clean `` [`simon.scheidegger@unil.ch`](mailto:simon.scheidegger@unil.ch) `` link that R20's local Class I stopgap was producing, so **Class I is deleted** and book#2 is resolved end-to-end. The 4 commits, classified:

| # | Commit | Effect on this book |
|---|---|---|
| 1 | [QE#181](https://github.com/QuantEcon/claude-latex-to-myst/pull/181) — email `@` in `mailto:` / `\nolinkurl` / `\url` no longer a citation (closes QE#179) | ✅ **native fix** — Class I retired; preface renders clean (0 `{cite:t}`unil``, 2 clean `@unil`) |
| 2 | [QE#180](https://github.com/QuantEcon/claude-latex-to-myst/pull/180) — `itemize` with custom `\item[...]` labels kept (follow-up to #111) | — N/A (no dropped labels among the book's 77 `itemize` blocks) |
| 3 | `#182` — deep-learning count re-baseline after #179 | — tool-internal fixtures |
| 4 | `#183` — test lock for the #177 inline-math / blockquote shape | — test-only |

**Structural integrity:** every count byte-for-byte identical to R20 — 88 figures, 43 tables, 87 exercises, 14 definitions, 57 remarks, 3 algorithms, 5 code blocks, 418 display equations — with 0 escaped-role leaks, 0 marker leaks, 0 KaTeX errors, 0 unresolved cross-refs, 0 image-resolution errors; a full reconvert is idempotent. **Build: 4 warnings / 0 errors** (unchanged) — 2 kept-`\paragraph` heading-depth ([#165](https://github.com/QuantEcon/claude-latex-to-myst/pull/165), by design), 2 "Duplicate identifier". **Local config delta:** Class I deleted (upstream #181 supersedes). **No regressions → no upstream issue filed.**

## 1.0 Headline result (Round 20, preserved)

Upstream pin: **`89960a2`** (fast-forward from `9d8367b`/R19 — 5 commits). Source synced `main` `fd51356` → `1a123b9` (2 commits: the `6b18c3a` e-book source fixes for book#1/#2, and the `1a123b9` Lecture-13-NB08 notebook rebuild, which lives outside the `lecture_script/*.tex` → MyST source path). Build improves **5 → 4 warnings, 0 errors** — the `unil` citation warning is cleared. Every changed line in the 15-file output diff (1276 ins / 172 del) was classified; all classes are intentional upstream improvements or no-ops — **no regressions**:

| # | Change class | Sites | Verdict |
|---|---|---|---|
| 1 | **[QE#171](https://github.com/QuantEcon/claude-latex-to-myst/pull/171)**: plain `$$…$$` / `\[…\]` display math → `{math}` `:enumerated: false` (unnumbered, matching the PDF); **total display equations conserved 418 → 418** | 142 | ✅ fidelity improvement (0 math lost) |
| 2 | **[QE#175](https://github.com/QuantEcon/claude-latex-to-myst/pull/175)**: `--`→`–` / `---`→`—` dash ligatures now convert inside `{prf:*}` titles & bodies (Fischer–Burmeister, Gauss–Hermite, Brock–Mirman, Krusell–Smith) | ~15 | ✅ improvement |
| 3 | **[QE#173](https://github.com/QuantEcon/claude-latex-to-myst/pull/173)**: `multicols` paired columns → `{grid}` — N/A, book has no `multicols` | 0 | — |
| 4 | **[QE#172](https://github.com/QuantEcon/claude-latex-to-myst/pull/172)**: inline `$…$` across a hard line break no longer leaks raw LaTeX — 0 in this book | 0 | — |
| 5 | **#176**: `setup_fixtures` / count re-baseline — tool-internal test fixtures | 0 | — |

**Source-side (merged from `main`):** book[#1](https://github.com/mmcky/Deep_Learning_for_Solving_And_Estimating_Dynamic_Economic_Models/issues/1) (`L{<width>}` column types) is **resolved at source** — `6b18c3a` inline-expands all 20 usages to `>{\RaggedRight\arraybackslash}p{…}`, so the local `L{…}`→`p{…}` preprocess stopgap is now dead and was **removed** (0 `L{<width>}` matches remain). book[#2](https://github.com/mmcky/Deep_Learning_for_Solving_And_Estimating_Dynamic_Economic_Models/issues/2) (preface mailto) was source-fixed with `\nolinkurl{}` but is **not cleared** through the converter — pandoc still reads `@unil` as a citation inside the `mailto:` URL and the `\nolinkurl` body; **new Class I** postprocess rewrite (`stems: [preface]`) restores the literal `@unil`, yielding a clean monospace mailto link and removing the last citation warning. Converter root cause (shield `mailto:`/`\nolinkurl` from pandoc's citation scan) filed upstream as [QE#179](https://github.com/QuantEcon/claude-latex-to-myst/issues/179); downstream tracker book#2.

**Structural integrity:** every directive count byte-for-byte identical to R19 — 88 figures, 43 tables, 87 exercises, 14 definitions, 57 remarks, 3 algorithms, 5 code blocks — and 0 marker leaks (`[[CITE`/`FSS`/`smallcaps`), 0 escaped-role leaks (`\{ref}`/`\{eq}`), 0 KaTeX errors, 0 unresolved cross-refs, 0 image-resolution errors. The 4 remaining build warnings are all pre-existing: 2 kept-`\paragraph` heading-depth ([#165](https://github.com/QuantEcon/claude-latex-to-myst/pull/165), by design), 2 "Duplicate identifier" (`exercises`/`further-reading`). Same 3 nondeterministic TikZ SVGs reverted to committed (R16–R19 pattern). **No regressions → no upstream issue filed.**

## 1.0 Headline result (Round 19, preserved)

Upstream pin: **`9d8367b`** (fast-forward from `0bda217`/R18 — 24 commits, the "improvements just released" sync). Source pin unchanged (`fd51356`/R17); no TikZ churn. Build improves **18 → 5 warnings, 0 errors**. Every changed line in the 21-file output diff (803 ins / 1130 del) was classified; all classes are intentional upstream improvements or no-ops — **no regressions**:

| # | Change class | Sites | Verdict |
|---|---|---|---|
| 1 | **#158B** ([QE#164](https://github.com/QuantEcon/claude-latex-to-myst/pull/164)): bracketed `[…\cref…]` no longer swallows its prose — recovers exercises that shipped as `**\{eq}…`/`**\{ref}…` with title + lead-in dropped and the role left escaped | **11** | ✅ **major fix** (was latent in R18, invisible to the xref gate) |
| 2 | **#160B/#166**: `\paragraph` → bold run-in (LaTeX run-in semantics); eliminates 13 "missing heading depth" level-skip warnings | 387 | ✅ improvement |
| 3 | **#165**: labelled+referenced `\paragraph` kept as a heading so `\ref` resolves (`sec-matern`, `sec-irbc_fischer_burmeister`) | 2 | ✅ verified safe (the 2 remaining heading-depth warnings, by design) |
| 4 | **#1**: `--`→`–`, `---`→`—` dash ligatures — prose-only, **0 in code/math** (0 KaTeX errors); Brock–Mirman ×79, Gauss–Hermite ×34, … | ~453 | ✅ improvement |
| 5 | **#161/#163**: algorithm control keywords (`for`/`do`/`end`/`return`/`while`) rendered bold, matching the algorithm2e PDF | 31 | ✅ improvement |
| 6 | **#111**: custom-label enumerate `\(a\)`→`(a)` unescaped (appF) | 6 | ✅ improvement |
| 7 | **#150/#131**: Section/Table doubled-noun strip (`Section␣{ref}`, `Table␣{numref}`) | — | ✅ 0 "Table Table"/"Section Section" in output |
| 8 | **#154**: Stage-4 copies only referenced figure assets (10→6); 88/88 figures, **0 untracked-file churn** | — | ✅ improvement |
| 9 | **#142** `\not`→`\neq` — no-op (book already used `\neq`); pifont/#159, `{prf:proof}`/#143, `::: center`/#140 — N/A to this book | 0 | — |

**Structural integrity:** every directive count is byte-for-byte identical before/after — 700 `$$`, 88 figures, 44 tables, 87 exercises, 14 definitions, 57 remarks, 3 algorithms, 11 `{math}`, 5 code blocks — and 0 marker leaks (`[[CITE`/`FSS`/`smallcaps`/`:::`). The 5 remaining build warnings are all pre-existing: 2 kept-paragraph heading-depth (#165, by design), 2 "Duplicate identifier" (`exercises`/`further-reading`), 1 `unil` book#2 citation. **Local config delta:** dropped the now-redundant `Table`/`Tables`+`tab-` `doubled_noun_refs` entries (covered by upstream #131 since this bump; regen byte-identical without them); `Algorithm`/`alg-` kept (upstream keys Algorithm off `algo-`, not this book's `alg-`). One pre-existing cosmetic artifact persists, **not introduced this round**: appF's `(statements: p. , p. )` `\pageref` hangs — #158A's orphan-pageref strip requires an `on`/`from` locator and doesn't cover the `(statements: p.~\ref, …)` multi-ref parenthetical form. **No regressions → no upstream issue filed.**

## 1.0 Headline result (Round 18, preserved)

Upstream pin: **`0bda217`** (fast-forward from `ae466b8`/R15 — the first tool bump in three rounds, bringing the architecture-evolution phases 1–6 ([QE#103](https://github.com/QuantEcon/claude-latex-to-myst/pull/103)) plus the #98/#99 figure-marker fixes). Phase 6 of that PR was a parity pass run against this book, so most of the delta was upstream-predicted. Every changed line in the 14-file output diff was classified; all 8 classes are intentional upstream improvements:

| # | Change class | Sites | Verdict |
|---|---|---|---|
| 1 | "Figure␣`{numref}`" doubled-noun strip (rendered "Figure Figure N" fixed) | 105 | ✅ improvement |
| 2 | `prf:` directives carry optional titles (`{prf:remark} Chapter Summary`, …) | 71 | ✅ improvement |
| 3 | unnumbered `$$aligned$$` → `{math}` `:enumerated: false` (PDF numbering fidelity) | 11 | ✅ improvement |
| 4 | algorithm-box `\eqref`→`{eq}`, `\texttt{{@}X}`→code span, `do`/`end` markers | 3 + 3 | ✅ closes QE#105/#106 |
| 5 | `:width:` on `\includegraphics` figures; converter resolves `fig/restud_*` rasters | 10 + 2 | ✅ closes QE#104 |
| 6 | leaked TikZ node-text lines dropped (text lives in the SVGs) | 5 | ✅ improvement |
| 7 | duplicate-`\label{}` aliases deduped; refs remapped to primary label | 3 anchors + 6 refs | ✅ verified safe |
| 8 | `[X]{.smallcaps}` → uppercase | 4 | ✅ improvement |

Local config delta: R16's Class F and Class G rewrites **deleted** (both made redundant by QE#104/#105/#106 landing — verified empirically); `tikz_overrides:` renamed to `project_overrides:`; two additions — **Class H** (escape the ch02 `**[NEW: … `@tf.function` …]**` bracket that mystmd's citation scanner misparses *through* a code span; root cause filed as [QE-mystmd#46](https://github.com/QuantEcon/mystmd/issues/46)) and **`doubled_noun_refs:` extras** for `tab-`/`alg-` (clearing 62 "Table Table N" + 4 "Algorithm Algorithm N" pre-existing rendered doublings — first round to measure rendered ref text). Upstream's own count baseline for this book (`tests/baselines/deep-learning.json`) diffs against this regen only where their fixture lags our source (cloned pre-R16 restructure).

Build state: **0 unresolved cross-refs, 0 KaTeX errors, 0 label collisions, 0 marker leaks, 88/88 figures with images, 87 exercises.** The marker-aware `validate.py` now also flags the pre-existing `{cite:t}`unil`` mailto artifact (book#2 — present since the scaffold, newly visible). Remaining warnings: the unchanged cosmetic pair (2 "Duplicate identifier", ~15 "missing heading depth") + the `unil` line. No TikZ churn this round.

## 1.0 Headline result (Round 17, preserved)

Upstream pin: **held at `ae466b8`** (R15) — second source-driven round, syncing `main` (`c7f1762` → `fd51356`, the Lukas Frank Ch 6 / Ch 8 annotations). The commit is **prose-only**: no new sections, math environments, figures, or tables, so the conversion delta is confined to three files.

| Source edit | Output file | Result |
|---|---|---|
| 9 Ch 6 prose clarifications (MC panel, forecasting rule, consistency bullet, equispacing weight, linearity/sparsity split, discretization-bias drawback, $\mathcal{O}(1)$-per-state, one→two state vars, local `\varrho`) | `ch06_ha_youngs.md` | propagated 1:1 ✅ |
| 4 Ch 8 prose clarifications (Aiyagari/Krusell–Smith opener, "Why CT?" bullets, Brownian-path caption, Dirac-atom KFE) | `ch08_ctime_ha.md` | propagated 1:1; new `{ref}`sec-master_eq`` resolves ✅ |
| Add Lukas Frank to Acknowledgments | `preface.md` | propagated 1:1 ✅ |

Build state: **0 unresolved cross-refs, 0 KaTeX errors, 0 label collisions, 0 figure-resolution errors.** PDF cross-check: all 14 distinctive new phrases located in the rendered PDF (`fd51356`) — `.tex` → `.md` and `.tex` → PDF agree. No new `postprocess`/`config` changes were needed. The 3 nondeterministic TikZ SVGs churned again from the mtime cache and were reverted to committed (see the **Round 17 update** line above). Remaining warnings are the unchanged cosmetic pair (2 "Duplicate identifier", ~15 "missing heading depth").

## 1.0 Headline result (Round 16, preserved)

Upstream pin: **held at `ae466b8`** (R15) — this is the first round driven by *source* changes synced from `main` (`6363c56` → `c7f1762`), not a tool bump. Four source edits propagated; all five long-standing source-side residuals are now resolved:

| Item (prior status) | Source change | Output result |
|---|---|---|
| `alg-nsdeqn` rendered as `{prf:definition}` (book#13) | `4b70424` wraps it in `\begin{algorithm}` | now `{prf:algorithm}` ✅ |
| `@tf.function` citation false-positive (book#13) | `4b70424` escapes `@` → `\texttt{{@}…}` | box warning suppressed; prose fixed via **Class F** ✅ |
| `restud_fig11a/15a` missing assets (book#14) | `6cdec62` adds PNGs, drops `.pdf` ext | figures resolve via **Class G** path rewrite ✅ |
| Ch 9 = "Deep Surrogate Models and GPs" | `a81cf80`+`c7f1762` split GPs from surrogates | retitled **"Gaussian Processes"** (config) ✅ |
| Ch 10 = "Structural Estimation via SMM" | (same restructure) | retitled **"Deep Surrogate Models and Structural Estimation"** (config) ✅ |

Build state: **0 unresolved cross-refs, 0 KaTeX errors, 0 label collisions, 0 figure-resolution errors, 0 citation false-positives.** Two new local `postprocess` rewrites this round (Class F: prose `` `@``X` `` → `` `@X` ``; Class G: ch11 `fig/<name>` → `figures/<name>.png`), both documented with the upstream root cause. Remaining warnings are the unchanged cosmetic pair (2 "Duplicate identifier", ~15 "missing heading depth"). See the **Round 16 update** line above for the full classification.

## 1.0 Headline result (Round 15, preserved)

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
