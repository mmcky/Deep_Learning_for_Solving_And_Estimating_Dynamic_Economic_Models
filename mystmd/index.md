---
title: "Deep Learning for Solving and Estimating Dynamic Models in Economics and Finance"
---

## Abstract

This script offers an implementation-oriented introduction to deep learning methods for solving and estimating high-dimensional dynamic stochastic models in economics and finance. Its starting point is the curse of dimensionality: heterogeneous-agent economies, overlapping-generations models with aggregate risk, continuous-time models with occasionally binding constraints, climate-economy models, and macro-finance environments with many assets and frictions all generate state and parameter spaces that strain classical tensor-product grid methods.

The exposition is organized around four complementary methodologies. Deep Equilibrium Nets embed discrete-time equilibrium conditions directly into neural-network loss functions. Physics-Informed Neural Networks approximate continuous-time Hamilton–Jacobi–Bellman, Kolmogorov forward, and related partial differential equations. Deep surrogate models provide fast, differentiable approximations to expensive structural models, while Gaussian processes add a probabilistic layer that quantifies approximation uncertainty; together they support estimation, sensitivity analysis, and constrained policy design. Gaussian-process-based dynamic programming, combined with active learning and dimension reduction, extends value-function iteration to settings with very large continuous state spaces.

Applications range from representative-agent and international real business cycle models to overlapping-generations and heterogeneous-agent economies, continuous-time macro-finance, structural estimation by simulated method of moments, and climate economics under uncertainty. The emphasis throughout is practical: economic restrictions are translated into trainable residuals, algorithms are paired with diagnostics, and companion notebooks in TensorFlow and PyTorch invite students to experiment, modify, and learn by doing.

These notes are not intended as an exhaustive textbook. They are a deliberately subjective and inevitably incomplete snapshot of a rapidly evolving field. The selection of architectures, references, and case studies reflects one researcher’s judgment about useful entry points at the time of writing. Their purpose is to equip PhD students and researchers with enough conceptual and computational machinery to engage with this frontier hands-on.

> “The machine, the frozen form of a living intelligence, is the power that expands the potential of your life by raising the productivity of your time.”
>
> — Ayn Rand, *Atlas Shrugged* (1957), Galt’s Speech (Part Three, Chapter VII)

:::{note}
This is the MyST Markdown rendering of the companion script. The authoritative PDF lives alongside the [LaTeX source](https://github.com/sischei/Deep_Learning_for_Solving_And_Estimating_Dynamic_Economic_Models/blob/main/lecture_script/Deep_Learning_for_Solving_And_Estimating_Dynamic_Economic_Models.pdf). The 18-lecture course materials (slides, notebooks, exercises) sit beside it in [`lectures/`](https://github.com/sischei/Deep_Learning_for_Solving_And_Estimating_Dynamic_Economic_Models/tree/main/lectures).
:::

## Front Matter

- [](preface.md)
- [](how_to_read.md)
- [](notation.md)
- [](execution_map.md)

## Chapters

- [](ch01_intro.md)
- [](ch02_deqns.md)
- [](ch03_irbc.md)
- [](ch04_nas.md)
- [](ch05_olg.md)
- [](ch06_ha_youngs.md)
- [](ch07_pinns.md)
- [](ch08_ctime_ha.md)
- [](ch09_surrogates_gps.md)
- [](ch10_smm.md)
- [](ch11_climate.md)
- [](ch12_synthesis.md)

## Appendices

- [](appA_glossary.md)
- [](appB_matrix_calc.md)
- [](appC_ito.md)
- [](appD_fixed_points.md)
- [](appE_reproducibility.md)
- [](appF_solutions.md)
