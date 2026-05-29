#!/usr/bin/env python3
"""Render inline TikZ figures from the LaTeX source to SVG.

Auto-discovers ``\\begin{figure}...\\end{figure}`` blocks that contain
``\\begin{tikzpicture}`` in the source, extracts the label + TikZ
content, compiles each via pdflatex + pdf2svg, and writes:

  - mystmd/figures/<label>.svg    (one per figure)
  - mystmd/tikz_overrides.py      (TIKZ_FIGURE_MAP populated)

The next ``bash mystmd/convert.sh`` run then sees the overrides and
swaps each ``{admonition} Figure (TikZ — needs manual conversion)``
placeholder for a real ``{figure}`` directive.

Usage:
  python3 mystmd/scripts/render_tikz.py             # discover + render all
  python3 mystmd/scripts/render_tikz.py --list      # discover only, no compile
  python3 mystmd/scripts/render_tikz.py --figure fig-dl_enablers
  python3 mystmd/scripts/render_tikz.py --force     # re-render even if up-to-date

Requires: pdflatex (TeX Live), pdf2svg.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
MYSTMD_DIR = SCRIPT_DIR.parent
REPO_DIR = MYSTMD_DIR.parent
SOURCE_DIR = REPO_DIR / "lecture_script"
SOURCE_TEX = (
    SOURCE_DIR
    / "Deep_Learning_for_Solving_And_Estimating_Dynamic_Economic_Models.tex"
)
FIGURES_DIR = MYSTMD_DIR / "figures"
OVERRIDES_PY = MYSTMD_DIR / "tikz_overrides.py"

# Search path for \includegraphics filenames, mirroring the source's
# \graphicspath{}. Listed in lookup order: bare filename first, then
# subdirectories under lecture_script/fig/. Found files are copied
# into mystmd/figures/ so MyST serves them at a stable relative path.
GRAPHICSPATH = [
    SOURCE_DIR / "fig",
    SOURCE_DIR / "fig" / "chapter11",
]

# Standalone preamble — mirrors the book's TikZ-relevant packages and
# math macros so figures compile out-of-context. lmodern + pdflatex
# matches the source (not XeLaTeX/STIX like dp1).
# varwidth=16cm matches the book's body \textwidth (A4 with 2.5cm margins).
# Using \maxdimen here overflows pgfplots width=0.62\textwidth calculations;
# the explicit cm value gives pgfplots a sensible reference for relative widths.
STANDALONE_TEMPLATE = r"""\documentclass[border=5pt,varwidth=16cm]{standalone}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage{amsmath,amssymb,amsfonts}
\usepackage{bm}
\usepackage{enumitem}
\usepackage{tikz}
\usetikzlibrary{shapes,arrows.meta,positioning,calc,fit,backgrounds,patterns,decorations.pathreplacing}
\usepackage{pgfplots}
\pgfplotsset{compat=1.18}
\usepgfplotslibrary{fillbetween}
\usepackage{xcolor}
% Colors used by TikZ figures (mirrored from source preamble).
\definecolor{uzhblue}{rgb}{0,0,0.5}
\definecolor{uzhgreylight}{RGB}{236,238,241}
\definecolor{uzhgreydark}{RGB}{81,86,94}
\definecolor{harvardcrimson}{RGB}{153,0,0}
\definecolor{darkgreen}{RGB}{0,100,0}
\definecolor{darkred}{RGB}{139,0,0}
\definecolor{softblue}{RGB}{70,130,180}
\definecolor{softorange}{RGB}{230,159,0}
\definecolor{softgreen}{RGB}{0,158,115}
% Math macros (mirrored from source preamble).
\newcommand{\x}{\bm{x}}
\newcommand{\h}{\bm{h}}
\newcommand{\y}{\bm{y}}
\newcommand{\w}{\bm{w}}
\newcommand{\bb}{\bm{b}}
\newcommand{\z}{\bm{z}}
\newcommand{\W}{\bm{W}}
\newcommand{\Wh}{\bm{W}_{hh}}
\newcommand{\Wx}{\bm{W}_{xh}}
\newcommand{\Wo}{\bm{W}_{hy}}
\newcommand{\X}{\bm{X}}
\renewcommand{\a}{\bm{a}}
\newcommand{\R}{\mathbb{R}}
\newcommand{\E}[1]{\mathbb{E}\!\left[#1\right]}
\DeclareMathOperator*{\argmin}{arg\,min}
\DeclareMathOperator*{\argmax}{arg\,max}
\begin{document}
%CONTENT%
\end{document}
"""


@dataclass
class Figure:
    label: str          # 'fig-dl_enablers' (markdown-style, colon→dash)
    raw_label: str      # 'fig:dl_enablers' (as-in-source)
    content: str        # tikz body, ready to drop into the standalone template


@dataclass
class IncludedImage:
    """A \\begin{figure}…\\end{figure} block that uses \\includegraphics
    rather than TikZ. The upstream converter misclassifies these as TikZ
    admonitions (it's a non-nested \\<figure>\\</figure> with \\<img\\> in
    pandoc's output, and Pass 2 of convert_html_figures doesn't check for
    an image source — see claude-latex-to-myst upstream).
    Mapping them through TIKZ_FIGURE_MAP swaps the admonition for a
    real {figure} pointing at the already-committed image file.
    """
    label: str          # 'fig-loss_kernels'
    raw_label: str      # 'fig:loss_kernels'
    src: str            # 'loss_kernel_convergence.png' (as in \includegraphics)


def strip_braced(text: str, cmd_re: str) -> str:
    """Strip ``\\cmd{...}`` with brace-balanced argument matching.

    Plain regex misses nested braces inside arguments (captions often
    contain ``\\textbf{...}``, citations, etc.). This walks the string
    manually so the whole argument is removed.
    """
    out = []
    i = 0
    pattern = re.compile(cmd_re + r"\{")
    while i < len(text):
        m = pattern.search(text, i)
        if not m:
            out.append(text[i:])
            break
        out.append(text[i:m.start()])
        depth = 1
        j = m.end()
        while j < len(text) and depth:
            ch = text[j]
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
            j += 1
        i = j
    return "".join(out)


def extract_tikz_content(figure_block: str) -> str:
    """Strip surrounding figure scaffolding; leave the TikZ content for
    standalone compilation. Keeps minipage / center wrappers that may
    matter for multi-panel layout.
    """
    content = figure_block
    content = re.sub(r"\\begin\{figure\}(?:\[[^\]]*\])?", "", content)
    content = re.sub(r"\\end\{figure\}", "", content)
    content = strip_braced(content, r"\\caption\*?")
    content = strip_braced(content, r"\\label")
    content = re.sub(r"\\centering\b", "", content)
    return content.strip()


def discover(source: str) -> tuple[list[Figure], list[IncludedImage]]:
    """Walk \\begin{figure}…\\end{figure} blocks. Each block is one of:

    - TikZ figure: contains \\begin{tikzpicture} → returned as Figure
      (to be rendered to SVG by this script).
    - Included-image figure: contains \\includegraphics but no
      tikzpicture → returned as IncludedImage (no rendering; the file
      already exists in mystmd/figures/, we just need a map entry).

    Multi-panel TikZ figures (multiple tikzpicture/minipage inside one
    \\begin{figure}) become one Figure — rendered to a single composite
    SVG matching the single ``:name:`` label on the markdown placeholder.
    """
    figures: list[Figure] = []
    images: list[IncludedImage] = []
    fig_re = re.compile(r"\\begin\{figure\}.*?\\end\{figure\}", re.DOTALL)
    label_re = re.compile(r"\\label\{(fig:[^}]+)\}")
    incl_re = re.compile(r"\\includegraphics(?:\[[^\]]*\])?\{([^{}]+)\}")
    seen_labels: set[str] = set()
    for m in fig_re.finditer(source):
        block = m.group(0)
        label_m = label_re.search(block)
        if not label_m:
            continue
        raw_label = label_m.group(1)
        label = raw_label.replace(":", "-")
        if label in seen_labels:
            print(f"  WARN: duplicate label {raw_label!r}, second occurrence ignored")
            continue
        if r"\begin{tikzpicture}" in block:
            seen_labels.add(label)
            figures.append(Figure(
                label=label,
                raw_label=raw_label,
                content=extract_tikz_content(block),
            ))
            continue
        incl_m = incl_re.search(block)
        if incl_m:
            seen_labels.add(label)
            images.append(IncludedImage(
                label=label,
                raw_label=raw_label,
                src=incl_m.group(1).strip(),
            ))
    return figures, images


def render(fig: Figure, force: bool = False) -> str:
    """Returns one of: 'rendered', 'skipped', 'failed'."""
    out_svg = FIGURES_DIR / f"{fig.label}.svg"
    if not force and out_svg.exists():
        if out_svg.stat().st_mtime > SOURCE_TEX.stat().st_mtime:
            print(f"  SKIP {fig.label} (up to date)")
            return "skipped"
    print(f"  Render {fig.label}...")
    doc = STANDALONE_TEMPLATE.replace("%CONTENT%", fig.content)
    with tempfile.TemporaryDirectory(prefix="tikz_render_") as td:
        td_path = Path(td)
        tex_file = td_path / f"{fig.label}.tex"
        pdf_file = td_path / f"{fig.label}.pdf"
        tex_file.write_text(doc, encoding="utf-8")

        result = subprocess.run(
            [
                "pdflatex",
                "-interaction=nonstopmode",
                "-halt-on-error",
                f"-output-directory={td_path}",
                str(tex_file),
            ],
            capture_output=True,
            text=True,
            cwd=str(td_path),
            timeout=120,
        )
        if result.returncode != 0 or not pdf_file.exists():
            print(f"  ERROR: pdflatex failed for {fig.label}")
            for line in result.stdout.splitlines()[-20:]:
                print(f"    {line}")
            return "failed"

        FIGURES_DIR.mkdir(parents=True, exist_ok=True)
        result = subprocess.run(
            ["pdf2svg", str(pdf_file), str(out_svg)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            print(f"  ERROR: pdf2svg failed for {fig.label}: {result.stderr}")
            return "failed"

    if out_svg.stat().st_size < 100:
        print(f"  ERROR: {fig.label} SVG too small (likely corrupt)")
        out_svg.unlink()
        return "failed"
    print(f"  OK     {fig.label} -> figures/{fig.label}.svg")
    return "rendered"


def resolve_image(src: str) -> Path | None:
    """Resolve a \\includegraphics filename to a real file under
    mystmd/figures/, copying from the source tree if needed.

    Strips any leading ``fig/`` (which is the source's explicit subdir
    prefix; mystmd/figures/ is flat). Then:
    1. If the basename already exists under mystmd/figures/, use it.
    2. Otherwise search GRAPHICSPATH for the basename and copy it in.
    3. Return ``None`` if the file can't be located.
    """
    src = src.strip()
    # Strip a leading 'fig/' or './fig/' (source-tree convention)
    src = re.sub(r"^\./?", "", src)
    if src.startswith("fig/"):
        src = src[len("fig/"):]
    basename = Path(src).name
    target = FIGURES_DIR / basename
    if target.exists():
        return target
    for d in GRAPHICSPATH:
        candidate = d / basename
        if candidate.exists():
            FIGURES_DIR.mkdir(parents=True, exist_ok=True)
            shutil.copy2(candidate, target)
            print(f"  Copied {candidate.relative_to(REPO_DIR)} -> figures/{basename}")
            return target
    return None


def write_overrides(figures: list[Figure], images: list[IncludedImage]) -> None:
    """Emit ``mystmd/tikz_overrides.py`` keyed by every figure with a
    resolvable image. Auto-generated; safe to overwrite.

    Two sources:
    - TikZ figures: include only those with a rendered SVG present.
    - Included images: include only those whose file is present under
      mystmd/figures/. Skipped silently if the file isn't committed.
    """
    rendered = [
        (f.label, f"figures/{f.label}.svg")
        for f in figures
        if (FIGURES_DIR / f"{f.label}.svg").exists()
    ]
    included: list[tuple[str, str]] = []
    missing_images: list[IncludedImage] = []
    for img in images:
        resolved = resolve_image(img.src)
        if resolved is None:
            missing_images.append(img)
            continue
        included.append((img.label, f"figures/{resolved.name}"))
    for img in missing_images:
        print(f"  WARN: image {img.src!r} for {img.label} not found in figures/ or graphicspath")

    all_entries = sorted(rendered + included)
    longest = max((len(repr(label)) for label, _ in all_entries), default=0)
    entries = "\n".join(
        f"    {repr(label):<{longest}}: ({path!r}, None),"
        for label, path in all_entries
    )
    text = (
        '"""TikZ figure overrides — auto-generated by mystmd/scripts/render_tikz.py.\n'
        "\n"
        "Do NOT hand-edit; the render script overwrites this file on every run.\n"
        "Consumed by the shared `claude-latex-to-myst` pipeline via the\n"
        "`tikz_overrides:` key in `mystmd/config.yaml`. The postprocess maps\n"
        "each placeholder admonition (keyed by its `:name:` label) to the\n"
        "image path below — both TikZ-rendered SVGs and pre-committed\n"
        "raster/vector images that the upstream postprocess currently\n"
        "misclassifies as TikZ.\n"
        '"""\n'
        "\n"
        "TIKZ_FIGURE_MAP: dict[str, tuple[str, str | None]] = {\n"
        f"{entries}\n"
        "}\n"
        "\n"
        "TIKZCD_INLINE_MAP: dict[str, list[dict]] = {}\n"
    )
    OVERRIDES_PY.write_text(text, encoding="utf-8")
    print(
        f"  Wrote {OVERRIDES_PY.relative_to(REPO_DIR)} "
        f"({len(rendered)} TikZ + {len(included)} image entries)"
    )


def check_tools() -> None:
    missing = []
    for cmd in ("pdflatex", "pdf2svg"):
        if subprocess.run(["which", cmd], capture_output=True).returncode != 0:
            missing.append(cmd)
    if missing:
        sys.stderr.write(f"ERROR: missing required commands: {', '.join(missing)}\n")
        sys.stderr.write("Install: brew install --cask mactex && brew install pdf2svg\n")
        sys.exit(1)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--list", action="store_true", help="discover only; no compile")
    ap.add_argument("--force", action="store_true", help="re-render even if up-to-date")
    ap.add_argument("--figure", help="render only the named label (e.g. fig-dl_enablers)")
    args = ap.parse_args()

    if not SOURCE_TEX.exists():
        sys.stderr.write(f"ERROR: source not found: {SOURCE_TEX}\n")
        sys.exit(1)

    source = SOURCE_TEX.read_text(encoding="utf-8")
    all_figures, all_images = discover(source)
    print(
        f"Discovered {len(all_figures)} TikZ figure(s) "
        f"and {len(all_images)} \\includegraphics figure(s) in {SOURCE_TEX.name}."
    )

    if args.list:
        for f in all_figures:
            status = "EXISTS" if (FIGURES_DIR / f"{f.label}.svg").exists() else "MISSING"
            print(f"  [{status}] tikz  {f.label}   (\\label{{{f.raw_label}}})")
        for img in all_images:
            status = "EXISTS" if (FIGURES_DIR / img.src).exists() else "MISSING"
            print(f"  [{status}] image {img.label}   ({img.src})")
        return

    check_tools()

    targets = all_figures
    if args.figure:
        targets = [f for f in all_figures if f.label == args.figure]
        if not targets:
            sys.stderr.write(f"ERROR: no TikZ figure with label {args.figure!r}\n")
            sys.stderr.write(
                f"Available: {', '.join(f.label for f in all_figures[:10])}"
                f"{'...' if len(all_figures) > 10 else ''}\n"
            )
            sys.exit(1)

    rendered = skipped = failed = 0
    for f in targets:
        status = render(f, force=args.force)
        if status == "rendered":
            rendered += 1
        elif status == "skipped":
            skipped += 1
        else:
            failed += 1

    # Always regenerate the overrides file against the full discovery set,
    # not just the filtered subset — so a --figure run doesn't shrink the map.
    write_overrides(all_figures, all_images)

    print(f"\nDone: {rendered} rendered, {skipped} skipped, {failed} failed")
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
