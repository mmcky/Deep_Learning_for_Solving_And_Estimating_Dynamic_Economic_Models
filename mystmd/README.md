# MyST Markdown rendering

This directory holds the MyST Markdown rendering of the lecture script, generated from the LaTeX source in [`../lecture_script/`](../lecture_script/) by [`QuantEcon/claude-latex-to-myst`](https://github.com/QuantEcon/claude-latex-to-myst).

The committed `*.md` files are **conversion output**, not human-authored. Edits should land in the LaTeX source (and propagate via re-conversion); editing a `.md` directly will be overwritten on the next run.

## Regenerating the output

```bash
bash mystmd/convert.sh                 # all chapters
bash mystmd/convert.sh ch01_intro      # one stem
bash mystmd/convert.sh --build         # convert + myst build --html
```

Prerequisites: [`uv`](https://github.com/astral-sh/uv) (used to bootstrap a recent Python — falls back to `python3` if absent) and `pandoc >= 3.0`. The wrapper script clones `claude-latex-to-myst` into [`../_tools/claude-latex-to-myst/`](../_tools/) (gitignored, self-managed) at the SHA pinned in [`.tool-version`](.tool-version).

## Local preview

```bash
cd mystmd
myst start                             # dev server on http://localhost:3000
myst build --html                      # static site into _build/html/
```

Requires the [mystmd CLI](https://mystmd.org/guide/installing). The repo also ships a GitHub Actions workflow ([`../.github/workflows/deploy-myst.yml`](../.github/workflows/deploy-myst.yml)) that builds and publishes on every push to `mystmd-conversion`.

**Deployed preview:** https://mmcky.github.io/Deep_Learning_for_Solving_And_Estimating_Dynamic_Economic_Models/

## What's in this directory

| Path | Role | Tracked? |
|---|---|---|
| `convert.sh` | Entry point — bootstraps the tool checkout, runs preprocess + pandoc + postprocess | ✅ |
| `.tool-version` | Pins `claude-latex-to-myst` to a specific SHA | ✅ |
| `config.yaml` | Per-book conversion config (chapter list, preprocess rewrites, TikZ map filename, extra envs, …) | ✅ |
| `myst.yml` | mystmd renderer config (project layout, KaTeX math macros) | ✅ |
| `tikz_overrides.py` | Map from `fig-…` label → rendered SVG path; written by `scripts/render_tikz.py` and read by the upstream postprocess | ✅ |
| `scripts/render_tikz.py` | Discovers `\begin{tikzpicture}` blocks in source, compiles to SVG via pdflatex + pdf2svg, updates `tikz_overrides.py` | ✅ |
| `figures/` | Compiled SVGs / curated raster figures | ✅ |
| `references.bib` | Bibliography (mirror of `../readings/bibliography.bib`, copied during convert) | ✅ |
| `index.md`, `preface.md`, `notation.md`, `ch??_*.md`, `appA…F_*.md` | Conversion output — 23 files (12 chapters + 6 appendices + 5 frontmatter) | ✅ |
| `VALIDATION.md` | Per-round validation report (structural counts, build warnings, round-to-round deltas) | ✅ |
| `tmp/` | Per-chapter `.tex` slices produced by `preprocess.split:`, plus pandoc intermediate markdown | gitignored |
| `_build/` | mystmd HTML output | gitignored |
| `_tools/claude-latex-to-myst/` (parent dir) | Vendored tool checkout | gitignored |

## Bumping the tool version

Edit [`.tool-version`](.tool-version) to the new SHA (or a branch name like `main`), re-run `bash mystmd/convert.sh`, and check the diff. Each round in [`VALIDATION.md`](VALIDATION.md) documents one such bump with the resulting build state and any new issues filed.

> **These two pins move together.** `.tool-version` (which converter generates the markdown) and the `git checkout qe-v9` in [`../.github/workflows/deploy-myst.yml`](../.github/workflows/deploy-myst.yml) (which renderer builds the site) are coupled as of Round 26. Since [QuantEcon/claude-latex-to-myst#201](https://github.com/QuantEcon/claude-latex-to-myst/pull/201) the converter emits non-starred `align` verbatim and relies on the QuantEcon fork's per-row equation numbering ([QuantEcon/mystmd#81](https://github.com/QuantEcon/mystmd/pull/81), released as `qe-v9`). Bumping the converter while the workflow still builds an older tag does **not** break the site — it silently renders the *previous* equation numbering while the converter's changelog claims the numbering matches the printed PDF. Check the renderer floor whenever you move `.tool-version`, and diff the built equation numbers against the PDF rather than against the previous build.

## Known follow-ups

Open, and each blocked on something specific:

| Issue | What it tracks | Blocked on |
|---|---|---|
| [#19](https://github.com/mmcky/Deep_Learning_for_Solving_And_Estimating_Dynamic_Economic_Models/issues/19) | 24 starred headings (`\section*{Further Reading}` / `{Exercises}`, ch03's `Validation Protocol`) still carry section numbers they should not. Needs a converter bump **and** `qe-v10` in one commit — on `qe-v9` an `{.unnumbered}` attribute block leaks as literal braces into the heading text and its slug. | [QE#160](https://github.com/QuantEcon/claude-latex-to-myst/issues/160) emitting `{.unnumbered}` on starred sections |
| [#15](https://github.com/mmcky/Deep_Learning_for_Solving_And_Estimating_Dynamic_Economic_Models/issues/15) | Retire **Class L**, the local escape for 10 line-leading `(a)`/`(i)` enumerate markers. | book adopting `quantecon-theme.mystmd` (the fix is in v2.2.0; the stock `book-theme` still drops `style`/`delimiter` — [QuantEcon/mystmd#74](https://github.com/QuantEcon/mystmd/issues/74)) |
| [#8](https://github.com/mmcky/Deep_Learning_for_Solving_And_Estimating_Dynamic_Economic_Models/issues/8) | Optional CI convert-and-diff check that fails if committed `.md` drifts from what the converter produces. | nothing — deferred as optional |
| [#16](https://github.com/mmcky/Deep_Learning_for_Solving_And_Estimating_Dynamic_Economic_Models/issues/16) | Migrating this work upstream: a `myst/` folder alongside the LaTeX sources, AI-licensing permissions. | upstream decision |

Also open upstream, with no local action required: [QE#207](https://github.com/QuantEcon/claude-latex-to-myst/issues/207) — a bridging `,` is dropped when a labelled `align` row is split into a standalone block but kept when the row fuses, so ch11's three sibling FOCs end `= 0` / `= 0,` / `= 0.` (see [`VALIDATION.md`](VALIDATION.md) Round 26).

Resolved, kept here for provenance: [#1](https://github.com/mmcky/Deep_Learning_for_Solving_And_Estimating_Dynamic_Economic_Models/issues/1) (`L{<width>}` column types) and [#2](https://github.com/mmcky/Deep_Learning_for_Solving_And_Estimating_Dynamic_Economic_Models/issues/2) (`mailto` href misparsed) closed by source changes in Round 20; [#13](https://github.com/mmcky/Deep_Learning_for_Solving_And_Estimating_Dynamic_Economic_Models/issues/13) (alg-nsdeqn wrapper; `@tf.function` escaped) and [#14](https://github.com/mmcky/Deep_Learning_for_Solving_And_Estimating_Dynamic_Economic_Models/issues/14) (`restud_fig11a/15a` ship as PNGs) in Round 16; [#17](https://github.com/mmcky/Deep_Learning_for_Solving_And_Estimating_Dynamic_Economic_Models/issues/17) (the `qe-v9` pin coupling) in Round 26.
