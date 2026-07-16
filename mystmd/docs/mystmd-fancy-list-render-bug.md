# Upstream bug report — drafted, NOT YET FILED

**Target repo:** `QuantEcon/mystmd`

**Suggested title:** Fancy ordered lists (#50): HTML renderer drops `style`/`delimiter`, so (a)/(i) markers render as 1./2./3.

File it with:

    gh issue create --repo QuantEcon/mystmd \
      --title "Fancy ordered lists (#50): HTML renderer drops style/delimiter, so (a)/(i) markers render as 1./2./3." \
      --body-file mystmd/docs/mystmd-fancy-list-render-bug.md

Once filed, replace the `NOT YET FILED` note in `config.yaml` (Class L) with the real issue number, and delete this file.

---

## Summary

`#50` (fancy ordered lists) parses alphabetic/roman/parenthesized markers correctly into the AST, but the HTML renderer drops the `style` and `delimiter` properties, so a `(a)`/`(i)` list renders with plain decimal markers (`1.`, `2.`, `3.`).

The parse is right; only the render is lossy. That makes the feature a silent downgrade for documents that use parenthesized markers as literal text: on a build without `#50` the markers survive as paragraph text, while on a build with `#50` they are consumed by the list parser and then rendered as decimals — so the labels disappear from the output entirely.

## Reproduction

Minimal `index.md`:

```markdown
(a) Alpha item body.

(i) Roman item body.
```

Build with `myst build --html`.

## Actual

The AST (`_build/html/index.json`) captures the markers correctly:

| node | properties |
| --- | --- |
| list 1 | `"ordered": true, "start": 1, "style": "lower-alpha", "delimiter": "parens"` |
| list 2 | `"ordered": true, "start": 1, "style": "lower-roman", "delimiter": "parens"` |

But the emitted HTML discards both:

```html
<ol start="1"><li><p>Alpha item body.</p></li></ol>
<ol start="1"><li><p>Roman item body.</p></li></ol>
```

Rendered result: `1.` and `1.` — the `(a)` and `(i)` styling is lost.

## Expected

The HTML should honour `style` and `delimiter` — e.g. `<ol type="a">` / `<ol type="i">` plus parenthesized delimiter styling (`list-style-type: lower-alpha` with a parens marker, or an equivalent `::marker` treatment) — so the rendered markers read `(a)` and `(i)`.

## Version

Reproduced on `qe-v8` (`v1.10.1`). Not present on `qe-v6`, which predates `#50`: there the markers are left as literal paragraph text, which is why this only surfaces on upgrade.

## Impact

Found while upgrading the QuantEcon *Deep Learning for Solving and Estimating Dynamic Economic Models* book build from `qe-v6` to `qe-v8`: 10 custom enumerate labels (`a`, `b`, `c`, `i`, `ii`, `iii`) silently changed to `1./2./3.` across two chapters. Worked around downstream by escaping the parens (`\(a\)`) to suppress the list parse and keep the literal text, but that gives up the semantic list — the designed path is the converter's `postprocess.enumerate_style` (claude-latex-to-myst `#111`), which explicitly depends on fancy-list support rendering correctly here.
