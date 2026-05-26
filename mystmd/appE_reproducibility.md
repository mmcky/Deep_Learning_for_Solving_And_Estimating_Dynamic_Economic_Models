---
title: "Reproducibility Information"
label: app-reproducibility
---

Every empirical statement in the main text relies on the companion notebooks listed in the *Execution Map*. Bit-exact reproducibility on a different machine requires fixing both the random seeds and the floating-point environment; Table {numref}`tab-repro_conventions` summarizes the conventions used in this script's notebooks.

````{table}
:name: tab-repro_conventions

Reproducibility conventions used by the companion notebooks. The conventions pin random seeds and document hardware, software, and precision choices; bit-exact reproduction additionally requires the deterministic settings and caveats described below the table.

| **Item** | **Convention** |
|---|---|
| Random seeds | Each notebook declares a `SEED` constant in cell 1 (default `0`); the corresponding framework seeds (`numpy.random.seed(SEED)`, `torch.manual_seed(SEED)`, `tf.random.set_seed(SEED)`, and `jax.random.PRNGKey(SEED)` where the framework is used) are derived from it. Per-cell offsets and per-iteration deviations are documented inline. Notebook-by-notebook normalisation against this convention is tracked through the chapter audits; some legacy notebooks still hard-code a literal seed and are scheduled for normalisation. |
| Run-mode budget | Each notebook declares `RUN_MODE` $\in$ `{smoke, teaching, production}` alongside `SEED` in cell 1. `smoke` is sized for a single CPU core (CI-friendly); `teaching` for one consumer GPU; `production` for an A100 or larger. Per-notebook hyperparameters (epochs, batch sizes, restart counts) are gated on `RUN_MODE`. |
| Hardware | Classroom-scale runs target a single CPU core or one consumer GPU (e.g. NVIDIA T4 / RTX 3060). Production runs use one A100 or larger; this is documented per-notebook in the chapter. |
| Software stack | Python $\geq 3.10$, TensorFlow $\geq 2.15$, PyTorch $\geq 2.0$, JAX $\geq 0.4.20$, GPyTorch $\geq 1.11$. Pinned versions live in `requirements.txt` on the companion repository. JAX appears in the Krusell--Smith warm-up notebook in `lectures/lecture_10_*` (sequence-space DEQNs); the other lectures use TensorFlow or PyTorch. |
| Numerical precision | TensorFlow / PyTorch default to `float32`; PINNs and EMINN training use `float64` where second-order derivatives are sensitive (documented inline). |
| GPU determinism | *Optional, bit-exact runs only*: set `CUBLAS_WORKSPACE_CONFIG=:4096:8` and `torch.use_deterministic_algorithms(True)` on the PyTorch side, and call `tf.config.experimental.enable_op_determinism()` on the TensorFlow side. Default classroom and production runs leave these unset, accepting last-decimal nondeterminism in exchange for speed; small accuracy regression possible when the flags are on. |
| Reported numbers | Where the script states an accuracy or runtime, the source is either the cited paper (for production-scale results) or the companion notebook with the seed above (for classroom-scale results). |
````

For full bit-exact reproduction, e.g. for a regulatory-grade audit, the determinism flags above are necessary but not sufficient: GPU non-determinism in atomic accumulators and BLAS implementation differences across CUDA versions can still cause diverging results in the last few decimal places. This is a known limitation of GPU-accelerated deep learning and is one of the reasons {ref}`sec-when_not_to_use_dl` flags reproducibility-critical settings as a regime where deterministic finite-difference solvers may still be preferred.
