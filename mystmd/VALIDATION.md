# MyST conversion — VALIDATION report

**Scope:** structural counts + targeted spot-checks of the MyST/HTML build against the LaTeX source and rendered PDF.
**Initial validation:** 2026-05-24 (commit `a26cddc`).
**Round 2 update:** 2026-05-25 — re-tally after upstream landed fixes for issues #30–#33.
**Round 3 update:** 2026-05-25 — re-tally after upstream landed fixes for follow-ups #35, #36, #37.
**Round 4 update:** 2026-05-25 — drill into deferred items; 2 new bugs filed (#39 algorithm label, #40 HTML entity in math); 2 prior "gaps" resolved as counting artifacts.
**Round 5 update:** 2026-05-25 — re-tally after upstream landed fixes for #38, #39, #40 *and* a major refactor (P3a series, 11 commits) splitting `postprocess.py` into a `transforms/` package. #38 and #40 work; #39 only partially (filed [#43](https://github.com/QuantEcon/claude-latex-to-myst/issues/43)). The P3a refactor introduced a critical regression: module double-load drops `TIKZ_FIGURE_MAP` content silently, breaking **all 88 figures** ([#42](https://github.com/QuantEcon/claude-latex-to-myst/issues/42) filed). Round 4 also under-reported KaTeX warnings — re-grep surfaces 9 pre-existing instances of `\,^\circ` and `\tag*` patterns that KaTeX can't handle (not a refactor regression).
**Round 6 update:** 2026-05-25 — #42 closed with the `sys.modules['postprocess']` aliasing fix (option B from the proposal). Re-tally: **all 88 figures restored**, all cross-ref classes resolve cleanly, citations clean. The fix is generic — every `transforms/` module that late-imports `postprocess` for state now resolves to the same instance, closing the whole class of bugs at once.
**Round 7 update:** 2026-05-27 — re-tally after fast-forward from `0e88cab` → `9649b0b` (six new commits, including #51/#55/#60 table unification, #49 nested-subfigure fast path, #50/#22 dropped-text-macro warner, #54 longtable extraction, and #63 `regen: false`). Headline wins: **all 41 captioned tables now render as `{table}` directives** (R6: 4 list-tables, 37 anchors-only) — issue #34 fully closed end-to-end. Headline gap: a methodology defect was discovered — **`validate.py` has been silently skipping every chapter in this book since R1**, because it looks for split-source `.tex` files in `lecture_script/` (which only ships the monolithic file; split outputs live in `mystmd/tmp/`). Building the html surfaces what `validate.py` missed: 96 unresolved `{prf:ref}\`ex-chN-M\`` exercise refs (labels inside `\item\label{ex:ch1:1}` are dropped by pandoc), 15 per-row `\label{}` collisions on `\begin{align}` blocks that MyST collapses to one anchor, and the 3rd algorithm renders as `{prf:definition}` because its source wrapper is `\begin{definitionbox}[Algorithm: …]` rather than `\begin{algorithm}`. None of these were introduced by R7 upstream — they are pre-existing, only newly visible.
**Branch:** `mystmd-conversion`
**Sources:**
- `lecture_script/Deep_Learning_for_Solving_And_Estimating_Dynamic_Economic_Models.tex` (24,557 source lines, 329-page PDF)
- `mystmd/*.md` (23 converted files: 12 chapters + 6 appendices + 5 frontmatter)
- `mystmd/_build/` (post `myst build --html`)
- `readings/bibliography.bib` (278 entries)
- `mystmd/myst.yml`, `mystmd/config.yaml`, `mystmd/tikz_overrides.py`

**Methodology (what this report does and doesn't do):** structural counts compare totals between source and output; per-anchor cross-ref checks identify broken references; spot-checks compare 2 PDF pages (ch01 §1.6 and ch11 §11.12) side-by-side with the converted markdown. This report does **not** do a full paragraph-level content diff — that would be infeasible at this scale. The goal is to give bounded confidence that the conversion is structurally faithful and to enumerate any remaining gaps with concrete examples.

---

## 1. Headline result (Round 7)

Upstream pin: `9649b0b` (fast-forward from `0e88cab`, six commits). Conversion ran clean; `myst build --html` ran with the warnings tabulated below.

| Dimension | Source | MyST | Match? | R6 | R5 | R4 | R3 | R2 | R1 |
|---|---|---|---|---|---|---|---|---|---|
| Chapters / sections / subsections / subsubsections | 22/144/81/5 | 22/144/81/5 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Paragraph heads / footnotes | 385 / 24 | 385 / 24 | ✅ | ✅ | ✅ | ✅ | ⚠️ glob | ⚠️ same | ⚠️ same |
| Figures rendered | 88 | 88 | ✅ | ✅ | ❌ #42 | ✅ | ✅ | ✅ | ✅ |
| Captioned tables — `{table}` directives / anchors | 41 / 41 | **41 / 41** | ✅ | ⚠️ #34 | ⚠️ same | ⚠️ same | ⚠️ same | ⚠️ same | ⚠️ same |
| `\label{alg:X}` → `{prf:algorithm}` round-trip | 3 labels | 2 of 3 (alg-nsdeqn → `prf:definition`, see §3.4) | ⚠️ new | ⚠️ #43 | ⚠️ #39 | n/a | n/a | n/a | n/a |
| `{numref}` cross-ref targets | — | 168 emitted, all resolve | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `{ref}` cross-ref targets (chapter/section) | — | clean | ✅ | ✅ | ⚠️ 11 | ⚠️ same | ⚠️ 12 | ⚠️ 1 | — |
| `{eq}` cross-ref targets | 186 src labels | 241 emitted; **15 per-row align collisions** (see §3.2) | ⚠️ new-surface | ✅ | ✅ | ✅ | ⚠️ 1 | ⚠️ 18 | — |
| `{prf:ref}` to exercises (appF + chapter cross-refs) | 87 labels | **96 unresolved** (`ex:ch1:1` in `\item` is dropped by pandoc, see §3.1) | ❌ new-surface | (missed by validate.py — see §3.0) | (missed) | (missed) | (missed) | (missed) | (missed) |
| Citation keys vs `references.bib` | 254 | all resolve except `unil`, `tf.function` (2; see §3.5) | ⚠️ minor | ✅ | ✅ | ✅ | ⚠️ 9 | ⚠️ 5 | — |
| New `_warn_dropped_text_macros` warning | — | 1 (`\checkmark` 1×, ch06) | ℹ️ new | n/a | n/a | n/a | n/a | n/a | n/a |
| KaTeX build errors (`⛔`) | — | 5 unique patterns / 10 instances in ch11+ch02 (see §3.3) | ⚠️ same as R5 | (under-counted) | (under-counted) | (under-counted) | n/a | n/a | n/a |
| `Could not convert TeX math` (pandoc, math-macro coverage) | — | ~22 (custom `\x \z \a \E \R \Wh \h ...` macros) | ⚠️ pre-existing | (missed) | (missed) | (missed) | n/a | n/a | n/a |
| Missing image files (`fig/restud_fig{11a,15a}.pdf`) | 2 refs | not in repo; need imagemagick to render PDF anyway | ⚠️ asset-gap | (missed) | (missed) | (missed) | n/a | n/a | n/a |

**Round 7 verdict — net positive, with one methodology fix and one large pre-existing gap newly visible:**

✅ **Closed by this round's upstream (R7):**
- **#34 / #51 / #55 / #60 — captioned tables fully arrive as `{table}` directives.** Source has 41 `\begin{table}` floats; output now has 42 `{table}` directives (the extra is the `notation` common-symbols table, also extracted via the unified `_apply_table_markers.py` path). All 41 carry their `:name: tab-…` anchor, all per-table captions and headers survive. R6 had only 4 `{list-table}` directives + 37 anchor-only tables. This is the largest single quality bump since R1.
- **#22 / #50 — `_warn_dropped_text_macros` runs and surfaces one usable warning** (`\checkmark` ×1 in ch06_ha_youngs). The fix is a one-line config addition — see §3.6.
- **#54 longtable** does not apply to this book (0 `\begin{longtable}` in source) but the path is now there for any future addition.
- **#49 nested subfigure fast path** does not apply (the book uses TikZ-rendered composites via `tikz_overrides.py`, not native `subfigure`).
- **#63 `regen: false`** is available; not used here (preferred over silent omission once we have curated files).

⚠️ **Methodology defect discovered (§3.0):** `validate.py` has been silently skipping every chapter in this book on all prior rounds. It looks for split-source `.tex` files in `source_dir: lecture_script/` and skips when `tex.exists()` is False — but `lecture_script/` only ships the monolithic source; the split per-stem `.tex` files live in `mystmd/tmp/`. So the per-chapter resolution loop never runs, no rows are printed, and the trailing "All counts match. All cross-references resolve and are well-typed" is a vacuous pass. This is why R2–R6 all reported clean cross-refs while `myst build` was actually emitting hundreds of unresolved-target warnings (most of which were also masked by the warner only firing once per unique label). This is upstream — filed in §4 as the highest-priority action item for R8.

❌ **Largest surfaced issue (§3.1):** 96 unique broken `{prf:ref}\`ex-chN-M\`` exercise refs across the chapter bodies and appF. Root cause: source has `\item\label{ex:ch1:1} …` inside `enumerate`; pandoc drops the `\label{}` (no MyST anchor lands on the list item), so when appF references `{prf:ref}\`ex-ch1-1\`` no target exists. There are 87 such labels in source; appF has 98 `{prf:ref}` to exercises, of which 96 are unresolved (the other 2 happen to alias chapter-level anchors). Triage in §4.

⚠️ **Other newly-surfaced issues** are detailed in §3 — they were all present in R6 but masked by the no-op validator and selective warning grep:
- §3.2 — 15 per-row `\label{}` collisions on `\begin{align}` blocks (`eq-iam_l2..l8` collapsed to `eq-iam_l1`; `eq-temp_oc` collapsed to `eq-temp_at`, etc.). MyST treats stacked `(eq-x)=` anchors above one `$$ \begin{aligned} … $$` block as duplicates for the same target.
- §3.3 — 5 unique KaTeX errors in ch11 (`Got group of unknown type: 'internal'`, `Multiple \tag`) plus 1 in ch02 (`Got function '\\' with no arguments as superscript`). The ch11 'internal' errors are a likely-new myst/KaTeX upstream behaviour; not previously catalogued.
- §3.4 — `alg:nsdeqn` (3rd algorithm) renders as `{prf:definition}` because the source uses `\begin{definitionbox}[Algorithm: Non-Stationary DEQN Training]`; the algorithm marker extractor triggers on `\begin{algorithm}` only.
- §3.5 — `Could not link citation with label "unil"` (preface) and `"tf.function"` (ch02_deqns). The `unil` lookalike is a `\cite` to a missing bib key (or a `\href` mis-parsed as a `cite`); `tf.function` looks like a `@tf.function` Python decorator that pandoc swallowed as a citation key.

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

### 3.0 `validate.py` has been a no-op for this book since R1 — methodology defect ❌

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

### Round 7 — NEW items to file upstream

| # | Item | Triage layer | Severity | Notes |
|---|---|---|---|---|
| R7-1 | `validate.py` silently skips every chapter when `preprocess.split:` is used (§3.0) | Layer 2 | **critical** (validator no-op) | Highest-priority R8 item. Without this, all subsequent rounds operate blind on cross-ref breakage. |
| R7-2 | 87 `\item\label{ex:chN:M}` exercise labels dropped by pandoc → 96 broken `{prf:ref}` (§3.1) | Layer 2 | **high** (largest single-class bug) | Mirror the existing `_apply_description_markers.py` pattern for `enumerate`-of-exercises; emit either an `(ex-chN-M)=` anchor or a full `{prf:exercise}` directive. |
| R7-3 | Per-row align `\label{}` collisions — only first label survives (§3.2) | Layer 2 | medium (10 dead `{eq}` refs) | Convert multi-row `aligned` blocks to `{math}` directive with per-row `:label:`, or split into one `$$ … $$` per row. Related to closed [#30](https://github.com/QuantEcon/claude-latex-to-myst/issues/30) but at a different layer. |
| R7-4 | `\begin{definitionbox}[Algorithm: …]` not auto-routed to `prf:algorithm` (§3.4) | Layer 1 (local) or Layer 2 (general) | low | Easier as a one-line source fix in this book; upstream change worth a CHANGELOG note for any book that adopts the dp1/dp2 `definitionbox` convention. |

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
| R5 | Per-row `\tag*` breaks KaTeX (Multiple \tag) | [#45](https://github.com/QuantEcon/claude-latex-to-myst/issues/45) | ⏳ open (R7: same 1 instance in ch11) |
| R5 | `\,^\circ\mathrm{C}` breaks KaTeX (`'internal'` group) | [#46](https://github.com/QuantEcon/claude-latex-to-myst/issues/46) | ⏳ open (R7: now 7 ch11 instances — broader than R5's "8 of `\,^\circ` only", but same KaTeX limitation class) |

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
