---
title: "Physics-Informed Neural Networks"
label: ch-pinn
---

Chapters {ref}`ch-deqn`--{ref}`ch-young` operated in discrete time, where the equilibrium conditions take the form of expectational (Euler) equations. We now shift to *continuous time*, where the optimality conditions are partial differential equations -- Hamilton--Jacobi--Bellman (HJB) equations for optimal control and Kolmogorov forward equations for wealth distributions. *Physics-Informed Neural Networks* (PINNs) approximate the solution of such PDEs by minimizing the PDE residual at collocation points, using automatic differentiation to compute the required derivatives {cite:p}`sirignano2018dgm,raissi2019physics`. The PINN loss is structurally analogous to the DEQN loss of Chapter {ref}`ch-deqn`, but instead of time-stepping a fixed-point iteration we solve a single PDE globally over the state space. This chapter develops the PINN methodology from simple ODEs through boundary-condition strategies to the HJB equation for consumption--savings problems, with applications to macro-finance.

## From DEQNs to PINNs: Discrete vs. Continuous Time

Many frontier models in macroeconomics and finance are written in continuous time. Examples include Hamilton--Jacobi--Bellman (HJB) equations for optimal control, Kolmogorov forward equations for wealth distributions, and Black--Scholes PDEs for asset pricing. The DEQN methodology from Chapters {ref}`ch-deqn`--{ref}`ch-irbc` handles discrete-time equilibrium conditions. Its continuous-time analogue relies on derivatives of the network with respect to its inputs, which automatic differentiation provides directly.

The resulting framework, known as *Physics-Informed Neural Networks* (PINNs), was introduced by {cite:t}`raissi2019physics`. In economics and finance, continuous-time models governed by HJB and related PDEs arise naturally in asset pricing under climate uncertainty {cite:p}`barnett2020pricing`, portfolio choice {cite:p}`duarte2024ml`, and heterogeneous-agent economies with aggregate shocks {cite:p}`gopalakrishna2024aliens`. {cite:t}`duarte2024ml` apply machine-learning methods to continuous-time finance problems, while {cite:t}`gopalakrishna2024aliens` develops the ALIENs framework for solving continuous-time economies with deep learning. PINNs provide a natural and scalable computational framework for such problems. Figure {numref}`fig-deqn_pinn_comparison` summarizes the discrete-time DEQN template and its continuous-time PINN analogue.

```{figure} figures/fig-deqn_pinn_comparison.svg
:name: fig-deqn_pinn_comparison

Discrete-time DEQNs and continuous-time PINNs use the same residual-minimization principle with different mathematical residuals. DEQNs minimize algebraic equilibrium conditions such as Euler-equation errors evaluated along simulated states, while PINNs minimize PDE and boundary residuals evaluated at collocation points using derivatives of the network with respect to its inputs.
```

## The PINN Loss and Automatic Differentiation for PDEs

##### Prerequisites in one paragraph.

A few terms from PDE numerics recur throughout the chapter and deserve to be fixed in advance. *Collocation points* are interior evaluation points at which the PDE residual is enforced; they do not need to lie on a Cartesian grid, and in high dimensions they are typically drawn at random or from a low-discrepancy sequence. The *strong form* minimizes the residual point-wise and requires the network's activation to be at least $C^k$ if the differential operator is of order $k$. The *weak form* integrates the residual against test functions, which tolerates rougher solutions but is rarely needed for the PDEs in this chapter. We assume throughout that each problem is *well-posed* (existence, uniqueness, and continuous dependence on data); proving well-posedness for a particular HJB or KFE is part of the PDE literature, not of this course.

Given a PDE $\mathcal{D}[u](\x) = 0$ on a domain $\Omega$ with boundary conditions $\mathcal{B}[u](\x) = 0$ on $\partial\Omega$, the PINN loss is:

$$
\boxed{
\ell_\theta^\mathrm{PINN} =
\underbrace{\frac{1}{N_r}\sum_{i=1}^{N_r} \big|\mathcal{D}[\mathcal{N}_\theta](\x_i^r)\big|^2}_{\text{PDE residual}}
+ \underbrace{\frac{\lambda}{N_b}\sum_{j=1}^{N_b} \big|\mathcal{B}[\mathcal{N}_\theta](\x_j^b)\big|^2}_{\text{boundary conditions}}.
}
$$ (eq-pinn_loss)

The derivatives appearing in $\mathcal{D}[\mathcal{N}_\theta]$ are computed algorithmically via automatic differentiation[^1] (e.g., `torch.autograd.grad` in PyTorch), up to floating-point precision and without any finite-difference approximation. This removes finite-difference truncation error in derivative terms and is a major practical advantage in high dimensions because no state-space grid is required. Remaining error sources are function-approximation error, optimization error, and collocation sampling error.

##### Activation function requirements.

The choice of activation function is particularly important for classical *strong-form* PINNs that compute high-order derivatives via automatic differentiation. If the PDE operator $\mathcal{D}$ involves $k$-th order derivatives, the network's activation function must be at least $C^k$ for the strong residual to be well-defined. $\mathrm{ReLU}(z) = \max(0,z)$ is only $C^0$ and its second derivative is zero almost everywhere (and undefined at the kink), so a ReLU network is not suitable for the strong form of a second-order PDE. For second-order PDEs (HJB, Black--Scholes, Poisson), one should use $C^\infty$ activations such as $\tanh$, Swish, or softplus. This requirement stands in contrast to the supervised setting, where ReLU is the default. The trade-off is real: smooth saturating activations propagate gradients more slowly than ReLU on the same architecture (the upper plateau of $\tanh$ has near-zero slope), so PINNs typically need wider networks or more iterations to reach the same training loss as a comparable supervised ReLU network. In practice this is the price of having well-defined second derivatives. Note that the limitation is specific to strong-form auto-differentiation PINNs: weak/variational formulations and methods that handle nonsmooth solutions explicitly can still use ReLU activations, since high-order derivatives never need to be differentiated point-wise. More broadly, PINN optimization can suffer from gradient pathologies across loss terms, which is why adaptive loss balancing is often beneficial {cite:p}`wang2021understanding,bischof2025relobralo`.

```{prf:remark}

The PINN notebooks use PyTorch, whereas the DEQN code (Chapters {ref}`ch-deqn`--{ref}`ch-irbc`) uses TensorFlow. This is a practical implementation choice rather than a mathematical one: PINNs repeatedly differentiate the network with respect to its *inputs* (e.g., $V_{SS}$ in the Black--Scholes PDE), and PyTorch's eager-mode `autograd` makes those higher-order derivatives easy to compose. TensorFlow remains a natural fit for the DEQN training loop already used earlier in the course. The underlying mathematics is identical in both frameworks: a PINN written here in PyTorch can be ported to TensorFlow line-for-line by replacing `torch.autograd.grad` with `tf.GradientTape` (one tape per derivative order, since TF tapes are by default not persistent), and `torch.compile` with `tf.function`.
```


### A Concrete Example: Solving a 1D ODE with a PINN

To build intuition, consider the boundary value problem

$$
y''(x) = -1, \qquad x \in (0,1), \qquad y(0) = y(1) = 0,
$$ (eq-1d_ode_bvp)

whose analytical solution is $y^\star(x) = \tfrac{1}{2}\,x(1-x)$. Approximate the unknown function by a raw neural network $\mathcal{N}_\theta(x)$, with no boundary information built in. The strong-form residual is

$$
R(x;\theta) = \partial_{xx}\mathcal{N}_\theta(x) + 1,
$$

where $\partial_{xx}\mathcal{N}_\theta$ is obtained by two applications of `torch.autograd.grad`. The boundary conditions are then added to the loss as a penalty term -- the *soft* enforcement strategy:

$$
\ell_\theta = \frac{1}{N_r}\sum_{i=1}^{N_r} R(x_i;\theta)^2
            \;+\; \lambda\bigl(\mathcal{N}_\theta(0)^2 + \mathcal{N}_\theta(1)^2\bigr),
$$ (eq-1d_ode_soft_loss)

with collocation points $x_i$ drawn uniformly from $(0,1)$ and a weight $\lambda>0$ on the boundary term. Building the boundary conditions directly into the network output instead -- the *hard* enforcement alternative, which removes the $\lambda$ term entirely -- is taken up in {ref}`sec-bc_soft_hard`.

```{prf:remark}

Uniform random sampling is the simplest collocation strategy but not necessarily the most efficient. Alternatives include low-discrepancy Sobol sequences {cite:p}`sobol1967distribution`; Latin Hypercube Sampling {cite:p}`mckay1979comparison`, which provides better space coverage; other quasi-Monte Carlo points {cite:p}`niederreiter1992random,owen1995randomly`, which fill the domain more evenly; and residual-based adaptive refinement {cite:p}`lu2021deepxde`, which concentrates points in regions where the current PDE residual is largest. For most applications in this course, uniform or LHS sampling is sufficient, but adaptive refinement can be beneficial for PDEs with sharp gradients, boundary layers, and near payoff discontinuities (e.g., the kink at $S = K$ in Black--Scholes). *Mini-batch sizes.* Per-step collocation batches are typically $32$--$256$ points in low-dimensional problems and $512$--$4096$ when the input dimension or interaction-order grows; the right number is the largest that fits comfortably in GPU memory together with the AD graph for the highest-order derivative needed. All companion notebooks make this an explicit hyperparameter near the top of the training cell.
```


```{figure} figures/fig-pinn_1d_ode_soft.svg
:name: fig-pinn_1d_ode_soft

PINN solution of the 1D ODE y″ = −1 on (0, 1) with y(0) = y(1) = 0 and the soft-penalty loss {eq}`eq-1d_ode_soft_loss`. The analytical solution $\tfrac12 x(1-x)$ (solid blue) is recovered to plotting accuracy by the converged network (dotted green); the dashed red curve illustrates a typical early-training iterate, which still misses the endpoints because the boundary penalty is enforced only approximately. Tick marks on the x-axis are the uniformly drawn collocation points. The curves above are TikZ illustrations rather than direct exports. Notebook lecture_11_01_ODE_PINN_ZeroBCs runs exactly this experiment; notebook lecture_11_02_ODE_PINN_SoftVsHardBCs then contrasts the soft penalty against the hard trial-solution construction of {ref}`sec-bc_soft_hard` on a non-zero-BC variant.
```

Figure {numref}`fig-pinn_1d_ode_soft` shows this calculation graphically. This simple example illustrates the key ingredients of every PINN: (i) a neural network that approximates the unknown function, (ii) automatic differentiation to compute derivatives, (iii) a loss function built from the PDE residual (plus, here, a boundary penalty), and (iv) collocation points sampled from the domain interior. The same machinery extends directly to PDEs in two or more dimensions, as we demonstrate in the following applications.

(sec-bc_soft_hard)=
## Boundary Conditions: Soft vs. Hard Enforcement
The treatment of boundary conditions is a critical design choice in PINNs.

##### Soft enforcement.

Boundary conditions are penalized as an additional loss term, weighted by $\lambda$. The difficulty is that $\lambda$ must be tuned: too small and the BCs are violated; too large and the optimizer ignores the PDE interior. Figure {numref}`fig-soft_bc_failure_modes` sketches the two failure modes and the compromise regime in between.

```{figure} figures/fig-soft_bc_failure_modes.svg
:name: fig-soft_bc_failure_modes

Failure modes of soft boundary-condition enforcement on a Dirichlet problem with y(0) = 1, y(1) = 2. Left: the BC penalty weight λ is too small, so the optimizer minimizes the interior PDE residual but lets the candidate solution miss both endpoints (visible as the “gap” at x = 0). Right: λ is too large, so the network nails the boundary values but distorts the interior, producing a wiggly profile with PDE residual error against the affine reference (dashed grey). Centre: a balanced λ approximately satisfies both objectives, but the right-shaped value depends on the network, the PDE, and the geometry, and is not known a priori. This trade-off motivates the hard-enforcement construction below, which removes the boundary loss term entirely.
```

##### Hard enforcement.

A *trial solution* is constructed that satisfies the boundary conditions *by construction*:

$$
\hat{y}(x) = A(x) + B(x) \cdot \mathcal{N}_\theta(x),
$$ (eq-trial)

where $A(x)$ is an anchor function satisfying the BCs exactly, and $B(x)$ is a mask function that vanishes at the boundary. For Dirichlet BCs $\hat{y}(0) = a$, $\hat{y}(1) = b$, one may choose $A(x) = a + (b-a)x$ and $B(x) = x(1-x)$. Figure {numref}`fig-trial_solution_decomposition` visualizes this anchor-plus-mask decomposition for non-zero endpoint data.

```{figure} figures/fig-trial_solution_decomposition.svg
:name: fig-trial_solution_decomposition

Hard boundary-condition decomposition for the trial solution ŷ(x) = A(x) + B(x) ⋅ 𝒩θ(x) with Dirichlet data ŷ(0) = 1, ŷ(1) = 2. Left: anchor A(x) = 1 + x matches the boundary values exactly. Centre: mask times network, B(x) ⋅ 𝒩θ(x) with mask B(x) = x(1 − x), which vanishes at x ∈ {0, 1} regardless of 𝒩θ. Right: their sum ŷ(x) = A(x) + B(x) ⋅ 𝒩θ(x) (solid green) is a candidate solution that satisfies both BCs by construction; the dashed red line is the affine anchor A(x) = 1 + x for visual reference. Training loss reduces to the interior PDE residual alone.
```

Hard enforcement eliminates the boundary loss term entirely, reducing the number of hyperparameters and improving accuracy near the boundaries. The trade-off is real, however: because $\hat y = A + B\cdot\mathcal{N}_\theta$ multiplies the network output by a mask $B$ that vanishes on $\partial\Omega$, the input-gradient $\partial\hat y/\partial x$ inherits a factor of $B$ near the boundary and is thus damped by construction. When the true solution exhibits a steep boundary layer (e.g., a Hamilton--Jacobi--Bellman equation at the borrowing constraint, see {ref}`sec-hjb_theory`), the network must compensate by making $\mathcal{N}_\theta$ itself locally large, which can slow convergence. In short: hard BCs trade boundary-loss tunability for vanishing input gradients at $\partial\Omega$, and the trade is favorable for smooth Dirichlet problems but less obviously so for problems with sharp boundary features.

##### A worked 1D instance.

As a concrete instantiation, return to the simple ODE $y''(x)+y(x)=0$ on $[0,\pi/2]$ with $y(0)=0$, $y(\pi/2)=1$, whose analytical solution is $\sin x$. A trial solution that builds in both endpoints is

$$
\hat{y}(x) = \underbrace{\frac{2x}{\pi}}_{A(x)} + \underbrace{x\!\left(\frac{\pi}{2} - x\right)}_{B(x)} \cdot \mathcal{N}_\theta(x),
$$ (eq-1d_ode_trial)

which has the anchor-plus-mask form {eq}`eq-trial`: the anchor $A$ matches the boundary data ($A(0)=0$, $A(\pi/2)=1$) and the mask $B$ vanishes at both endpoints, so $\hat{y}(0)=0$ and $\hat{y}(\pi/2)=1$ hold exactly for any network output, and the loss reduces to the interior PDE residual alone, $$\ell_\theta = \frac{1}{N_r}\sum_{i=1}^{N_r}\big(\hat{y}''(x_i) + \hat{y}(x_i)\big)^2,$$ with $\hat{y}''$ obtained by two applications of `torch.autograd.grad` and collocation points $x_i$ drawn uniformly from $[0,\pi/2]$.

```{figure} figures/fig-pinn_1d_ode.svg
:name: fig-pinn_1d_ode

PINN solution of the 1D ODE y″ + y = 0 on [0, π/2] with the hard-BC trial solution {eq}`eq-1d_ode_trial`. The analytical solution sin (x) (solid blue) is recovered to plotting accuracy by the converged network (dotted green); the dashed red curve illustrates a typical early-training iterate. Tick marks on the x-axis are the uniformly drawn collocation points. The curves above are TikZ illustrations rather than direct exports. Notebook lecture_11_02_ODE_PINN_SoftVsHardBCs contrasts this hard-trial-solution construction with the soft-penalty alternative on a non-zero-BC variant.
```

Figure {numref}`fig-pinn_1d_ode` confirms that the converged trial solution recovers $\sin x$ to plotting accuracy, with the boundary values exact by construction; contrast the early-training iterate of Figure {numref}`fig-pinn_1d_ode_soft`, which still misses the endpoints under the soft penalty.

##### Transfinite interpolation for 2D domains.

The 1D hard-enforcement idea ($\hat{y} = A + B \cdot \mathcal{N}_\theta$) extends naturally to rectangular 2D domains, but the anchor function $A$ must now interpolate prescribed boundary data along entire *edges*, not just at two endpoints. The classical technique for this is transfinite interpolation (also known as Gordon--Coons blending): it constructs a function over the rectangle that exactly matches given boundary curves, in much the same way that bilinear interpolation matches four corner values, except that here we match four continuous edge functions rather than four discrete values.

Consider a rectangular domain $[a,b] \times [c,d]$ with Dirichlet boundary data $f_L(y)$ (left edge, $x=a$), $f_R(y)$ (right edge, $x=b$), $f_B(x)$ (bottom edge, $y=c$), and $f_T(x)$ (top edge, $y=d$). Introduce the normalized coordinates $\xi = (x-a)/(b-a) \in [0,1]$ and $\eta = (y-c)/(d-c) \in [0,1]$. The idea is to blend the four edge functions using linear weights, then correct for the corners that get counted twice.

**Step 1, Interpolate in $x$:** The function $(1-\xi)\,f_L(y) + \xi\,f_R(y)$ matches the left and right edges exactly for every $y$, but says nothing about the top and bottom edges.

**Step 2, Interpolate in $y$:** Similarly, $(1-\eta)\,f_B(x) + \eta\,f_T(x)$ matches the bottom and top edges exactly for every $x$.

**Step 3, Add and correct.** Summing these two would double-count the corner values (e.g., $f_L(c)$ and $f_B(a)$ both contribute at $(a,c)$). We subtract a bilinear interpolant through the four corner values to compensate. The result is the blending (anchor) function:

$$
\begin{split}
A(x,y) &= \underbrace{(1-\xi)\,f_L(y) + \xi\,f_R(y)}_{\text{left/right interpolation}}
       \;+\; \underbrace{(1-\eta)\,f_B(x) + \eta\,f_T(x)}_{\text{bottom/top interpolation}} \\[4pt]
       &\quad -\; \underbrace{\bigl[(1-\xi)(1-\eta)\,f_{BL} + \xi(1-\eta)\,f_{BR} + (1-\xi)\eta\,f_{TL} + \xi\,\eta\,f_{TR}\bigr]}_{\text{bilinear corner interpolant}},
\end{split}
$$

where $f_{BL} = f_B(a) = f_L(c)$, etc., are the four corner values. These values must be *consistent* across the two edges that meet at each corner (e.g., the value of $f_L$ at $y=c$ must equal the value of $f_B$ at $x=a$); otherwise the corner-correction bilinear cancels imperfectly and $A$ does not match any of the four edges exactly at the offending corner. Under consistent corner data, $A$ matches all four edge functions exactly by construction.

The mask function must vanish on all four edges so that the network can modify the interior without disturbing the boundaries:

$$
B(x,y) = \xi\,(1-\xi)\,\eta\,(1-\eta).
$$

Note that $B = 0$ whenever $\xi \in \{0,1\}$ or $\eta \in \{0,1\}$, i.e., on every edge of the rectangle. The hard-enforced trial solution is then:

$$
\hat{u}(x,y) = A(x,y) + B(x,y) \cdot \mathcal{N}_\theta(x,y).
$$

On any boundary edge, $B=0$ and $\hat{u}$ reduces to $A$, which matches the prescribed data. In the interior, $B > 0$ and the network $\mathcal{N}_\theta$ is free to learn whatever shape is needed to satisfy the PDE. This construction satisfies all four Dirichlet conditions exactly for *any* network output $\mathcal{N}_\theta$.

```{prf:remark}

**Hard enforcement** is preferred whenever a valid trial solution can be constructed analytically, which is the case for most standard boundary value problems in economics (e.g., Dirichlet conditions on finite domains). **Soft enforcement** is necessary when the boundary conditions are complicated (e.g., free-boundary problems, state-dependent constraints) or when the domain geometry makes it difficult to construct the mask function $B(x)$. In practice, hard enforcement typically improves accuracy by 1--2 orders of magnitude near the boundaries.
```


### 2D Poisson Benchmark

As a pedagogical 2D benchmark, the accompanying notebook `lecture_11_03_PDE_PINN_Poisson2D` solves a Poisson equation on the unit square,

$$
\nabla^2 u(x,y) = f(x,y), \qquad (x,y) \in [0,1]^2,
$$

with manufactured solution $u^\star(x,y) = x^2 + y + \sin(\pi x)\sin(\pi y)$, yielding $f(x,y) = 2 - 2\pi^2\sin(\pi x)\sin(\pi y)$ and non-homogeneous Dirichlet data $u\big|_{y=0} = x^2$, $u\big|_{y=1} = x^2+1$, $u\big|_{x=0} = y$, $u\big|_{x=1} = 1+y$. (Some PDE references prefer the standard-elliptic convention $-\nabla^2 u = f$; switching to that form flips the sign of $f$ but leaves the boundary data and the network architecture unchanged.) Because $\sin(\pi x)\sin(\pi y)$ vanishes on $\partial\Omega$, the polynomial part $A(x,y) = x^2 + y$ already matches all four edges (and their corner values) exactly, so it serves as the transfinite-interpolation anchor (the corner-consistency requirement of {ref}`sec-bc_soft_hard` is automatic here). The mask $B(x,y) = x(1-x)y(1-y)$ vanishes on every edge, and the hard-enforced trial solution $\hat u(x,y) = A(x,y) + B(x,y)\,\mathcal{N}_\theta(x,y)$ satisfies all Dirichlet conditions by construction; the network is trained on the interior PDE residual alone. In the reference notebook configuration, the verification gate is a mode-dependent relative-$L_2$ error against the manufactured solution on a $100 \times 100$ test grid (disabled in the `smoke` CI run, with progressively tighter bounds in `teaching` and `production`), computed for a modest network and a few thousand collocation points; the exact numbers depend on seed, hardware, optimizer settings, and the collocation sample. This benchmark is the clean 2D extension of the 1D ODE example and a useful bridge before turning to economic applications, and it exercises the full hard-BC transfinite-interpolation machinery on non-zero edge data rather than collapsing to the trivial $u\big|_{\partial\Omega}=0$ case.

## Common PINN Failure Modes and Remedies

In practice, PINN training often fails for optimization reasons rather than approximation capacity. Table {numref}`tab-pinn_failure_modes` lists the most common pathologies and practical remedies.

````{table}
:name: tab-pinn_failure_modes

Common PINN failure modes and practical remedies. The main implementation lesson is to monitor loss components separately: a small total loss can hide boundary violations, interior residual spikes, or gradient imbalance across terms.

| **Symptom** | **Typical cause** | **Practical remedy** |
|---|---|---|
| Large boundary violations | Soft BC penalties underweighted or unstable | Prefer hard BC trial solutions when possible; otherwise use adaptive loss balancing (e.g., ReLoBRaLo). |
| Good BC fit, poor interior PDE fit | Boundary penalties overweighted | Decrease BC weights or rebalance losses dynamically. |
| Residual spikes in narrow regions | Collocation undercoverage (boundary layers / kinks) | Use residual-based adaptive resampling, Sobol/LHS points, and local point refinement. |
| Slow or stalled optimization | Gradient imbalance across loss terms; or initialization in a basin disconnected from the true solution | Normalize loss components and monitor per-term gradients; use adaptive balancing schemes {cite:p}`wang2021understanding,bischof2025relobralo`; restart with different seeds or warm-start from a coarser solver if the loss plateaus far from any plausible solution. |
| Optimizer stuck on a symmetric / structureless ansatz | Initialization too symmetric to represent an asymmetric solution; gradient updates preserve the symmetry | Break the symmetry explicitly: asymmetric weight initialization, an auxiliary symmetry-breaking input feature, or a short pre-training pass that nudges the ansatz toward the correct shape. |
| Oscillatory solution near payoff kink | Spectral bias and non-smooth target geometry | Increase sampling density near kink and split domain if needed; use problem-specific transforms. |
````

The penultimate row above is folklore in computational quantum chemistry, where solvers routinely ship dedicated symmetry-breaking modules because a symmetric initial guess is preserved exactly under gradient training; the analogous trap shows up in PINNs whenever the true solution lacks a symmetry that the architecture happens to enforce.

For the course applications, a robust default stack is: smooth activation ($\tanh$ or Swish), hard BCs when analytically available, adaptive loss balancing, and adaptive collocation near high-residual regions.

## The Deep Galerkin Method (DGM) Architecture

The plain MLP used in the examples so far -- and, below, for the cake-eating HJB -- is sufficient for low-dimensional PDEs with smooth solutions, but its expressive bottleneck shows up in two regimes: (i) genuinely high-dimensional state spaces (where curse-of-dimensionality effects compound across layers), and (ii) PDEs with sharp internal features such as boundary layers, wave fronts, or kinks at policy switches. The Deep Galerkin Method addresses both by adding LSTM-style gates and skip connections from the input to every layer, so that the network can carry input information forward unchanged through depth and route it past intermediate transformations. In the 1D problems studied so far, an MLP and a DGM block train to comparable accuracy and the MLP is preferred for transparency; the architectural complexity pays off as dimension grows or sharp features appear. Table {numref}`tab-mlp_vs_dgm` gives a qualitative comparison across the problem classes treated in this chapter; the chapter's exercises invite a concrete benchmark of the two architectures on the same PDE.

````{table}
:name: tab-mlp_vs_dgm

Qualitative MLP vs. DGM comparison across the problem classes of this chapter. "Comparable" means the two architectures train to similar final residual at similar wall time; "preferred" indicates which one a practitioner should reach for first. A quantitative benchmark on a fixed pair (residual, wall time, parameters) is the natural project extension and is not run here.

| **Problem class** | **MLP** | **DGM** | **Where DGM helps** |
|---|:---:|:---:|---|
| 1D ODE ({ref}`sec-bc_soft_hard`) | comparable | comparable | not in 1D smooth problems; MLP preferred for transparency |
| 2D Poisson ({ref}`sec-bc_soft_hard`) | comparable | comparable | marginally, on stiff sources |
| Cake-eating HJB ({ref}`sec-cake_eating_hjb`) | preferred | comparable | MLP wins when hard BCs already kill the boundary loss; DGM wins if kinks at policy-switching points dominate |
| Black--Scholes ({ref}`sec-bs_pinn`) | adequate | cleaner near kink | sharp payoff kink at $S=K$; DGM gates absorb local geometry better |
| High-dim HJB ($d\gtrsim 4$) | curse of dim. visible | preferred | input-skip connections retain raw coordinates at every depth, mitigating expressivity loss across layers |
````

For high-dimensional PDEs, {cite:t}`sirignano2018dgm` introduced the Deep Galerkin Method (DGM), an architecture with LSTM-style gating {cite:p}`hochreiter1997long` and skip connections from the input layer to every hidden layer reminiscent of Highway Networks {cite:p}`srivastava2015highway` (the immediate precursor of ResNets, in which a learned gate controls how much of the previous representation is carried forward unchanged versus transformed).[^2] A related deep BSDE-based formulation was introduced by {cite:t}`e2017deep` (E--Han--Jentzen) and developed in the companion paper of {cite:t}`han2018solving` (Han--Jentzen--E). An accessible exposition of DGM together with several PDE applications is given by {cite:t}`al2018solving`, which also introduces the gate naming convention adopted below. The original DGM architecture of {cite:t}`sirignano2018dgm` uses four gates at each layer $l$:

$$
\begin{aligned}
Z^{(l)} &= \sigma\!\big(\W_z^{(l)} \a^{(l-1)} + \bm{U}_z^{(l)} \x + \bb_z^{(l)}\big), && \text{(update gate)} \\
G^{(l)} &= \sigma\!\big(\W_g^{(l)} \a^{(l-1)} + \bm{U}_g^{(l)} \x + \bb_g^{(l)}\big), && \text{(forget gate)} \\
R^{(l)} &= \sigma\!\big(\W_r^{(l)} \a^{(l-1)} + \bm{U}_r^{(l)} \x + \bb_r^{(l)}\big), && \text{(relevance gate)} \\
H^{(l)} &= \tanh\!\big(\W_h^{(l)} (R^{(l)} \odot \a^{(l-1)}) + \bm{U}_h^{(l)} \x + \bb_h^{(l)}\big), && \text{(candidate state)}
\end{aligned}
$$

and the state update is:

$$
\a^{(l)} = (1 - G^{(l)}) \odot H^{(l)} + Z^{(l)} \odot \a^{(l-1)}.
$$

Note that this formulation uses two separate gates: $Z^{(l)}$ controls how much of the previous state $\a^{(l-1)}$ to retain, while $(1 - G^{(l)})$ scales the new candidate $H^{(l)}$. Because $Z$ and $G$ are independent in the original Sirignano--Spiliopoulos formulation, the two coefficients need not sum to one. A simpler GRU-style variant {cite:p}`cho2014gru` collapses the two gates into a single convex combination $\a^{(l)} = (1-G) \odot \a^{(l-1)} + G \odot H$, where the coefficients sum to one; in practice, both variants perform comparably on the PDE benchmarks in this course. The gate $R^{(l)}$ controls which parts of the previous state are relevant for computing the candidate $H^{(l)}$. The gate naming convention $(Z,G,R,H)$ used here follows {cite:t}`al2018solving`; in GRU terminology, $Z$ corresponds to the update gate and $R$ to the reset gate. The input $\x$ enters every layer through the $\bm{U}$ matrices, providing skip connections that ensure input information is available at every depth. This gating mechanism, directly analogous to LSTM recurrent networks, helps the DGM architecture learn functions that depend sensitively on the input coordinates, a common feature of PDE solutions near boundary layers. Figure {numref}`fig-dgm_architecture` shows the resulting feed-forward architecture.

```{figure} figures/fig-dgm_architecture.svg
:name: fig-dgm_architecture

The DGM (Deep Galerkin Method) architecture of . The input $\x$ feeds the first layer through a standard forward path (solid arrows) and is, in addition, routed to every subsequent DGM block via skip connections (dashed arrows), so each layer can see $\x$ directly as well as the running hidden state. Each DGM block combines $\x$ with the hidden state through update, forget, and relevance gates (see body text), in the spirit of LSTM/GRU recurrences applied across depth rather than time.
```

##### Stationary vs. evolutionary PDEs.

The PINN framework applies uniformly to both *stationary* PDEs, where the unknown depends only on state variables ($u = u(\mathbf{x})$), and *evolutionary* PDEs, where time enters as an additional input ($u = u(\mathbf{x}, t)$). The network architecture is identical in both cases: only the input dimension changes. The HJB equation below is stationary: the value function $V(a)$ depends on a single state variable. The Black--Scholes PDE of Section {ref}`sec-bs_pinn` is evolutionary: $V(S,t)$ depends on both the asset price and time to maturity.

(sec-cake_eating_hjb)=
## Application: HJB Equation and the Cake-Eating Problem
```{prf:remark}

In this section, $\gamma$ denotes the coefficient of relative risk aversion (CRRA), with utility $c^{1-\gamma}/(1-\gamma)$. This convention differs from Chapter {ref}`ch-irbc`, where $\gamma_j$ denotes the intertemporal elasticity of substitution (IES $= 1/\text{CRRA}$). Both conventions are standard in their respective literatures.
```


Consider a household with wealth $a(t) > 0$ that chooses a consumption stream $c(t) \geq 0$ to maximize discounted lifetime utility:

$$
\max_{\{c(t)\}_{t \geq 0}} \int_0^\infty e^{-\rho t}\,\frac{c(t)^{1-\gamma}}{1-\gamma}\,dt
\quad\text{s.t.}\quad \dot{a}(t) = r\,a(t) - c(t),
$$ (eq-cake_problem)

where $\rho > 0$ is the subjective discount rate, $\gamma > 0$ ($\gamma \neq 1$) is the coefficient of relative risk aversion (CRRA), and $r$ is the interest rate on wealth. The budget constraint says that wealth grows at rate $r$ minus consumption; we call this the "cake-eating" problem in a loose sense because the household consumes out of a single finite stock of wealth. Strictly speaking, the textbook cake-eating problem has $r = 0$ (the cake does not grow); the $r > 0$ variant solved here is the consumption--savings problem with deterministic returns, and {prf:ref}`ex-ch7-3` traces the $r = 0$ limit explicitly. The dynamic-programming perspective is classical in economics; see {cite:t}`stokeylucas1989` for the standard textbook treatment. Conceptually, this is the same recursive optimization that produced the discrete-time Bellman equations of Chapters {ref}`ch-deqn`--{ref}`ch-irbc`; the only difference is that the household now optimizes over a continuous time grid, so the resulting optimality condition is a partial differential equation (the HJB) rather than an algebraic Euler equation. The derivation below makes this $\Delta t \to 0$ link precise.

##### Deriving the HJB equation.

Define the *value function* $V(a)$ as the maximum attainable lifetime utility starting from wealth $a$:

$$
V(a) = \max_{\{c(t)\}} \int_0^\infty e^{-\rho t}\,\frac{c(t)^{1-\gamma}}{1-\gamma}\,dt.
$$ (eq-cake_value)

Since the problem is stationary (no explicit time dependence in the return or the law of motion), $V$ depends only on the current state $a$, not on calendar time.

To derive the HJB equation, apply the *principle of optimality*: over a short interval $[0, \Delta t]$, the household chooses $c$ optimally and then continues optimally from the resulting state $a + \dot{a}\,\Delta t$. This gives:

$$
V(a) = \max_c \left\{\frac{c^{1-\gamma}}{1-\gamma}\,\Delta t + e^{-\rho\,\Delta t}\,V\!\bigl(a + (ra - c)\,\Delta t\bigr)\right\} + \mathcal{O}(\Delta t^2).
$$ (eq-cake_bellman_dt)

Now expand both the discount factor and the value function to first order in $\Delta t$:

$$
e^{-\rho\,\Delta t} \approx 1 - \rho\,\Delta t
$$ (eq-cake_expand_disc)

$$
V\!\bigl(a + (ra - c)\,\Delta t\bigr) \approx V(a) + V'(a)\,(ra - c)\,\Delta t.
$$ (eq-cake_expand_V)

```{prf:remark}

The expansion {eq}`eq-cake_expand_V` silently assumes that $V$ is differentiable at $a$. When $V$ has a kink, a common feature of HJB solutions, e.g. at borrowing constraints or policy-switching points, the expansion still holds, but $V'(a)$ must be replaced by the appropriate *one-sided* derivative chosen by the sign of the drift $(ra-c)$. This is exactly the origin of the upwind scheme used in finite-difference HJB solvers: the side of the derivative is selected to follow information flow. PINNs that minimize the strong-form residual implicitly demand two-sided differentiability and therefore tend to over-smooth genuine kinks, one of the mechanisms behind the oscillatory failure mode in Table {numref}`tab-pinn_failure_modes`.
```


Substituting {eq}`eq-cake_expand_disc` and {eq}`eq-cake_expand_V` into {eq}`eq-cake_bellman_dt`:

$$
V(a) = \max_c \left\{\frac{c^{1-\gamma}}{1-\gamma}\,\Delta t + (1 - \rho\,\Delta t)\Bigl[V(a) + V'(a)(ra-c)\,\Delta t\Bigr]\right\} + \mathcal{O}(\Delta t^2).
$$

Expanding the product and dropping terms of order $(\Delta t)^2$:

$$
V(a) = \max_c \left\{\frac{c^{1-\gamma}}{1-\gamma}\,\Delta t + V(a) + V'(a)(ra-c)\,\Delta t - \rho\,V(a)\,\Delta t\right\} + \mathcal{O}(\Delta t^2).
$$

Cancel $V(a)$ from both sides, divide by $\Delta t$, and let $\Delta t \to 0$:

$$
\boxed{\rho\, V(a) = \max_c \left\{\frac{c^{1-\gamma}}{1-\gamma} + V'(a)\,(ra - c)\right\}.}
$$ (eq-cake_hjb)

This is the *Hamilton--Jacobi--Bellman (HJB) equation*. The left-hand side is the "cost of holding wealth $a$" (the required return $\rho V$). The right-hand side is the "benefit": instantaneous utility from consuming $c$, plus the capital gain $V'(a)\,\dot{a}$ from the change in wealth.

##### First-order condition and optimal consumption.

The maximization in {eq}`eq-cake_hjb` is over $c$ with the objective being concave in $c$ (since $\gamma > 0$). Differentiating the term inside the braces with respect to $c$ and setting to zero:

$$
\frac{\partial}{\partial c}\left[\frac{c^{1-\gamma}}{1-\gamma} + V'(a)(ra - c)\right]
= c^{-\gamma} - V'(a) = 0
\qquad\Longrightarrow\qquad
c^\star(a) = \bigl(V'(a)\bigr)^{-1/\gamma}.
$$ (eq-cake_foc)

The economic content is intuitive: the marginal utility of consumption $c^{-\gamma}$ equals the marginal value of wealth $V'(a)$. A higher $V'(a)$ (wealth is more valuable) implies lower optimal consumption.

##### Analytical solution.

The HJB {eq}`eq-cake_hjb` with the FOC {eq}`eq-cake_foc` substituted in becomes a nonlinear ODE in $V(a)$. To solve it, conjecture $V(a) = \Lambda\, a^{1-\gamma}/(1-\gamma)$ for some constant $\Lambda > 0$. Then $V'(a) = \Lambda\, a^{-\gamma}$, and from the FOC {eq}`eq-cake_foc`:

$$
c^\star = (\Lambda\, a^{-\gamma})^{-1/\gamma} = \Lambda^{-1/\gamma}\, a.
$$

Substituting into the HJB:

$$
\rho\,\Lambda\,\frac{a^{1-\gamma}}{1-\gamma}
= \frac{(\Lambda^{-1/\gamma}\,a)^{1-\gamma}}{1-\gamma} + \Lambda\, a^{-\gamma}\bigl(ra - \Lambda^{-1/\gamma}\,a\bigr).
$$

Dividing through by $a^{1-\gamma}/(1-\gamma)$ and solving for $\Lambda$ gives $\Lambda = \kappa^{-\gamma}$ with $\kappa = (\rho - (1-\gamma)r)/\gamma$, so $V^\star(a) = \kappa^{-\gamma}\,a^{1-\gamma}/(1-\gamma)$ and the optimal consumption rule is $c^\star(a) = \kappa\, a$. This solution is well-defined provided $\kappa > 0$, i.e., $\rho > (1-\gamma)r$, a standard transversality condition ensuring that the agent discounts future utility sufficiently relative to wealth growth. This closed form is the natural validation target for the PINN in notebook `lecture_11_04_Cake_Eating_HJB_PINN`: the trained network should recover $V(a)$ to mean relative error well below $10^{-3}$, and any larger discrepancy signals an under-trained network or a malformed loss.

##### PINN formulation and PDE residual.

To solve the HJB equation {eq}`eq-cake_hjb` with a PINN (rather than using the closed-form above), we proceed as follows. A neural network $\hat{V}(a) = \mathcal{N}_\theta(a)$ approximates the value function. Its derivative $\hat{V}'(a)$ is computed by automatic differentiation up to floating-point precision, so no finite differences are needed. From this derivative, we reconstruct the optimal consumption via the FOC {eq}`eq-cake_foc`:

$$
\hat{c}(a) = \bigl(\hat{V}'(a)\bigr)^{-1/\gamma}.
$$

Substituting $\hat{V}$, $\hat{V}'$, and $\hat{c}$ into the HJB {eq}`eq-cake_hjb` and moving everything to one side defines the *PDE residual*. In practice both the FOC inversion and the residual evaluation use a positivity-guarded derivative $\widetilde V_a := \operatorname{softplus}(\hat V'(a)) + \varepsilon$ rather than the raw $\hat V'(a)$, so that consumption is well-defined even where the network's raw derivative is negative during early training (see also the listing below):

$$
\hat{c}(a) = \widetilde V_a^{-1/\gamma}, \qquad
\mathcal{R}(a) = \rho\,\hat{V}(a) - \left[\frac{\hat{c}(a)^{1-\gamma}}{1-\gamma} + \widetilde V_a\,(ra - \hat{c}(a))\right].
$$ (eq-cake_residual)

Once training has converged with $\hat V'(a) \gg 0$ on the support, $\operatorname{softplus}(\hat V'(a)) \approx \hat V'(a)$ to high precision (the exponential tail decays rapidly), so the safeguarded residual is asymptotically equivalent to the original HJB residual; using $\widetilde V_a$ throughout keeps the FOC inversion and the HJB residual mutually consistent during training, when $\hat V'(a)$ may transiently be small or negative. If the network has perfectly learned the true value function, $\mathcal{R}(a) = 0$ for all $a$. The PINN loss is the mean squared residual over a set of collocation points $\{a_i\}_{i=1}^M$ sampled in the interior of the domain:

$$
\ell_{\mathrm{HJB}} = \frac{1}{M}\sum_{i=1}^{M} \mathcal{R}(a_i)^2.
$$

The DGM (Deep Galerkin Method) architecture of {cite:t}`sirignano2018dgm`, which provides LSTM-style gating and skip connections from the input to every hidden layer, may be used in place of the plain MLP below to improve expressivity for this type of PDE problem; the listing keeps a plain MLP for clarity. In low dimension the trial-solution MLP of notebook `lecture_11_04_Cake_Eating_HJB_PINN` typically outperforms a soft-BC DGM, because the boundary loss no longer competes with the interior residual; DGM becomes worthwhile primarily in higher dimensions or for PDEs with sharp internal features.

```{prf:remark}

A small HJB residual is necessary but not sufficient for an economically meaningful solution. The same residual minimum can correspond to wildly different value-function levels when the boundary anchor is weak, and to spurious non-monotonic policies when $\hat V'(a) \le 0$ is left unpenalized. Practical safeguards used in notebook `lecture_11_04_Cake_Eating_HJB_PINN`: (i) hard-BC trial solution that fixes both endpoints exactly, removing the boundary--interior trade-off; (ii) a softplus-transformed derivative $\widetilde V_a=\operatorname{softplus}(\hat V_a)+\varepsilon$ inside the FOC inversion, eliminating the negative-derivative pathology in training; (iii) checking the implied consumption policy, the raw derivative $\hat V_a$, and the HJB residual against the closed-form benchmark. When the residual, boundary conditions, and policy diagnostics agree, the solution is also economically sensible; when only the HJB residual is small, it usually is not.
```


```{prf:remark}

The PINN notebooks of this chapter use a two-stage pipeline: *Adam* on resampled collocation points to find a basin of attraction, then a *deterministic L-BFGS* polish on a fixed grid in float64. Two practical points are not cosmetic. First, switching collocation points each L-BFGS evaluation breaks the strong Wolfe line search; the polish requires a deterministic objective. Second, second derivatives of a $\tanh$ MLP lose substantial precision in float32, which is exactly the scale L-BFGS probes when comparing successive line-search points. FP64 is therefore a stability device, not a guarantee of machine-precision residuals: in a longer `teaching`/`production` run, the one-dimensional cake HJB reaches final HJB loss about $3\times 10^{-4}$ (the checked-in `RUN_MODE="smoke"` notebook stops well short of that), while the heterogeneous-agent examples still require residual, policy, density, and aggregate diagnostics. Recent quantitative discussions of PINN precision and floating-point limits are reviewed in the further-reading list at the end of the chapter.
```


```{code-block} text
:caption: PINN residual for the HJB equation (PyTorch).

def pde_residual(model, a, gamma, rho, r):
    a.requires_grad_(True)
    V = model(a)
    V_a = torch.autograd.grad(V.sum(), a, create_graph=True)[0]
    safe_Va = F.softplus(V_a) + 1e-6    # positivity guard; +1e-6 avoids division by zero in safe_Va.pow(-1/gamma)
    c = safe_Va.pow(-1.0 / gamma)        # FOC
    u_c = c.pow(1 - gamma) / (1 - gamma)
    R = rho * V - (u_c + safe_Va * (r * a - c))
    return R
```
(sec-ct_hank)=
## Continuous-Time Heterogeneous Agent Models
Many frontier models in macroeconomics feature a continuum of agents who face idiosyncratic risk and interact through equilibrium prices. Chapter {ref}`ch-young` studied the discrete-time version with Young's histogram method inside a DEQN. In continuous time the same economic question becomes a *coupled PDE system*: a Hamilton--Jacobi--Bellman equation for individual optimization and a Kolmogorov forward (Fokker--Planck) equation for the stationary cross-sectional density, closed by a market-clearing condition that pins down prices. This is the canonical example of a PINN applied to a *system* of equilibrium PDEs, in contrast to the single HJB of the cake-eating problem ({ref}`sec-cake_eating_hjb`) and the single Black--Scholes PDE ({ref}`sec-bs_pinn`): a PINN parameterizes the value function and the density by two networks $\hat V_\theta(a,z)$, $\hat g_\psi(a,z)$ and minimizes a four-term loss -- the HJB residual, the KFE residual, the no-flux boundary residual at the borrowing constraint, and a mass-normalization residual -- with the loss-balancing and boundary-layer issues familiar from the rest of this chapter.

The full development -- the stochastic-calculus background, the formal HJB and KFE derivations, the Huggett and Aiyagari equilibria, the PINN solver for the stationary coupled system, the master equation that handles aggregate shocks, and the EMINN method -- is the subject of Chapter {ref}`ch-ct_theory`: see {ref}`sec-ct_equilibrium` and {ref}`sec-ct_pinn` for the stationary problem and {ref}`sec-master_eq`--{ref}`sec-eminn` for the aggregate-shock case. Following {cite:t}`achdou2022income` for the model setup (whose own numerical solution uses finite differences), that treatment replaces the traditional fixed-point iteration over $r$ with joint training of all components.

(sec-bs_pinn)=
## Application: Black--Scholes PDE
The Black--Scholes PDE has a closed-form solution, so a PINN run on it is not motivated by the absence of an analytical answer. The pedagogical purpose is exactly the opposite: it is a known-answer benchmark. We verify that the same PINN recipe (smooth activations, hard or soft BCs, autodiff for $V_S$ and $V_{SS}$, Adam-then-L-BFGS) reproduces a textbook formula on a clean domain before applying it to PDEs without closed forms (American options, jump diffusions, multi-asset pricing, HJBs with multiple state variables). If the network cannot recover Black--Scholes to plotting accuracy, no further trust should be placed in its output on harder problems.

The Black--Scholes PDE for a European call option with strike $K$, maturity $T$, risk-free rate $r$, and volatility $\sigma$ is the canonical option-pricing benchmark of {cite:t}`black1973pricing`:

$$
\frac{\partial V}{\partial t} + \frac{1}{2}\sigma^2 S^2 \frac{\partial^2 V}{\partial S^2} + rS\frac{\partial V}{\partial S} - rV = 0,
$$

with terminal condition $V(S,T) = \max(S-K, 0)$ and boundary conditions $V(0,t)=0$, $V(S_\mathrm{max}, t) = S_\mathrm{max} - Ke^{-r(T-t)}$.

The PINN approach approximates $V(S,t) \approx \mathcal{N}_\theta(S,t)$ and computes the partial derivatives $V_t$, $V_S$, and $V_{SS}$ via automatic differentiation. The total PINN loss for the Black--Scholes problem has four terms:

$$
\begin{aligned}
\ell ={}& \underbrace{\frac{1}{N_r}\sum_i
\left|V_t(S_i^r,t_i^r) + \tfrac{1}{2}\sigma^2 (S_i^r)^2 V_{SS}(S_i^r,t_i^r)
+ rS_i^r V_S(S_i^r,t_i^r) - rV(S_i^r,t_i^r)\right|^2}_{\text{PDE residual}} \\
&+ \underbrace{\frac{\lambda_\mathrm{TC}}{N_T}\sum_j \left|V(S_j,T) - \max(S_j-K,0)\right|^2}_{\text{terminal condition}}
+ \underbrace{\frac{\lambda_0}{N_0}\sum_k \left|V(0,t_k)\right|^2}_{\text{lower BC}} \\
&+ \underbrace{\frac{\lambda_\infty}{N_\infty}\sum_l
\left|V(S_\mathrm{max},t_l) - \bigl(S_\mathrm{max}-Ke^{-r(T-t_l)}\bigr)\right|^2}_{\text{upper BC}} .
\end{aligned}
$$

The loss has four terms (PDE residual, terminal condition, lower BC, upper BC) and three relative penalty weights $(\lambda_\mathrm{TC}, \lambda_0, \lambda_\infty)$; the PDE residual coefficient is normalized to one. These weights must be tuned or adaptively balanced via ReLoBRaLo from Chapter {ref}`ch-nas`. As a practical diagnostic of what goes wrong if the weights are mis-set: underweighting $\lambda_{\mathrm{TC}}$ produces a smooth surface that mis-prices the payoff at maturity (the network ignores the kink at $S=K$); overweighting $\lambda_{\mathrm{TC}}$ pins the network at $t=T$ but the interior PDE residual then fails to balance the $V_t$ term, producing visible drift in the early-time slice. In notebook `lecture_11_05_Black_Scholes_PINN`, the benchmark parameters are $K=50$, $T=1$, $r=0.05$, $\sigma=0.2$, and $S_\mathrm{max}=100$, for which the analytical at-the-money call value is roughly $4.8$. A longer `teaching`/`production` run reports a max absolute error around $0.13$ and a mean absolute error around $0.04$ against the analytical Black--Scholes formula (the checked-in `smoke` notebook prints larger errors); at the ATM value scale this is roughly a $2.7\%$ peak and $0.8\%$ average relative error. Accuracy is therefore a diagnostic to check after training, not a guaranteed property of the architecture. The choice of $\tanh$ is natural here: it is $C^\infty$ (so $V_{SS}$ is well-defined everywhere), and its bounded range $(-1,1)$ provides a stable starting point for learning the option price surface.

(sec-operator_learning_bridge)=
## From PINNs to Operator Learning: One Network, Many Problems
*This section is script-only outlook material; it has no companion slide and no notebook. It can be skipped on a first read without loss of continuity, and is intended for readers preparing to scale a PINN-based pipeline across many parameter configurations.*

A PINN learns *one solution* to one PDE. Each new boundary condition, parameter set, or coefficient field forces a fresh training run. In economic and financial applications this is often exactly the bottleneck: we want option prices for many strike--maturity pairs, value functions for many discount factors, or HJB solutions across an entire parameter sweep. *Operator learning* flips the question: instead of learning a function $u : \mathbb{R}^d \to \mathbb{R}$ that solves the PDE for a single instance, one learns the *solution operator* $$\mathcal{G}: \;\;\text{(input field, BCs, parameters)} \;\longmapsto\; \text{solution function } u,$$ i.e. a map between two function spaces.

Two mature architectures dominate the literature.

##### DeepONet {cite:p}`lu2021learning`.

Inspired by the universal-approximation theorem for nonlinear operators, DeepONet uses two sub-networks: a *branch net* encodes the input field at sensor locations into a latent vector, and a *trunk net* encodes the query point at which the output is requested; their inner product is the predicted operator output. The architecture is generic and trains entirely on input--output pairs of an offline solver.

##### Fourier Neural Operator (FNO) {cite:p}`li2021fourier`.

FNO parameterizes a kernel integral operator by truncating it in Fourier space and applying a learned linear transformation to the low-frequency modes per layer. This captures global interactions cheaply ($\mathcal{O}(n\log n)$ via FFT) and exhibits resolution invariance: a network trained on one grid can be evaluated on a finer grid at test time.

```{figure} figures/fig-operator_learning_bridge.svg
:name: fig-operator_learning_bridge

Operator learning generalizes PINNs by amortising over an entire parametric family of PDEs. For economic applications such as option-price surfaces over (K, T), value functions across a parameter range, or HJB sweeps for sensitivity analysis (Chapter {ref}`ch-gp`), training the operator once gives instant predictions at test time.
```

Figure {numref}`fig-operator_learning_bridge` summarizes this progression from one-instance PINNs to operator-learning architectures. In the rest of this script, we mostly stay with PINNs because the focus is on solving one model carefully; we revisit operator learning briefly in Chapter {ref}`ch-outlook` and point readers who want to amortise across an entire parametric family of PDEs to {cite:t}`lu2021learning` {cite}`li2021fourier`.

```{prf:remark}

PINNs approximate PDE solutions by minimizing the residual at collocation points, with automatic differentiation supplying the required derivatives algorithmically up to floating-point precision {cite:p}`raissi2019physics`. Hard versus soft enforcement of boundary conditions is the central design lever: trial-function constructions of the form $\hat y = A(x) + B(x)\mathcal{N}_\theta(x)$ enforce BCs by construction, while soft penalties cover cases where hard enforcement is intractable. For second-order PDEs (HJB, Black--Scholes, Poisson) the activation must be at least $C^2$, which excludes ReLU and makes $\tanh$ and Swish the standard choices. Operator learning (DeepONet, FNO) is the natural generalization when one wants to amortise across a parametric family rather than solve one instance.
```


(further-reading)=
## Further Reading
- {cite:t}`raissi2019physics`, the foundational PINN paper.

- {cite:t}`sirignano2018dgm`, the Deep Galerkin Method, the original deep-PDE solver in finance.

- {cite:t}`e2017deep` {cite}`han2018solving`, deep BSDE methods, the SDE counterpart.

- {cite:t}`wang2021understanding` {cite}`bischof2025relobralo`, adaptive loss balancing for PINNs.

- {cite:t}`lu2021deepxde`, the DeepXDE software ecosystem.

(exercises)=
## Exercises
Worked solutions and guidance for these exercises appear in Appendix {ref}`app-solutions`.

```{exercise}
:label: ex-ch7-1

**[Core\] Trial-function BC enforcement.** For the BVP $y'' + y = 0$ on $[0,\pi/2]$ with $y(0)=0$, $y(\pi/2)=1$, verify that $\hat y(x) = 2x/\pi + x(\pi/2-x)\,\mathcal{N}_\theta(x)$ satisfies both BCs for any network output. Why is this preferable to a soft penalty?
```

```{exercise}
:label: ex-ch7-2

**[Core\] ReLU pathology.** Explain why a ReLU network is unsuitable for the strong-form Black--Scholes residual. Then sketch a weak-form formulation that would work with ReLU activations.
```

```{exercise}
:label: ex-ch7-3

**[Core\] Discrete $\to$ continuous bridge.** Take the discrete-time Bellman operator $$V(a) = \max_c \bigl[u(c)\,\Delta t + \beta_{\Delta t}\,\E V(a')\bigr],
\qquad
a' = a - c\,\Delta t,
\qquad
\beta_{\Delta t}=e^{-\rho\Delta t}.$$ Show that as $\Delta t \to 0$ it formally yields the HJB $\rho V = \max_c [u(c) - V'(a)\,c]$. (This is the pure cake-eating problem with $r=0$; including a return $r$ on wealth, $\dot a = ra - c$, recovers {eq}`eq-cake_hjb`.)
```

```{exercise}
:label: ex-ch7-4

**[Computational\] BC penalty weight $\lambda$ tuning.** In notebook `lecture_11_02_ODE_PINN_SoftVsHardBCs`, run the soft-BC variant with PDE residual $\ell_\mathrm{int}$ and BC residual $\ell_\mathrm{BC}$ combined as $\mathcal{L} = \ell_\mathrm{int} + \lambda\,\ell_\mathrm{BC}$ (the notebook exposes $\lambda$ as the `bc_weight` hyperparameter dispatched from `RUN_MODE`) for $\lambda \in \{10^{-1}, 10^0, 10^1, 10^2, 10^3,10^4\}$. For each, train to a fixed budget of $5{,}000$ iterations and record (i) the BC violation $|\hat y(0) - y_0|$ at convergence, (ii) the maximum interior residual, and (iii) training wall time. Plot all three on log--log axes against $\lambda$, identify the elbow at which boundary fit stops improving cheaply, and compare against the hard-BC variant.
```

```{exercise}
:label: ex-ch7-5

**[Advanced/project\] Collocation strategy comparison.** In notebook `lecture_11_03_PDE_PINN_Poisson2D` solving $\Delta u = f$ on $[0,1]^2$ with Dirichlet BCs, replace the default uniform-random collocation with (a) Latin Hypercube sampling, (b) a Sobol low-discrepancy sequence, (c) residual-based adaptive sampling that draws each batch of collocation points proportional to the residual magnitude at the current iterate. Train each variant to the same residual tolerance ($10^{-4}$) and report (i) the number of collocation points needed, (ii) the wall time, (iii) the spatial distribution of final residuals (compute $\sup_x |\Delta u_\theta - f|$ on a fine $200\times 200$ test grid). Discuss when each strategy is preferred: uniform for smooth problems, low-discrepancy for moderately rough, adaptive for problems with localized features (e.g., near boundary layers).
```

```{exercise}
:label: ex-ch7-6

**[Advanced/project\] Strong vs. weak forms.** Extend the Black--Scholes notebook. First compare the current strong-form $\tanh$ PINN with a ReLU version and explain why the second derivative term is problematic for ReLU. Then derive a weak-form variant: multiply the residual by a smooth test function $\varphi$ supported inside $[0,S_\mathrm{max}]$, integrate by parts to move the second derivative onto $\varphi$, and state which derivatives of $V$ remain. If you implement the weak-form ReLU variant, compare its held-out pricing error with the strong-form $\tanh$ baseline. Connect the result to {prf:ref}`ex-ch7-2`.
```

```{exercise}
:label: ex-ch7-7

**[Core\] Operator learning vs. PINN.** For an option pricing problem where the strike $K$ varies across $\{45,46,\ldots,55\}$, count the training cost of (a) eleven independent PINN runs vs. (b) one operator-learning or parametric-PINN run that takes $K$ as an input; see Section {ref}`sec-operator_learning_bridge` and Chapter {ref}`ch-outlook`. At what cost ratio does amortized training win?
```

[^1]: Automatic differentiation is the algorithmic backbone of every deep-learning framework discussed in this script; {cite:t}`baydin2018automatic` survey forward- and reverse-mode AD, the dual-number and tape-based implementations, and the practical trade-offs that determine why reverse mode is the standard for neural-network training (one backward pass costs roughly the same as one forward pass, irrespective of the parameter count).

[^2]: Notation reuse: the gate $G^{(l)}$ in the DGM block below is unrelated to the cross-sectional density $g$ that appears in heterogeneous-agent models (Chapters {ref}`ch-young`, {ref}`ch-ct_theory`); the symbols share a letter only.
