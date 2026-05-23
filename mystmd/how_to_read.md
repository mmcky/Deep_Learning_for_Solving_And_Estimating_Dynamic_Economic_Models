---
title: "How to Read This Script"
label: how-to-read-this-script
---

The four methodologies sketched in the Preface, namely DEQNs, PINNs, deep surrogates with Gaussian processes, and GP-based dynamic programming, share a common philosophy but differ in their prerequisites, dependencies, and natural reading order. This short orientation translates that conceptual map into a practical reading plan: how the chapters, companion notebooks, notation tables, and visual conventions fit together, and how the manuscript can be used either as a sequential textbook for a reader encountering these tools for the first time or as a reference one can drop into at the level of a single method.

Although the live course groups the material into eight classroom sessions, the manuscript is organized by conceptual dependency rather than by calendar time. Each main chapter follows the same rhythm: the economic problem first, then the computational obstacle that classical methods leave open, then the neural-network or GP construction that closes it, then the algorithmic implementation, and finally exercises and notebooks that turn the method into running code. The notebooks are not an optional appendix; they are part of the exposition. They make explicit which residuals are minimized, which variables enter as states or pseudo-states, how expectations are approximated, and how accuracy is checked in practice, and the chapters are written on the assumption that the reader will at least skim the corresponding code.

##### Cover to cover.

A reader new to both deep learning and computational economics should read the script in order. Chapter 1 supplies the machine-learning vocabulary used everywhere else: losses, gradients, backpropagation, architectures, optimization, and generalization. Chapters 2--6 then develop the discrete-time equilibrium toolkit, moving from representative-agent DEQNs to international business cycles, loss balancing, overlapping generations, and heterogeneous-agent distributions. Chapters 7--8 shift from conditional expectations to continuous-time PDE residuals, first through PINNs and then through HJB--KFE systems. Chapters 9--10 introduce surrogate models, Gaussian processes, active subspaces, and structural estimation. Chapter 11 uses these pieces in a climate-economics application, and Chapter 12 closes by comparing methods and highlighting open problems.

##### Selective reading paths.

Readers who already know part of the material can take a shorter route, but the dependencies still matter:

- **Discrete-time equilibrium methods:** read Chapters 1--6. This path covers the DEQN template, expectation approximation, high-dimensional DSGE examples, loss normalization, OLG models, and histogram-based heterogeneous-agent distributions.

- **Continuous-time methods:** read Chapter 1 for neural-network basics, Chapter 7 for PINNs and PDE residuals, and Chapter 8 for the continuous-time heterogeneous-agent HJB--KFE system. Chapter 6 is useful background if the distribution $\mu_t$ is unfamiliar.

- **Surrogates and estimation:** read Chapter 1 for optimization and approximation, Chapter 9 for deep surrogates, GPs, active subspaces, and GP-based dynamic programming, and Chapter 10 for the SMM pipeline. Chapter 2 is the minimum DEQN background for the Brock--Mirman examples used there.

- **Climate economics:** read Chapter 11 together with Chapter 2 for DEQN solution logic and Chapter 9 for surrogate-based uncertainty quantification. The climate chapter is written as an application chapter, not as a replacement for those methodological chapters.

These reading paths are minimum self-sufficient sets: chapters not listed are not strictly required for the path, but several later sections cross-reference earlier chapters more deeply, and the chapter introductions flag those dependencies explicitly when they arise.

##### Code and reproducibility.

Each chapter is accompanied by executable Jupyter notebooks that implement the methods described in the text. The notebooks are listed at the end of each chapter and are available on the companion GitHub repository.[^1] The classroom-scale examples are intentionally smaller than research-scale calibrations: their role is to make the residuals, training loops, diagnostics, and validation logic transparent. Production-scale settings, when relevant, are noted in comments within the notebooks. A useful workflow is to read the chapter once for the economic and mathematical structure, run or inspect the notebook to see the implementation, and then return to the chapter's exercises to check whether the approximation and validation choices are understood.

##### Notation and cross-references.

The notation tables following this orientation are meant to reduce ambiguity across chapters. Some symbols are necessarily reused because the script covers several literatures: for example, $\rho$ can denote neural-network parameters, an optimizer coefficient, or a continuous-time discount rate depending on context. When a symbol changes role, the notation table records the chapter-specific convention. Cross-references should be used actively: many later chapters refer back to the same core objects, such as residual losses, ergodic sampling, market-clearing errors, HJB residuals, or GP posterior variances. The goal is not to memorize every symbol on first reading, but to use the notation tables as a stable reference while moving between chapters and notebooks.

##### Visual conventions.

The script uses three colored callout boxes plus an algorithm box. Each color is consistent across the entire manuscript and signals a particular kind of content (the first instance of each box appears in Chapter {ref}`ch-intro`):

- **Blue boxes (Definitions and Algorithms).** Used for formal definitions, key constructions, and step-by-step pseudocode. When a section introduces a new method, the algorithmic core is typically displayed in a blue box.

- **Green boxes (Remarks and Worked Examples).** Used for practical guidance, worked numerical examples, and short discussions that contextualize a result. Green boxes can be skipped on a first read without losing the main thread.

- **Crimson boxes (Key Insights).** Used sparingly to flag the highest-level take-aways of a section, ideas the reader should remember even after the implementation details fade.

- **Numbered algorithms.** Inside blue boxes labeled "Algorithm: ...," the pseudocode follows the conventions of the `algorithmic` package: [Input]{.smallcaps} / [Output]{.smallcaps} statements, indented [For]{.smallcaps} / [If]{.smallcaps} blocks, and arrow-style assignments.

A few additional typographic conventions: file paths and code identifiers are set in `monospace`; emphasized terms appear in **bold crimson**; cross-references to other chapters use the form (Ch. $N$) or (§$N.M$); and figure / table captions sit below their objects.

[^1]: <https://github.com/sischei/Deep_Learning_for_Solving_And_Estimating_Dynamic_Economic_Models>
