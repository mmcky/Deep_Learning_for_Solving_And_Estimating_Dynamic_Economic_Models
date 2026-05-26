---
title: "Notation and Symbols"
label: notation-and-symbols
---

```{list-table}
:header-rows: 1

* - Symbol
  - Meaning
* - $\x \in \R^d$
  - Input or state vector, depending on context
* - $p(\x)$
  - Policy/control associated with state $\x$
* - $G(\x, p(\x))$
  - Equilibrium or residual operator (e.g., Euler equation)
* - $\mathcal{N}_\rho$
  - Neural network with parameters $\rho$
* - $\ell$
  - Loss function (supervised or residual-based)
* - $\eta$
  - Learning rate
* - $\beta_1, \beta_2$
  - Adam momentum coefficients
* - $\mathcal{D}$
  - Dataset or collocation set
* - $\theta$
  - Generic model or structural parameter vector; when structural parameters and neural-network weights must be distinguished, $\rho$ denotes network weights
* - $A$
  - Number of OLG cohorts (Ch. 5)
* - $G_t(k_i, \varepsilon_j)$
  - Histogram mass at grid point $k_i$, shock $\varepsilon_j$ (Ch. 6)
* - $\mu_t$
  - Cross-sectional wealth distribution (Ch. 6--8)
* - $V(a,z)$
  - Value function in continuous-time HJB (Ch. 7--8)
* - $g(a,z)$
  - Stationary density from the KFE / Fokker--Planck equation (Ch. 7--8)
* - $\mathrm{SCC}_t$
  - Social cost of carbon (Ch. 11)
```

Where necessary, chapter-specific notation (e.g., HJB/PDE operators, kernel functions) is introduced locally to avoid ambiguity. In a few places, the script intentionally reuses symbols such as $\eta$ when that is standard in the underlying literature; in those cases, the local chapter definition takes precedence.

**Symbols with conflicting uses across chapters.** Several symbols below are reused with different meanings depending on the chapter, because each chapter inherits the convention of its primary source. This table collects the conflicts in one place; chapters that introduce a new local meaning also add a one-line warning at first use.

```{list-table}
:header-rows: 1

* - Symbol
  - Meanings (by chapter)
* - $\gamma$
  - IES $=1/\text{CRRA}$ in Ch. {ref}`ch-irbc` (IRBC); CRRA in Ch. {ref}`ch-pinn` (cake-eating) and Ch. {ref}`ch-ct_theory` (continuous-time HA); reused as $\sigma_u$ in Ch. {ref}`ch-climate` (OLG-IAM) to free $\sigma_t$ for emissions intensity; RL discount factor $\gamma\in[0,1)$ and BatchNorm scale parameter in Ch. {ref}`ch-intro`; Hyperband / Successive-Halving reduction factor in Ch. {ref}`ch-nas`.
* - $\eta$
  - Learning rate (Ch. {ref}`ch-intro`--{ref}`ch-deqn`); TFP shock in OLG (Ch. {ref}`ch-olg`); idiosyncratic productivity in Krusell--Smith (Ch. {ref}`ch-young`); OU mean-reversion (Ch. {ref}`ch-ct_theory`); small numerical shift in I-spline basis; normalized temperature costate (Ch. {ref}`ch-climate`); normalized spatial coordinate in PINN bilinear BC construction (Ch. {ref}`ch-pinn`); functional-derivative test perturbation in KFE adjoint argument (Ch. {ref}`ch-ct_theory`).
* - $\alpha$
  - Capital share in Cobb--Douglas production (Ch. {ref}`ch-deqn`, {ref}`ch-olg`, {ref}`ch-young`, {ref}`ch-ct_theory`, {ref}`ch-climate`); ReLoBRaLo smoothing parameter (Ch. {ref}`ch-nas`); boundary MPC head in I-spline (Ch. {ref}`ch-pinn`).
* - $\zeta$ vs. $\alpha$
  - Capital share is denoted $\zeta$ in Ch. {ref}`ch-irbc` (Azinovic et al. convention) and $\alpha$ everywhere else.
* - $T$
  - ReLoBRaLo softmax temperature (Ch. {ref}`ch-nas`); time horizon (Ch. {ref}`ch-pinn`, {ref}`ch-climate`); atmospheric temperature $T^{\mathrm{AT}}_t$ in DICE (Ch. {ref}`ch-climate`); data sample size in SMM (Ch. {ref}`ch-estimation`).
* - $\delta$
  - Capital depreciation rate (most chapters); Dirac measure in master equation (Ch. {ref}`ch-young`); Huber-loss threshold in robust regression (Ch. {ref}`ch-intro`).
* - $\psi$
  - IES in Ch. {ref}`ch-climate` Epstein--Zin preferences (paired with $\gamma_u$ for risk aversion); Cobb--Douglas capital exponent in the GP surrogate model (Ch. {ref}`ch-gp`).
* - $\mu$
  - Cross-sectional wealth distribution $\mu_t$ (Ch. {ref}`ch-young`--{ref}`ch-ct_theory`); SGD momentum coefficient (Ch. {ref}`ch-intro`); Lagrange / KKT multiplier on investment irreversibility (Ch. {ref}`ch-irbc`); emissions abatement rate $\mu_t\in[0,1]$ (Ch. {ref}`ch-climate`).
* - $\rho$
  - Network parameters $\mathcal{N}_\rho$ (most chapters); RMSprop decay coefficient and recurrence spectral radius (Ch. {ref}`ch-intro`); discount rate in continuous-time HJB (Ch. {ref}`ch-pinn`, {ref}`ch-ct_theory`); ReLoBRaLo baseline-mix coefficient (Ch. {ref}`ch-nas`). The variant $\varrho$ is reserved for shock persistence in Ch. {ref}`ch-deqn`. TFP persistence is denoted $\rho_z$ in Ch. {ref}`ch-irbc` (Azinovic et al. convention) and $\varrho$ elsewhere.
* - $\sigma$
  - Logistic activation $\sigma(z)=1/(1+e^{-z})$ in Ch. {ref}`ch-intro` (single-output and final-layer use); the same symbol is used as a generic non-linearity in the RNN recurrence and as the LSTM gate non-linearity later in the same chapter, so the meaning is always logistic but the typographic role (specific vs. generic) shifts. Ch. {ref}`ch-climate` (climate) reserves $\sigma_t$ for emissions intensity, $\sigma_u$ for household CRRA.
* - $\tau$
  - Bounded time index $\tau_t$ used as a network input in the deterministic CDICE-DEQN derivation (Ch. {ref}`ch-climate`, {ref}`sec-deep_uq`); separately, the per-period carbon tax rate (also written $\tau_t$) later in the same chapter, in the OLG-IAM and Pareto-improving-tax discussion. The notation is reset locally at each first use; readers should rely on the surrounding sentence rather than on the symbol alone.
```

**Default reading.** When in doubt, default to the most common usage: $\rho$ is the neural-network parameter vector, $\eta$ is the learning rate, $\alpha$ is the Cobb--Douglas capital share, and $\sigma$ is the logistic activation. Chapter-specific reuses always override locally, and the chapter introductions flag a divergent meaning at first use. The conflict table above is a forward-reference for non-linear readers; a cover-to-cover reader will see each meaning introduced once and need not consult the table on a first pass.

**Abbreviations and acronyms.** The following acronyms appear throughout the script. They are introduced in full at first use within each chapter; this list serves as a quick reference.

```{list-table}
:header-rows: 0

* - ABC
  - Approximate Bayesian Computation
  - KFE
  - Kolmogorov forward (Fokker--Planck) Eq.
* - ACE
  - Analytic Climate Economy (Traeger)
  - KKT
  - Karush--Kuhn--Tucker conditions
* - AD
  - Automatic Differentiation
  - KS
  - Krusell--Smith (1998) economy
* - AdamW
  - Adam with decoupled weight decay
  - LSTM
  - Long Short-Term Memory net
* - AS
  - Active Subspace
  - MAGICC
  - Reduced-complexity climate emulator
* - BAL
  - Bayesian Active Learning
  - MC
  - Monte Carlo
* - BC
  - Boundary Condition
  - MFG
  - Mean Field Game
* - BSDE
  - Backward Stochastic Differential Eq.
  - ML
  - Machine Learning
* - CDICE
  - Calibrated DICE (Folini 2024)
  - MLE
  - Maximum Likelihood Estimator
* - CRN
  - Common Random Numbers
  - MLP
  - Multi-Layer Perceptron
* - CRRA
  - Constant Relative Risk Aversion
  - MMW
  - Maliar--Maliar--Winant (2021)
* - DEQN
  - Deep Equilibrium Net
  - MPC
  - Marginal Propensity to Consume
* - DGM
  - Deep Galerkin Method
  - NAS
  - Neural Architecture Search
* - DICE
  - Dyn. Integ. Climate-Econ. model
  - NTK
  - Neural Tangent Kernel
* - DKL
  - Deep Kernel Learning
  - OLG
  - Overlapping Generations
* - DL
  - Deep Learning
  - PDE
  - Partial Differential Equation
* - DNN
  - Deep Neural Network
  - PINN
  - Physics-Informed Neural Net
* - ECS
  - Equilibrium Climate Sensitivity
  - QMC
  - Quasi-Monte Carlo
* - EGM
  - Endogenous Grid Method
  - ReLoBRaLo
  - Relative Loss Balancing
* - ELU
  - Exponential Linear Unit
  - RL
  - Reinforcement Learning
* - EMINN
  - Economic Model Informed NN
  - RNN
  - Recurrent Neural Network
* - FaIR
  - Reduced-complexity climate emulator
  - SBI
  - Simulation-Based Inference
* - FB
  - Fischer--Burmeister loss
  - SCC
  - Social Cost of Carbon
* - FD
  - Finite Differences
  - SDE
  - Stochastic Differential Equation
* - FNO
  - Fourier Neural Operator
  - SGD
  - Stochastic Gradient Descent
* - FOC
  - First-Order Condition
  - SMM
  - Simulated Method of Moments
* - GE
  - General Equilibrium
  - TF / TF2
  - TensorFlow / TensorFlow 2
* - GMM
  - Generalized Method of Moments
  - UQ
  - Uncertainty Quantification
* - GP
  - Gaussian Process
  - VFI
  - Value Function Iteration
* - HA
  - Heterogeneous Agent
  - ZLB
  - Zero Lower Bound
* - HJB
  - Hamilton--Jacobi--Bellman Eq.
  - XLA
  - Accelerated Linear Algebra (TF/JAX)
* - IRBC
  - Internat. Real Business Cycle
  - DeepONet
  - Deep Operator Network
* - JAX
  - JAX autodiff library (Google)
  - DeepHAM
  - Deep Heterogeneous-Agent Model
```
