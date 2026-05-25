# MyST conversion — VALIDATION report

**Scope:** structural counts + targeted spot-checks of the MyST/HTML build against the LaTeX source and rendered PDF.
**Initial validation:** 2026-05-24 (commit `a26cddc`).
**Round 2 update:** 2026-05-25 — re-tally after upstream landed fixes for issues #30–#33.
**Round 3 update:** 2026-05-25 — re-tally after upstream landed fixes for follow-ups #35, #36, #37.
**Round 4 update:** 2026-05-25 — drill into deferred items; 2 new bugs filed (#39 algorithm label, #40 HTML entity in math); 2 prior "gaps" resolved as counting artifacts.
**Round 5 update:** 2026-05-25 — re-tally after upstream landed fixes for #38, #39, #40 *and* a major refactor (P3a series, 11 commits) splitting `postprocess.py` into a `transforms/` package. #38 and #40 work; #39 only partially (filed [#43](https://github.com/QuantEcon/claude-latex-to-myst/issues/43)). The P3a refactor introduced a critical regression: module double-load drops `TIKZ_FIGURE_MAP` content silently, breaking **all 88 figures** ([#42](https://github.com/QuantEcon/claude-latex-to-myst/issues/42) filed). Round 4 also under-reported KaTeX warnings — re-grep surfaces 9 pre-existing instances of `\,^\circ` and `\tag*` patterns that KaTeX can't handle (not a refactor regression).
**Round 6 update:** 2026-05-25 — #42 closed with the `sys.modules['postprocess']` aliasing fix (option B from the proposal). Re-tally: **all 88 figures restored**, all cross-ref classes resolve cleanly, citations clean. The fix is generic — every `transforms/` module that late-imports `postprocess` for state now resolves to the same instance, closing the whole class of bugs at once.
**Branch:** `mystmd-conversion`
**Sources:**
- `lecture_script/Deep_Learning_for_Solving_And_Estimating_Dynamic_Economic_Models.tex` (24,557 source lines, 329-page PDF)
- `mystmd/*.md` (23 converted files: 12 chapters + 6 appendices + 5 frontmatter)
- `mystmd/_build/` (post `myst build --html`)
- `readings/bibliography.bib` (278 entries)
- `mystmd/myst.yml`, `mystmd/config.yaml`, `mystmd/tikz_overrides.py`

**Methodology (what this report does and doesn't do):** structural counts compare totals between source and output; per-anchor cross-ref checks identify broken references; spot-checks compare 2 PDF pages (ch01 §1.6 and ch11 §11.12) side-by-side with the converted markdown. This report does **not** do a full paragraph-level content diff — that would be infeasible at this scale. The goal is to give bounded confidence that the conversion is structurally faithful and to enumerate any remaining gaps with concrete examples.

---

## 1. Headline result (Round 6)

| Dimension | Source | MyST | Match? | R5 | R4 | R3 | R2 | R1 |
|---|---|---|---|---|---|---|---|---|
| Chapters / sections / subsections / subsubsections | 22/144/81/5 | 22/144/81/5 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Paragraph heads / footnotes | 385 / 24 | 385 / 24 | ✅ | ✅ | ✅ | ⚠️ glob | ⚠️ same | ⚠️ same |
| Figure placeholders | 88 | **88 / 88 rendering** | ✅ | ❌ #42 | ✅ | ✅ | ✅ | ✅ |
| Captioned tables — anchors / `{list-table}` AST | 41 / 41 | 41 / 4 | ⚠️ #34 | ⚠️ same | ⚠️ same | ⚠️ same | ⚠️ same |
| `\label{alg:X}` cross-ref round-trip | 2 labels | broken (still auto-name) | ⚠️ #43 | ⚠️ #39 | n/a | n/a | n/a |
| Unique `{numref}` cross-ref targets | — | 125 / 125 | ✅ | ✅ | ✅ | ✅ | ✅ |
| Unique `{ref}` cross-ref targets | — | **0 broken** | ✅ | ⚠️ 11 | ⚠️ same | ⚠️ 12 | ⚠️ 1 |
| Unique `{eq}` cross-ref targets | — | 160 / 160 | ✅ | ✅ | ✅ | ⚠️ 1 | ⚠️ 18 |
| Citation keys vs `references.bib` | 254 | all resolve | ✅ | ✅ | ✅ | ⚠️ 9 | ⚠️ 5 |
| Math macros / tcolorbox / paragraph heads | — | match | ✅ | ✅ | ✅ | ✅ | ✅ |
| Caption section/chapter `\ref{}` | — | works | ✅ | ✅ | ✅ | ✅ | ❌ |
| Caption equation/algorithm typed refs | — | **typed dispatch works** | ✅ | ⚠️ #38 | ⚠️ same | ⚠️ same | n/a |
| `lstlisting` `label=…` anchor | — | `{code-block}` with `:name:` | ✅ | ✅ | ✅ | ⚠️ #36 | ❌ |
| HTML entity in caption math | — | unescaped | ✅ | ⚠️ #40 | n/a | n/a | n/a |
| KaTeX build warnings (other) | — | 9 (pre-existing, see §3.x) | ⚠️ note | (missed) | n/a | n/a | n/a |

**Round 5 verdict — mixed:**

✅ **Upstream fixes that landed and work**: #38 (typed caption refs — all 11 now resolve), #40 (HTML entity unescape — `&gt;` no longer leaks into math).

⚠️ **#39 (algorithm sibling label) partial**: the fix added a sibling-label scan, but it only handles the case where `\label{}` comes AFTER the algorithm body (and at end). The dominant LaTeX convention places `\caption{}\label{}` BEFORE the body (which is layout in our book) — for that layout the scan still bails and an auto-name is generated. Filed [#43](https://github.com/QuantEcon/claude-latex-to-myst/issues/43) with proposed generic scan covering both pre- and post-caption regions.

❌ **CRITICAL REGRESSION from P3a refactor**: the refactor split `postprocess.py` into a `transforms/` package. `transforms/figures.py::resolve_tikz_figures` reads `TIKZ_FIGURE_MAP` via `import postprocess; postprocess.TIKZ_FIGURE_MAP`. But `postprocess.py` runs as `__main__`, so `import postprocess` creates a *second* import of the module — fresh, with `TIKZ_FIGURE_MAP={}`. `load_overrides` populates the `__main__` namespace's map (88 entries); the transform reads the empty second-import map. Result: **all 88 figure placeholders left unresolved** in the converted markdown. Confirmed locally by patching the transform to read from `__main__` — figures return immediately. Filed [#42](https://github.com/QuantEcon/claude-latex-to-myst/issues/42) with three fix options (`__main__` fallback, module aliasing, shared state module). The same pattern likely affects every `transforms/` module that late-imports `postprocess` for state — should be audited.

ℹ️ **9 pre-existing KaTeX warnings surfaced** (not refactor-induced — verified by rolling upstream back to the Round 3 baseline `8b2ceec` and re-running; warning count was 9 there too). Round 4's grep only matched `Expected 'EOF'` patterns, so these were missed. Patterns: `T_{\mathrm{AT}}=3\,^\circ\mathrm{C}` (8 instances; KaTeX bug or limitation with `\,^\circ`), `Multiple \tag` (1 instance in ch11 `:= ... \tag*{(capital Euler)} \\ := ... \tag*{(budget)}` — source uses `\tag*` per row of an `align`, which KaTeX rejects on multi-row aligned blocks). These are KaTeX-side limitations, not converter bugs.

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

### 2.2 MyST output (`mystmd/*.md` + `_build/site/content/*.json`)

```
markdown files:                    23   — 12 ch + 6 app + 5 frontmatter (incl. index.md)
headings (## / ### / #### / #####):144 / 81 / 5 / 372

figure directives:                  88   — all resolve to {figure} ... .svg|.png|.pdf
{numref} cross-refs (unique):      125  (85 fig + 40 tab)
{ref}   cross-refs (unique):       103  (84 sec + 12 ch + 5 app + 1 subsec + 1 lst)
{eq}    cross-refs (unique):       160
{prf:ref} cross-refs:              116

citations:
  - {cite:t}: 481
  - {cite:p}: 215
  - {cite}:    15

directives:
  - {prf:remark}:     57   (close to 32 remarkbox + 25 keyinsightbox = 57 — exact match)
  - {prf:definition}: 14   (= 14 definitionbox — exact match)
  - {list-table}:      4   (2-col tables only; 4-col + other tables pass through)

labelled equation anchors:        160  (matches {eq} unique targets above, but 18 short of the 186 source labels)
```

---

## 3. Findings (by severity)

### 3.1 No remaining figure regressions ✅

All 88 placeholders render across all 12 chapters (verified via `_build/site/content/*.json` image-node count). The path from this morning's first scan (`6 dropped in ch01, 6 in ch02, 1 each in ch06/ch07/ch09 = 15 total`) is now `0 / 88`. The recovery came from upstream `claude-latex-to-myst` fixes [#26](https://github.com/QuantEcon/claude-latex-to-myst/issues/26) (math-swallow regex), [#27](https://github.com/QuantEcon/claude-latex-to-myst/issues/27) (pipeline ordering), and [#29](https://github.com/QuantEcon/claude-latex-to-myst/issues/29) (DESCITEM consuming nested `\item` markers), plus local TikZ rendering (commit `1cfb76d`).

### 3.2 Cross-references — 19 broken out of ~1080 (1.8%)

- **{eq}: 18 broken** — all are per-row labels inside multi-row `\begin{align}` blocks. Source has `\label{eq:X}` on individual `&...\\` rows of an align (`{eq:bayes_mean}`, `{eq:bayes_var}`, `{eq:cake_expand_disc}`, `{eq:cake_expand_V}`, `{eq:gp_mean}`, `{eq:gp_var}`, `{eq:iam_foc_c}`, `{eq:iam_foc_k}`, `{eq:iam_foc_mu}`, `{eq:iam_l1}`, `{eq:iam_l7}`, `{eq:irbc_adjcost_derivs}`, `{eq:irbc_foc_k_raw}`, `{eq:lstm_C}`, `{eq:tblock1}`, `{eq:tblock2}`, `{eq:temp_at}`, `{eq:temp_oc}`). MyST emits the math as `\begin{aligned}` but doesn't expose per-row anchors, so `{eq}` refs fall back to plain text. All 18 are actively cross-referenced elsewhere in the book; the refs show up unstyled. Recommend filing upstream — likely `convert_equations` could promote each per-row `\label{}` to a separate `(eq-X)=` anchor immediately above the math block, then strip the inline `\label{}`.
- **{ref}: 1 broken** — `lst-autodiff_euler` (referenced in `ch02_deqns.md:599`). Source has the label inside an `lstlisting` caption argument: `\begin{lstlisting}[caption={...}, label=lst:autodiff_euler]`. The label is lost during pandoc's listing conversion. Likely upstream-fixable in the listing preprocessor.
- **{numref}: 0 broken** ✅ — all figure and table refs resolve.

### 3.3 Citations — 5 colon-bearing keys lose their suffix in specific call sites

| Broken key | Full bib key | Where it breaks |
|---|---|---|
| `Bertsekas` | `Bertsekas:2000:DPO:517430` | `ch09_surrogates_gps.md:527` (one of multiple uses; other uses with full key are fine) |
| `Bilionis` | `Bilionis:2016wc` | `ch09_surrogates_gps.md:489` |
| `Rasmussen` | `Rasmussen:2005:GPM:1162254` | `ch09_surrogates_gps.md:6` |
| `marcet_marshall` | `marcet_marshall:94` | `ch02_deqns.md:89` |
| `ECTA` | `ECTA:ECTA1716` | `ch03_irbc.md:48, 432` (one site is fine, one is broken) |

Pandoc's citation parser appears to cut the bibkey at the first `:` in *one specific call style* (likely `\citet{}` inside a paragraph adjacent to text starting with a digit — symptomatic of a regex boundary issue). Every key has at least one *correct* occurrence too, which is why this only affects ~5 sites in total. Low priority — workaround would be to rewrite these specific call sites in source to use a colon-free alias, or file a tiny upstream issue.

The `unil` "broken citation" reported earlier was the mailto bug already tracked at downstream [#2](https://github.com/mmcky/Deep_Learning_for_Solving_And_Estimating_Dynamic_Economic_Models/issues/2) — not a real citation.

### 3.4 Tables — ~37 of 41 captioned tables likely under-rendered ⚠️

The upstream `convert_simple_tables` only converts **2-column** pandoc simple_tables to `{list-table}` directives (4 tables in the build). The other 37 captioned tables in source (mostly 3- to 5-column) survive in `mystmd/*.md` as pandoc's dash-rule simple_tables format — readable as raw text but not parsed by MyST into proper `table` AST nodes (`grep table mystmd/_build/site/content/*.json` shows only 4 `table` nodes across all chapters: 1 in appE, 1 in ch12, 2 in notation).

**Severity:** these tables likely still render in HTML (MyST falls back to raw rendering for un-recognized blocks) but lose semantic MyST structure — no `:caption:`, no `:numref:` integration, no themed styling. A separate validation pass that opens each rendered chapter page and visually inspects every table would confirm. For now, the tables are present and human-readable, just structurally raw.

This is a known scoping decision in the upstream converter (per its `convert_simple_tables` docstring: "Only 2-column tables are converted — wider tables have more layout nuance"). Extending to 3+ columns is upstream feature work.

### 3.5 Paragraph heads — 13 of 385 missing (3.4%) ⚠️

Source has 385 `\paragraph{...}` heads; MyST has 372 `##### ` heads. The 13-head gap likely traces to a few specific patterns — `\paragraph` inside a `tcolorbox` body, or `\paragraph` immediately after a `\subsubsection` boundary, both of which the upstream converter handles slightly differently. Not investigated in depth in this pass; deferred to step (5) of the visual review.

### 3.6 Captions with `\ref{}` resolve to wrong section numbers ⚠️

Spot-checked at `ch11_climate.md:926` (figure caption for `fig-cdice_vs_tcre`):

> "...is what makes the bilevel policy search of §**1.12** end-to-end feasible."

PDF (page 250) renders this as "§**11.12**". Source uses `\S\ref{sec:pareto_carbon_tax}`. The label `sec:pareto_carbon_tax` resolves to the OLG-IAM section, which is §11.12 in the book numbering but gets rendered as a chapter-unaware "1.12" by pandoc when it appears inside a `\caption{}` body. The non-caption uses of the same `\ref{}` (in chapter body text) get converted to `{ref}` directives that MyST resolves correctly.

This is a narrow bug class (`\ref` inside `\caption`). Worth a 5-minute scan of all figure captions to see how widespread. Not blocking — just produces slightly wrong section numbers in 0–N captions.

### 3.7 Math macros — full coverage ✅

All 16 math macros declared in the LaTeX preamble (`\x`, `\y`, `\z`, `\w`, `\h`, `\a`, `\bb`, `\W`, `\X`, `\Wh`, `\Wx`, `\Wo`, `\R`, `\E`, `\argmin`, `\argmax`) are mirrored in `mystmd/myst.yml`. KaTeX warnings during `myst build` (e.g. *"Could not convert TeX math `\x`, rendering as TeX"*) are pandoc-stage warnings, not build-stage failures; KaTeX renders the macros correctly at view time using the `myst.yml` declarations. Text macros `\tpath` and `\emphc` are handled via `config.yaml` preprocess rewrites (downstream issue [#9](https://github.com/mmcky/Deep_Learning_for_Solving_And_Estimating_Dynamic_Economic_Models/issues/9)). `\manuscriptmonthyear` is a date-stamp macro with no body content; safe to ignore.

### 3.8 Unlabeled `\begin{align}` blocks lose PDF numbering — known cosmetic divergence ℹ️

LaTeX auto-numbers every line of an unlabeled `\begin{align}` block (e.g. Adam optimizer equations 1.11–1.14 in §1.6.1, equation 1.15 cosine annealing in §1.6.3). MyST only numbers labeled equations, so these appear as an unnumbered `\begin{aligned}` block. Readers comparing PDF and HTML side-by-side will see "Equations 1.11–1.14 in PDF, no numbers in HTML." This is a source convention (no `\label`) interacting with MyST's numbering rules — not a conversion bug. Author can opt in to numbering by adding `\label{eq:X}` per row (which triggers the multi-row align label bug in §3.2 — so they're coupled).

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

### Round 1 status (closed)

| Item | Tracker | Status |
|---|---|---|
| 18 multi-row `\begin{align}` per-row `\label{}` lost | [#30](https://github.com/QuantEcon/claude-latex-to-myst/issues/30) | ✅ closed — 17/18 fixed (multline gap → #35) |
| `lstlisting` `label=lst:X` not propagated | [#31](https://github.com/QuantEcon/claude-latex-to-myst/issues/31) | ✅ closed — new postprocess pass added (caption-`}` gap → #36) |
| 5 citation keys with `:` lose suffix | [#32](https://github.com/QuantEcon/claude-latex-to-myst/issues/32) | ✅ closed — all 5 fixed (trailing-colon regression → #37) |
| `\ref{}` inside `\caption{}` produces wrong number | [#33](https://github.com/QuantEcon/claude-latex-to-myst/issues/33) | ✅ closed — section/chapter refs work; typed-prefix gap → #38 |
| Multi-column tables (>2 col) not converted to `{list-table}` (feature) | [#34](https://github.com/QuantEcon/claude-latex-to-myst/issues/34) | ⏳ open (feature request) |

### Round 2 follow-ups

| Item | Tracker | Status |
|---|---|---|
| `convert_pandoc_attr_code_blocks`: attrs regex chokes on `}` inside caption values | [#35](https://github.com/QuantEcon/claude-latex-to-myst/issues/35) | ✅ closed — quote-aware regex |
| `convert_citations`: trailing `:` regression | [#36](https://github.com/QuantEcon/claude-latex-to-myst/issues/36) | ✅ closed — trailing-`:` no longer captured |
| `convert_equations`: multline/gather coverage | [#37](https://github.com/QuantEcon/claude-latex-to-myst/issues/37) | ✅ closed — extended to all multi-row envs |
| Caption-ref typed dispatch (`{eq}`/`{numref}`/`{prf:ref}`) | [#38](https://github.com/QuantEcon/claude-latex-to-myst/issues/38) | ⏳ open — 11 caption refs still routed as generic `{ref}` |

### Round 4 follow-ups

| Item | Tracker | Status |
|---|---|---|
| `_apply_algorithm_markers`: `\label{alg:X}` as sibling of `\caption{}` not preserved | [#39](https://github.com/QuantEcon/claude-latex-to-myst/issues/39) | ✅ closed (partial — see #43) |
| `convert_html_figures::extract_caption`: HTML entities inside math break KaTeX | [#40](https://github.com/QuantEcon/claude-latex-to-myst/issues/40) | ✅ closed — works |

### Round 5 follow-ups

| Item | Tracker | Status | Severity |
|---|---|---|---|
| **P3a refactor: TIKZ_FIGURE_MAP empty at resolve_tikz_figures call time — every `tikz_overrides.py`-using book has all figures broken** | [#42](https://github.com/QuantEcon/claude-latex-to-myst/issues/42) | ✅ closed — `sys.modules` aliasing fix + subprocess regression test | (was critical) |
| #39 follow-up: `_extract_caption` doesn't handle `\caption{}\label{}` when both come BEFORE the algorithm body (the dominant LaTeX convention) | [#43](https://github.com/QuantEcon/claude-latex-to-myst/issues/43) | ⏳ open | medium |
| Multi-row `\begin{align}` with per-row `\tag*{...}` breaks KaTeX (Multiple \tag) — converter could drop, split, or convert | [#45](https://github.com/QuantEcon/claude-latex-to-myst/issues/45) | ⏳ open | low |
| `\,^\circ\mathrm{C}` breaks KaTeX (`Got group of unknown type: 'internal'`) — investigation only; likely KaTeX upstream | [#46](https://github.com/QuantEcon/claude-latex-to-myst/issues/46) | ⏳ open | low (note) |

### Not (yet) upstream-tracked

| Item | Layer | Notes |
|---|---|---|
| 13 `\paragraph` heads missing (§3.5) | not investigated | drill in during step-(5) visual review |
| Unlabeled `\begin{align}` loses PDF numbering (§3.8) | source convention | author choice — not a bug |

## 6. What this report does NOT cover

- **Paragraph-level content faithfulness** — no per-paragraph diff was attempted. The two spot-checks (§4.1, §4.2) cover ~3 pages of 329; structural counts cover everything else.
- **HTML rendering fidelity** — `myst build --html` succeeds, but a full visual walkthrough of every chapter in a browser hasn't happened yet. Step (5) of the PR #3 ordering ("Visual review of the deployed preview") is the natural place for that.
- **Bibliography ordering** — citation keys resolve, but the rendered references section ordering vs PDF wasn't compared.
- **Index** — the LaTeX source has 0 `\index{}` calls (stripped via `config.yaml`); no index to validate.
- **Cover page / title page / acknowledgments rendering** — frontmatter exists as separate `.md` files but wasn't visually checked.

## 7. How to reproduce this report

```bash
# From repo root
bash mystmd/convert.sh                      # regenerate .md from source
cd mystmd && myst build --html              # build the site
cd ..

# Structural counts (source side)
SRC=lecture_script/Deep_Learning_for_Solving_And_Estimating_Dynamic_Economic_Models.tex
grep -c '^\\chapter' "$SRC"
grep -c '^\\section' "$SRC"
grep -c '\\begin{tikzpicture' "$SRC"
grep -oE '\\label\{[^}]+\}' "$SRC" | sed -E 's/\\label\{([^:}]+):?.*/\1/' | sort | uniq -c

# Counts (MyST side)
grep -hF '```{figure}' mystmd/*.md | wc -l
grep -hoE '\(eq-[^)]+\)' mystmd/*.md | sort -u | wc -l
grep -hoE '\{numref\}`[^`]+`' mystmd/*.md | sort -u | wc -l

# Broken cross-refs
{
  grep -hE '^\([a-z][^)]+\)=$' mystmd/*.md | sed -E 's/^\(([^)]+)\)=$/\1/'
  grep -hE '^:name:' mystmd/*.md | sed 's/^:name: //'
  grep -hE '^label:' mystmd/*.md | sed -E 's/^label: *//'
} | sort -u > /tmp/anchors.txt
comm -23 \
  <(grep -hoE '\{ref\}`[^`]+`' mystmd/*.md | sed -E 's/.*`([^`]+)`/\1/' | sort -u) \
  /tmp/anchors.txt

# Build JSON inspection
python3 -c "
import json, sys
data = json.load(open(sys.argv[1]))
def walk(n,out):
  if isinstance(n,dict):
    if n.get('type')=='image': out.append(n.get('url','?'))
    for v in n.values(): walk(v,out)
  elif isinstance(n,list):
    for x in n: walk(x,out)
out=[]; walk(data, out)
print(f'{len(out)} images: {out[:5]}')
" mystmd/_build/site/content/ch01-intro.json
```
