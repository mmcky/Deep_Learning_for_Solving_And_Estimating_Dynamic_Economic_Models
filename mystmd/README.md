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

- LaTeX source-side suggestions: [#1](https://github.com/mmcky/Deep_Learning_for_Solving_And_Estimating_Dynamic_Economic_Models/issues/1) (`L{<width>}` column types), [#2](https://github.com/mmcky/Deep_Learning_for_Solving_And_Estimating_Dynamic_Economic_Models/issues/2) (`mailto` href misparsed). Resolved in R16 by upstream source changes: [#13](https://github.com/mmcky/Deep_Learning_for_Solving_And_Estimating_Dynamic_Economic_Models/issues/13) (alg-nsdeqn wrapper now `\begin{algorithm}`; `@tf.function` escaped) and [#14](https://github.com/mmcky/Deep_Learning_for_Solving_And_Estimating_Dynamic_Economic_Models/issues/14) (`restud_fig11a/15a` now ship as PNGs) — see [`VALIDATION.md`](VALIDATION.md) Round 16.
- Optional CI: [#8](https://github.com/mmcky/Deep_Learning_for_Solving_And_Estimating_Dynamic_Economic_Models/issues/8) — a convert-and-diff check that fails if committed `.md` files drift from what the converter produces.
