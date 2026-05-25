---
title: "Glossary"
label: ch-glossary
---

A short glossary of recurring concepts. Each entry is one or two sentences; for the full treatment, follow the cross-references in parentheses.

**Active subspace.**
: The leading eigenspace of the gradient outer-product matrix $\E[\nabla f \nabla f^\top]$. Captures the linear directions in input space along which a function varies most; allows GPs to scale to high $d$ {cite:p}`constantine2015active`.

**Active subspace, deep.**
: Replaces the linear projection $U_m^\top \x$ by a learned nonlinear encoder $h\colon \R^D \to \R^d$, trained jointly with an MLP link $g\colon \R^d \to \R$ so that $\hat f(\xi) = g(h(\xi))$; gradient-free, with $d$ chosen by a validation-MSE elbow instead of a spectral gap (Section {ref}`sec-deep_as`; {cite:t}`tripathy2018deep`).

**Adam, AdamW.**
: Adaptive stochastic-gradient optimizers using momentum on the gradient and on its square; AdamW separates the weight-decay step from the adaptive step {cite:p}`kingma2015adam,loshchilov2019decoupled`.

**Approximate aggregation.**
: Empirical observation that in Krusell--Smith-class economies the cross-sectional distribution of wealth is nearly summarized by its mean for price forecasting purposes (Chapter {ref}`ch-young`).

**Automatic differentiation (AD).**
: Algorithmic computation of exact derivatives of composite functions via the chain rule; reverse-mode AD is the engine of every deep-learning framework {cite:p}`baydin2018automatic,margossian2019review`.

**Bayesian active learning (BAL).**
: Adaptive sample-design strategy in which the next training point is chosen to maximize an acquisition function based on predictive uncertainty; pairs naturally with GPs (Chapter {ref}`ch-gp`).

**Bellman equation.**
: Recursive characterization of the value function in a discrete-time dynamic program. Continuous-time analogue is the HJB equation.

**Brock--Mirman model.**
: Stochastic neoclassical growth model with log utility and full depreciation that admits a closed-form policy $s^\star = \alpha\beta$; the canonical DEQN benchmark in this script.

**Common random numbers (CRN).**
: Variance-reduction technique in which the same shock realisations are reused across simulations of different parameter values, removing simulation noise from comparisons {cite:p}`glasserman2004monte`.

**Collocation point.**
: A spatial location at which a PDE residual is evaluated and minimized in a PINN training loop (Chapter {ref}`ch-pinn`).

**Curse of dimensionality.**
: Exponential blow-up of grid-based methods in the dimension of the state space; mitigated, not eliminated, by neural-network and GP approximators.

**Deep Equilibrium Net (DEQN).**
: A neural-network-based solver for dynamic stochastic equilibrium models that minimizes the equilibrium-equation residuals directly via SGD (Chapter {ref}`ch-deqn`).

**Deep Galerkin Method (DGM).**
: An LSTM-style architecture introduced by {cite:t}`sirignano2018dgm` for solving high-dimensional PDEs; the architectural sibling of standard PINNs.

**Deep kernel learning (DKL).**
: Composes a neural-network feature extractor with a GP layer in the learned feature space {cite:p}`wilson2016deep`.

**DeepONet.**
: A neural architecture for operator learning: a branch net encodes the input function and a trunk net encodes the query point; the inner product is the predicted output {cite:p}`lu2021learning`.

**EMINN.**
: Economic-Model Informed Neural Network: a PINN-style approach to the master equation in continuous-time HA models {cite:p}`gu2024masterequations`.

**Ergodic distribution.**
: The stationary distribution of a Markov process; in a Krusell--Smith economy it is the long-run distribution of wealth across agents.

**Fischer--Burmeister (FB).**
: A smooth complementarity function $\Phi(a,b) = a + b - \sqrt{a^2+b^2}$ used to encode KKT conditions in differentiable losses; the opposite sign has the same zero set but the chapter and notebooks use this convention {cite:p}`fischer1992special`.

**Fourier Neural Operator (FNO).**
: Operator-learning architecture parameterizing a kernel integral operator in Fourier space; cheap and resolution-invariant {cite:p}`li2021fourier`.

**Functional derivative.**
: $\delta V/\delta g$, the density / Riesz representer of the Fréchet derivative of $V$ with respect to a function-valued argument $g$ (equivalently, the directional derivative of $V$ at $g$ in the direction of a Dirac perturbation $\delta_{y_0}$); appears in the master equation (Chapter {ref}`ch-ct_theory`).

**Gauss--Hermite quadrature.**
: Polynomial quadrature rule for integrals against the standard normal density; backbone of the expectations step in DEQNs.

**HJB equation.**
: Hamilton--Jacobi--Bellman equation; continuous-time analogue of the Bellman equation, a PDE in the value function.

**Histogram (Young 2010).**
: Mass-redistribution scheme on a fixed grid that propagates a wealth distribution deterministically without Monte Carlo noise (Chapter {ref}`ch-young`).

**Hyperband.**
: Successive-halving multi-fidelity hyperparameter scheduler that explores many configurations cheaply and concentrates budget on the survivors {cite:p}`li2018hyperband`.

**Inducing points.**
: A small set of pseudo-data points used in sparse GPs to approximate the full kernel matrix at $\mathcal{O}(nm^2)$ cost {cite:p}`titsias2009variational`.

**Itô's lemma.**
: The chain rule of stochastic calculus; for the scalar diffusion $dX_t=\mu\,dt+\sigma\,dB_t$, the only difference from ordinary calculus is the second-order correction $\tfrac{1}{2}f''(X_t)\sigma^2\,dt$.

**Karush--Kuhn--Tucker (KKT) conditions.**
: First-order necessary conditions for constrained optimization; encoded smoothly via Fischer--Burmeister in DEQN losses.

**Kolmogorov forward equation (KFE / Fokker--Planck).**
: The PDE governing the time evolution of the probability density of an Itô process.

**Marginal likelihood.**
: The log-evidence $\log p(\bm y \mid \bm\vartheta)$ in a GP; sum of a data-fit term and a complexity penalty (Chapter {ref}`ch-gp`).

**Master equation.**
: A single PDE that subsumes the HJB, KFE, and market-clearing conditions of a continuous-time mean-field-game equilibrium; argument includes the cross-sectional measure $g$.

**Mean field game (MFG).**
: Equilibrium concept in which each atomistic agent best-responds to the cross-sectional distribution and the distribution evolves under those best responses; the natural framework for the HJB+KFE system {cite:p}`lasry2007mean`.

**Neural Tangent Kernel (NTK).**
: In the infinite-width limit, gradient-descent training of a deep network is equivalent to kernel regression with the (deterministic) NTK {cite:p}`jacot2018neural`.

**Operator learning.**
: Learning a map between function spaces (input field $\to$ solution function) rather than a single solution; DeepONet and FNO are the leading architectures.

**Physics-Informed Neural Network (PINN).**
: A neural network trained by minimizing a PDE residual at collocation points plus boundary-condition penalties {cite:p}`raissi2019physics`.

**Pseudo-state.**
: Treating model parameters as additional inputs to a neural network so that the trained surrogate covers an entire parameter range without retraining (Chapter {ref}`ch-gp`).

**Quasi-Monte Carlo (QMC).**
: Deterministic low-discrepancy sequences (Sobol, Halton, Niederreiter) achieving error rates close to $\mathcal{O}(1/M)$ for smooth integrands.

**ReLoBRaLo.**
: Adaptive loss-balancing scheme that reweights multi-component losses by recent relative-decrease ratios {cite:p}`bischof2025relobralo`.

**Simulated Method of Moments (SMM).**
: Estimator that matches simulated to empirical moments; the natural extension of GMM when moments lack closed form {cite:p}`mcfadden1989method`.

**Simulation-based inference (SBI).**
: Modern likelihood-free Bayesian inference using neural conditional density estimators {cite:p}`cranmer2020frontier`.

**Social cost of carbon (SCC).**
: Marginal welfare cost of one additional unit of emissions, commonly reported as USD/tCO$_2$ after choosing the consumption numeraire and applying the carbon-to-CO$_2$ conversion; the headline policy number from a climate IAM.

**Sobol / Shapley indices.**
: Variance-decomposition tools for global sensitivity analysis. Sobol decompositions are cleanest under independent inputs; Shapley effects allocate variance across inputs and can be defined for dependent inputs when the dependence structure is modeled explicitly.

**Universal approximation.**
: A single-hidden-layer network with a non-polynomial activation can approximate any continuous function on a compact set arbitrarily well {cite:p}`cybenko1989approximation,hornik1989multilayer`.

**Value Function Iteration (VFI).**
: Classical contraction-mapping algorithm for solving the Bellman equation by iterating the Bellman operator until convergence.

**Young's lottery.**
: The unique two-point split that, when applied to off-grid policy choices, preserves the conditional mean exactly; the building block of the histogram update.

