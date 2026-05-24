---
title: "Structural Estimation via SMM"
label: ch-estimation
---

With the surrogate machinery of Chapter {ref}`ch-gp` in hand, we now turn to one of its most important applications: *structural estimation*. The chapter's companion notebooks use the Brock--Mirman growth model to estimate first the productivity persistence parameter $\varrho$, and then the pair $\theta=(\beta,\varrho)$, by Simulated Method of Moments (SMM). The key computational idea is the same in both cases: train one policy surrogate with the structural parameter as an additional input, then reuse that trained network inside the estimator instead of re-solving the dynamic program at every candidate parameter value. The econometric foundations are {cite:t}`mcfadden1989method`, {cite:t}`pakes1989simulation`, {cite:t}`lee1991simulation`, {cite:t}`duffie1993simulated`, and {cite:t}`gourieroux1993indirect`; the surrogate logic follows the deep-surrogate and GP-surrogate pipelines in {cite:t}`chen2026Deep` and {cite:t}`SCHEIDEGGER201968`. Recent applications of the same surrogate-then-estimate move include heterogeneous-agent estimation {cite:p}`kase2022estimating`, search-and-matching {cite:p}`payne2025deepsam`, and climate-economy policy design and uncertainty quantification {cite:p}`kubler2025using,friedlDeep2023`.

Before the current deep-learning boom, neural networks were already studied as nonlinear *sieve* estimators in econometrics, with a rigorous asymptotic theory developed in parallel with the approximation-theory results of Chapter {ref}`ch-intro`. {cite:t}`chenwhite1999improved` establish convergence rates and asymptotic normality for single-hidden-layer network estimators, and {cite:t}`chen2007sieve` integrates that line into the broader sieve treatment of semi-nonparametric models defined by conditional moment restrictions, which is precisely the structural-estimation setting of this chapter. The modern continuation of this program uses deep architectures for efficient estimation in nonparametric instrumental-variable models {cite:p}`chenChristensenKankanala2021npiv`. The pipelines developed below should be read as the implementation-side companion to that theoretical tradition: the sieve literature tells us *when* neural-network estimators consistently identify deep structural parameters; the surrogate pipelines tell us *how* to make the resulting estimators cheap enough to deploy at research scale.

```{prf:remark}

1.  **The pseudo-state trick.** Concatenate the structural parameter $\theta$ into the network input, $(s, \theta) \mapsto \mathcal{N}_\rho(s, \theta)$, and train one network that encodes a *family* of policies indexed by $\theta$. Each new $\theta$ evaluation then requires a single forward pass through the trained network, not a re-solve of the dynamic program; this is what makes SMM with a deep structural model tractable.

2.  **Two-layer surrogates.** Stack a Gaussian-process surrogate on top of the policy net ({ref}`sec-smm_gp_moments`): Layer 1 (the policy net) turns "one re-solve per $\theta$" into "one forward simulation per $\theta$", and Layer 2 (a GP per moment) turns "one forward simulation per $\theta$" into "one GP posterior per $\theta$". The result is a microseconds-per-call moment map, enabling bootstrap, Bayesian post-processing, and policy search at scale.
```


## Brock--Mirman with Parameters as Pseudo-States

The stochastic Brock--Mirman model is the partial-depreciation model from Chapter {ref}`ch-deqn`:

$$
\begin{aligned}
Y_t &= z_t K_t^\alpha, \\
C_t + K_{t+1} &= Y_t + (1-\delta)K_t, \\
\log z_{t+1} &= \varrho \log z_t + \sigma_z \varepsilon_{t+1}, \qquad
\varepsilon_{t+1}\sim\mathcal{N}(0,1).
\end{aligned}
$$

We write $\varrho$ for TFP persistence to avoid overloading $\rho$, which elsewhere denotes neural-network parameters. The Python notebooks still use the variable name `rho`; mathematically, that code variable corresponds to $\varrho$.

The network outputs a savings rate, the fraction of current output that is invested. In the single-parameter exercise, $$s_t = \mathcal{N}_{\rho}(z_t,K_t,\varrho) \in (0,1),$$ with $\beta$ calibrated to $0.96$. In the joint exercise the input becomes $(z_t,K_t,\beta,\varrho)$. In either case, recover

$$
\begin{aligned}
K_{t+1} &= (1-\delta)K_t + s_t Y_t, \\
C_t &= (1-s_t) Y_t.
\end{aligned}
$$

Because $s_t \in (0,1)$ and $Y_t > 0$, this parameterization enforces $C_t > 0$, $K_{t+1} > (1-\delta)K_t > 0$, and gross investment $I_t = s_t Y_t \ge 0$ by construction, so the resource constraint and the non-negativity of investment hold automatically and the partial-depreciation Euler equation {eq}`eq-smm_euler_residual` applies as written, with no extra multiplier.[^1]

Training uses the same Euler equation as Chapter {ref}`ch-deqn`, but the residual is evaluated jointly over states and parameter draws. With partial depreciation, $$\frac{1}{C_t}
=
\beta\,\E{\frac{1-\delta+\alpha z_{t+1}K_{t+1}^{\alpha-1}}{C_{t+1}}}.$$ For a sampled state--parameter pair $(z_i,K_i,\theta_b)$, where $\theta_b=\varrho_b$ in the scalar exercise and $\theta_b=(\beta_b,\varrho_b)$ in the joint exercise, the companion notebooks form the *relative* residual

$$
G_i(\theta_b)
=
\frac{1}{\beta_b C_i\,\E{(1-\delta+\alpha z_{i,t+1}(K_i')^{\alpha-1})/C_{i,t+1}}}
-
1,
$$ (eq-smm_euler_residual)

where $Y_i = z_i K_i^\alpha$, $K_i' = (1-\delta)K_i + s_i Y_i$, $C_i = (1-s_i) Y_i$, and $C_{i,t+1}$ is computed by feeding $(z_{i,t+1},K_i',\theta_b)$ back through the same network. The expectation over $z_{i,t+1}$ is approximated by Gauss--Hermite quadrature (Section {ref}`sec-quadrature_rules`). The relative form is preferred to the equivalent absolute residual $1-\beta_b C_i\,\E{\cdot}$ because dividing by the consumption ratio makes the loss scale-free across $(z,K,\theta)$ samples; the two forms share the same zero set but the relative form is better conditioned under FP32 forward passes. A representative training loss is

$$
\ell_\rho
=
\frac{1}{N_sN_\theta}
\sum_{i=1}^{N_s}\sum_{b=1}^{N_\theta}
\left|G_i(\theta_b)\right|^2.
$$

The outer sum over $\theta_b$ is the pseudo-state trick: one network learns a family of policies over the whole parameter rectangle.

(sec-smm_method)=
## Simulated Method of Moments
The pseudo-state surrogate is what makes SMM cheap. Without it, every objective evaluation would re-solve the structural model. With it, the trained policy network and simulator define a fast deterministic map $\theta\mapsto m(\theta)$ once the simulation design is fixed.

The Simulated Method of Moments (SMM) estimates structural parameters by matching model-implied moments to their empirical counterparts. The method was developed as an extension of the Generalized Method of Moments (GMM) to settings where the moment conditions do not have a closed-form expression but can be computed via simulation {cite:p}`mcfadden1989method,pakes1989simulation,lee1991simulation,duffie1993simulated`. A closely related approach is *indirect inference* {cite:p}`gourieroux1993indirect`, which matches the parameters of an auxiliary model rather than raw moments.

In quantitative macro and finance, the same simulated-moments logic is especially useful in sovereign default and incomplete-markets environments, where likelihood-based estimation is either unavailable or prohibitively expensive {cite:p}`arellano2008default`.

Let $\hat{m}^\mathrm{data} \in \R^q$ denote a vector of $q$ sample moments computed from observed data (e.g., mean capital, output variance, consumption autocorrelation), and let $m(\theta) \in \R^q$ denote the corresponding moments simulated from the model at parameter value $\theta \in \R^p$. The SMM estimator solves:

$$
\hat{\theta}_\mathrm{SMM}
=
\argmin_\theta
\underbrace{\bigl(m(\theta)-\hat m^\mathrm{data}\bigr)^\top}_{1\times q}
\underbrace{W}_{q\times q}
\underbrace{\bigl(m(\theta)-\hat m^\mathrm{data}\bigr)}_{q\times 1},
$$ (eq-smm_objective)

where $W \in \R^{q \times q}$ is a symmetric positive definite weighting matrix.

##### The role of the weighting matrix $W$.

The matrix $W$ controls how much weight each moment (and each pair of moments) receives in the objective. To build intuition, consider three common choices:

1.  **Identity weighting** ($W = I_q$): all moments receive equal weight. The objective reduces to the unweighted sum of squared deviations, $\sum_{j=1}^q (m_j(\theta) - \hat{m}_j^\mathrm{data})^2$. This is simple but inefficient: moments measured with high precision receive the same weight as noisy moments.

2.  **Diagonal weighting** ($W = \mathrm{diag}(1/\hat{\sigma}_1^2, \ldots, 1/\hat{\sigma}_q^2)$): each moment is scaled by the inverse of its estimated variance. This corrects for differing units and precision.

3.  **Optimal weighting**: the inverse of the covariance matrix of the *moment discrepancy* $\hat g(\theta)=m(\theta)-\hat m^\mathrm{data}$. If the simulation noise is negligible, this is well approximated by the inverse covariance of the empirical moments. With independent simulated panels of the same length as the data and $S$ replications, the covariance is approximately $(1+1/S)\Sigma_m$, so the optimal weight is proportional to $\Sigma_m^{-1}$ but the scale matters for the $J$-statistic below.

With identity weighting, the criterion is the sum of squared moment deviations; with inverse discrepancy-covariance weighting, it is the squared Mahalanobis distance between simulated and empirical moments.

##### Consistency and efficiency.

Under standard regularity conditions, the SMM estimator is consistent: $\hat{\theta}_\mathrm{SMM} \xrightarrow{p} \theta_0$ as the data sample size $T \to \infty$. Identification requires more than the usual $q \geq p$ moment count: locally, the moment Jacobian must satisfy the rank condition

$$
\mathrm{rank}\bigl(\partial m(\theta_0)/\partial \theta'\bigr) = p,
$$

which is necessary for *local* identification. Note that full column rank is necessary but not sufficient: when the smallest singular value of $M$ is close to zero (a near-singular Jacobian), the parameter is only *weakly* identified in finite samples even though the rank condition formally holds. Global identification additionally requires the population value of the empirical moments, $\bar m := \lim_{T\to\infty}\hat m^\mathrm{data}$, to be matched at a *unique* $\theta_0 \in \Theta$, i.e., $\bar m = m(\theta_0)$ has a unique solution in $\Theta$; the rank condition is the local-curvature implication of that uniqueness. Let $M=\partial m/\partial\theta'|_{\theta_0}$, and let $\Omega$ denote the asymptotic covariance of $\sqrt{T}\hat g(\theta_0)$. The large-sample distribution is

$$
\sqrt{T}\bigl(\hat{\theta}_\mathrm{SMM}-\theta_0\bigr)
\xrightarrow{d}
\mathcal{N}\!\left(
\bm{0},
(M^\top W M)^{-1}M^\top W\Omega W M(M^\top W M)^{-1}
\right).
$$

For $S$ independent simulated panels each of length $\tau T$ (with $\tau \geq 1$ a relative-length factor), $\Omega = (1 + 1/(\tau S))\,\Sigma_m$. The classroom benchmark used below sets $\tau = 1$ (simulated panels of the same length as the data), giving the familiar $\Omega = (1+1/S)\Sigma_m$. As $\tau S \to \infty$, the *extra* simulation variance vanishes and $\Omega \to \Sigma_m$; the factor itself tends to one, not zero. The efficient SMM weight is $W^\star = \Omega^{-1}$. See {cite:t}`duffie1993simulated` for the corresponding large-sample theory in the simulated-moments setting.

## The SMM Workflow in the Exercise

The exercise uses a deliberately simple synthetic-data workflow so that the econometric logic is transparent. First, choose a true parameter and simulate a time series from the trained pseudo-state surrogate. These observations play the role of data. Second, for each candidate parameter, re-simulate the model with the same burn-in length, simulation horizon, initial state, and shock seed. Third, compute a small vector of economically interpretable moments and minimize the quadratic SMM criterion with identity weighting.

##### Single-parameter persistence exercise.

Notebook `lecture_15_03_Structural_Estimation_BM.ipynb` calibrates $\beta=0.96$, sets $\varrho_{\mathrm{true}}=0.90$, and estimates $\varrho\in[0.50,0.99]$. Let $\{C_t(\varrho),I_t(\varrho),Y_t(\varrho)\}_{t=1}^T$ denote a simulated sample at candidate persistence $\varrho$. The estimator uses three moments:

$$
\begin{aligned}
m_1(\varrho) &= \mathrm{std}\!\bigl(\Delta\log C_t(\varrho)\bigr), \\
m_2(\varrho) &= \mathrm{corr}\!\bigl(\Delta\log C_t(\varrho),\Delta\log C_{t-1}(\varrho)\bigr), \\
m_3(\varrho) &= \mathrm{corr}\!\bigl(\log Y_t(\varrho),\log Y_{t-1}(\varrho)\bigr).
\end{aligned}
$$

All three moments are computed on the raw simulated time series with no detrending or demeaning step, and $\mathrm{std}(\cdot)$ and $\mathrm{corr}(\cdot)$ denote sample standard deviation and sample autocorrelation evaluated directly on the simulated panel. The output autocorrelation is the most direct persistence moment. The volatility moment should be interpreted as an empirical simulated moment, not as the level-variance formula. For the AR(1) shock, $$\mathrm{Var}(\log z_t)=\frac{\sigma_z^2}{1-\varrho^2},
\qquad
\mathrm{Var}(\Delta\log z_t)=2\,\mathrm{Var}(\log z_t)\,(1-\varrho)=\frac{2\sigma_z^2}{1+\varrho},$$ so the familiar $1/(1-\varrho^2)$ amplification applies to the *level* of log productivity, not to first differences. The notebook also reports the mean savings rate as a diagnostic and correctly treats it as nearly uninformative for $\varrho$; it is masked out of the SMM criterion in the scalar exercise and used only for visual identification checks.

##### Joint exercise.

Notebook `lecture_15_03b_Structural_Estimation_BM_Joint.ipynb` estimates $\theta=(\beta,\varrho)$, with $\beta\in[0.92,0.99]$ and $\varrho\in[0.50,0.99]$. It uses four candidate moments: mean savings, growth volatility, consumption-growth autocorrelation, and output autocorrelation. The *shallow-ridge two-moment specification* retains $\{\mathrm{std}(\Delta\log C_t),\,\mathrm{corr}(\Delta\log C_t,\Delta\log C_{t-1})\}$ to expose the partial-identification ridge in the criterion surface; the over-identified specification uses all four moments and collapses the ridge around the synthetic truth. Formally the two-moment case is just-identified ($q=p=2$), so we avoid the econometric term *weak identification* (which refers to a near-singular Jacobian asymptotic regime) and use *shallow-ridge* or *partially-identified* for what the criterion-surface picture actually shows.

##### A deterministic objective.

Because the same initial condition and random seed are used for every candidate $\theta$, the map $\theta\mapsto m(\theta)$ is deterministic in the notebooks. This is still standard SMM; the fixed seed is a common-random-numbers device that removes irrelevant simulation noise while we study identification and optimization. In more realistic estimation exercises one averages over multiple replications or increases the simulation length to make Monte Carlo noise negligible. One consequence is worth stating explicitly: because the synthetic data come from the trained surrogate evaluated at the true parameter, and every candidate evaluates the same shock sequence, the SMM criterion attains a near-zero minimum at the truth. This is a clean self-consistency test of the surrogate-SMM pipeline, not a claim about the size of the criterion one would see with real data and independent simulation draws.

##### Implementation.

The single-parameter estimation routine proceeds in two steps:

1.  Evaluate the SMM objective on a coarse grid over $\varrho \in [0.52,0.99]$ (matching the notebook's grid bounds) to verify that the criterion is well behaved and to visualize identification.

2.  Refine the minimizer with a bounded scalar optimizer (e.g. Brent's method).

The joint notebook maps the 2D criterion on a grid, then refines from the grid minimizer using bounded Nelder--Mead. Since the policy surrogate has already been trained, each evaluation of $m(\theta)$ requires only a forward simulation, not a full re-solution of the dynamic program.

##### Interpretation.

If the moments are informative about $\theta$, the objective should be minimized close to the synthetic truth. In the scalar notebook, $\hat\varrho$ is very close to $0.90$ and the fitted policy functions at $\varrho_{\mathrm{true}}$ and $\hat\varrho$ nearly overlap. The joint notebook shows the additional lesson: point estimates can be accurate while the criterion still has weak curvature along one parameter direction, which is why contour plots and Jacobian diagnostics matter. Figure {numref}`fig-smm_2d_criterion` in {ref}`sec-smm_gp_moments` below visualizes both specifications and is worth looking at now to fix the geometric picture in mind.

## Practical Considerations

##### Moment selection and identification.

The choice of moment conditions is critical for identification. In the scalar exercise, autocorrelation moments identify $\varrho$ sharply, while the mean savings rate is nearly flat in $\varrho$. In the joint exercise, the mean savings rate carries most of the information about $\beta$, while persistence moments carry most of the information about $\varrho$. More generally, the number of moments must weakly exceed the number of parameters ($\dim(m)\geq\dim(\theta)$), and the selected moments should move in economically distinct ways as parameters vary.

##### Weighting.

The exercise uses $W=I$ so that the objective is easy to read. In applications, one usually moves to two-step SMM: first estimate $\hat{\theta}_1$ with identity weighting, then estimate the covariance matrix of the moment discrepancy and set $W=\hat{\Omega}^{-1}$ in a second pass. This corrects for different moment scales, moment correlations, and any non-negligible simulation noise. The two-step estimator is asymptotically efficient under *correct specification* and the usual GMM regularity conditions {cite:p}`duffie1993simulated`; under misspecification, the optimal-$W$ estimator can have larger finite-sample mean-squared error than identity weighting, because the efficient weighting is calibrated against the wrong moment-discrepancy distribution.

##### Simulation design.

The notebook fixes the burn-in length, horizon, initial state, and shock sequence across all objective evaluations. This is important because otherwise the optimizer would chase simulation noise rather than structural differences across parameter values. In larger empirical applications, the same idea appears as *common random numbers* (CRN) or replicated simulations: both are classical variance-reduction techniques in stochastic simulation {cite:p}`glasserman2004monte`, and within the simulated-moments setting {cite:t}`mcfadden1989method` emphasized fixing the simulated draws across parameter values to make the moment objective $m(\theta)$ a smooth function of $\theta$ rather than a noisy step function (the asymptotic theory of optimization estimators with simulation is developed in {cite:t}`pakes1989simulation`). The geometric intuition is simple: if every candidate parameter value is evaluated against the *same* draw of innovations, the residual $m(\theta) - m(\theta')$ isolates the structural effect of moving from $\theta$ to $\theta'$ rather than a Monte Carlo accident.

##### Identification diagnostics.

A necessary condition for local identification is that the Jacobian $M=\partial m/\partial\theta'$ has full column rank at the true parameter. In the scalar Brock--Mirman exercise this condition reduces to requiring that at least one selected moment changes with $\varrho$ in a neighborhood of the truth. In the joint exercise, the singular values of $M$ reveal the weak direction associated with $\beta$. Plotting the objective profile or contour is therefore already informative: a clear and well-centered U-shape signals useful identifying variation, whereas a flat ridge or a jagged profile indicates weak identification or excessive simulation noise.

##### Over-identification tests.

When the model is over-identified ($q > p$), report the standard $J$-statistic at the optimum:

$$
J = T \,\hat{g}(\hat{\theta})^\top W \hat{g}(\hat{\theta}), \qquad \hat{g}(\theta)=m(\theta)-\hat{m}^{\mathrm{data}}.
$$

Under correct specification and regularity conditions, $J$ is asymptotically $\chi^2_{q-p}$ when $W=\Omega^{-1}$, the inverse covariance of the moment discrepancy. If $W=\Sigma_m^{-1}$ is used while finite simulation noise remains, the statistic must be scaled accordingly or calibrated by bootstrap. A large $J$ indicates either model misspecification, poorly chosen moments, or underestimated sampling uncertainty in moments.

##### Standard errors and confidence intervals.

In applications, report not only $\hat{\theta}$ but also uncertainty quantification. A plug-in sandwich estimator is:

$$
\widehat{\mathrm{Var}}(\hat{\theta}) =
\frac{1+1/S}{T}\,(\hat{M}^\top W \hat{M})^{-1}\hat{M}^\top W \hat{\Sigma} W \hat{M}(\hat{M}^\top W \hat{M})^{-1},
$$

where $\hat{M}$ and $\hat{\Sigma}$ are estimated at $\hat{\theta}$ under the equal-length independent-simulation approximation. For small samples, time-series dependence, or highly nonlinear criteria, moving-block or parametric bootstrap intervals are often more reliable than first-order asymptotics.

##### Weak-identification workflow.

If the smallest singular values of $\hat{M}$ are close to zero, inference based purely on local curvature is fragile. In that case, complement Hessian-based standard errors with profile-criterion diagnostics: vary one parameter at a time (or along weak singular vectors), re-optimize the remaining parameters, and report objective-function contour sets in addition to pointwise intervals.

(sec-smm_gp_moments)=
## GP Surrogate over the Moment Map
```{prf:remark}

The simplified core notebooks `lecture_15_03_Structural_Estimation_BM.ipynb` and `lecture_15_03b_Structural_Estimation_BM_Joint.ipynb` stop after the direct surrogate-based SMM estimator and its identification diagnostics; they do *not* implement the second-layer Gaussian-process moment surrogate, leave-one-out validation, or Bayesian active learning described below. This section sketches the research-scale extension that a separate companion notebook would add on top of the policy surrogate, and that motivates the GP active-learning workflow used in Chapter {ref}`ch-climate`.
```


The pseudo-state DEQN of the previous sections turned "one re-solve per candidate $\theta$" into "one forward simulation per candidate $\theta$." For high-throughput SMM, that second cost is still nontrivial: a bootstrap with $B = 1{,}000$ resamples needs $1{,}000$ forward simulations on top of the inner optimisation, joint estimation in $p \ge 2$ dimensions multiplies the budget further, and downstream Bayesian or simulation-based-inference workflows want *very* cheap evaluations of $\theta \mapsto m(\theta)$. This section adds a second surrogate layer, a Gaussian process per moment, on top of the policy net, following exactly the supervised-learning logic of {ref}`sec-gp_dp_supervised_view`.

### The Two-Layer Surrogate Architecture

Recall the DEQN policy net $\mathcal{N}_\rho(z, K, \theta)$ from {ref}`sec-smm_method`; given $\theta$, it returns the savings rate as a function of $(z, K)$ and lets us simulate a length-$T$ path $\{C_t(\theta), I_t(\theta), Y_t(\theta)\}_{t=1}^T$ in milliseconds. The empirical SMM workflow then maps that simulated path to a moment vector $m(\theta) \in \R^q$ via a fixed numerical recipe (means, standard deviations, autocorrelations).

We now stack a second surrogate on top of this:

$$
\widehat m_j(\theta) \;\sim\; \mathrm{GP}\bigl(0,\, k_j(\cdot, \cdot)\bigr), \qquad j = 1, \ldots, q,
$$ (eq-moment_gp)

one independent GP per moment, with its own kernel and length-scale hyperparameters learned by maximising marginal likelihood on a small design $\{(\theta^{(i)},\, m(\theta^{(i)}))\}_{i=1}^n$. Once trained, evaluating the SMM objective at any candidate $\theta$ is a single GP forward pass per moment, no simulation required. Bootstrapped CIs and any subsequent Bayesian post-processing then run on the GP, not on the simulator. Figure {numref}`fig-smm_two_layer_surrogate` reads the architecture top-to-bottom. A candidate $\theta$ is fed into the DEQN policy net of {ref}`sec-smm_method`, which is rolled forward for $T$ periods to produce a simulated path and its moment vector $m(\theta)\in\R^q$; a small design $\{(\theta^{(i)},\,m(\theta^{(i)}))\}_{i=1}^n$ of those simulator labels then trains the second layer of $q$ independent moment GPs, after which the SMM criterion $Q(\theta)$ is a closed-form quadratic in the GP posterior means. The right-hand column traces the per-$\theta$ cost cascade from seconds-to-hours down to microseconds.

```{figure} figures/fig-smm_two_layer_surrogate.svg
:name: fig-smm_two_layer_surrogate

The two-layer surrogate architecture for surrogate-based SMM, read top-to-bottom along the chain θ → 𝒩ρ→ simulated path  → m(θ)→ moment GPs  → Q(θ). Layer 1 is the pseudo-state DEQN policy net of §1.2: trained once with θ as an additional input, it replaces the inner Bellman / fixed-point re-solve that direct SMM would require at every candidate parameter, leaving only a T-step forward simulation per θ. Layer 2 is the moment-map GP regression of this section: q independent Gaussian processes are fitted to the simulator’s (θ(i), m(θ(i))) pairs on a small design, after which evaluating the SMM criterion Q(θ) at any new θ requires only a closed-form GP posterior-mean call per moment. The right-hand annotation traces the per-θ cost cascade: the direct re-solve costs seconds-to-hours, Layer 1 brings the cost down to milliseconds (one DEQN-driven simulation), and Layer 2 down to microseconds (one differentiable regression call per moment). This is the same supervised-learning-on-an-expensive-oracle pattern as GP-VFI in §[sec:gp_dp_supervised_view], with the moment vector m(θ) playing the role the Bellman label $TV(\x)$ plays there; the saving compounds because the high-throughput downstream workflows of SMM, bootstrap, profile likelihood, and simulation-based inference, all live in the bottom box.
```

##### Same expensive-oracle structure as VFI.

This is structurally identical to the GP-VFI setup of {ref}`sec-gp_dp`. There, one design point cost one Bellman maximisation; here, one design point costs one $T$-step forward simulation plus a moment computation. In both cases the regressor sees a small but high-quality training set generated by an expensive numerical procedure, and the GP machinery, marginal-likelihood Occam's razor for hyperparameters, leave-one-out diagnostics for surrogate health, and Bayesian active learning for adaptive design, applies verbatim.

### Leave-One-Out Validation of the Moment Surrogate

The Cholesky-trick LOO formula {eq}`eq-gp_loo` of {ref}`sec-gp_loo` delivers a held-out predictive error for each moment GP at zero marginal cost beyond the existing posterior factorisation. A research-scale companion to the core SMM notebooks would track $$\mathrm{LOO\text{-}RMSE}_j \;=\; \sqrt{\frac{1}{n}\sum_{i=1}^{n}\bigl(\widehat m_j^{-i}(\theta^{(i)}) - m_j(\theta^{(i)})\bigr)^2}$$ for every moment $j$ and every design size $n$, and pair it with an independent sanity check that evaluates the GP at a *fresh* interior holdout point $\theta_\mathrm{holdout}$ never seen during training; agreement between the two RMSEs is the criterion for declaring the moment surrogate trustworthy before any bootstrap or SBI workflow is run on top of it.

### Active Learning of the Moment Surrogate

Two acquisition strategies are natural, matched to the dimensionality of the parameter.

##### Single-parameter case.

With a scalar $\theta=\varrho\in[0.50,0.99]$, a coarse uniform pilot grid of $n_0$ points can be enriched by $n_\mathrm{add}$ active points placed sequentially at locations of largest standardised moment-GP posterior uncertainty, $$\theta^{\mathrm{next}} \in \argmax_{\theta \in \mathcal{X}^\mathrm{cand}}\;\Bigl\|\boldsymbol\sigma_m(\theta) \,/\, \bar{\boldsymbol\sigma}_m\Bigr\|_2,$$ subject to a minimum-spacing constraint against existing design points. This is the same pure-exploration acquisition used for VFI {eq}`eq-bal_vfi`, modulo the per-moment normalisation that prevents one large-magnitude moment from dominating the objective.

##### Joint-parameter case.

With $\theta=(\beta,\varrho)$ on a 2D rectangle, pure exploration is wasteful because most of the rectangle sits far from the SMM minimiser. A natural alternative is a BoTorch-style Upper-Confidence-Bound (UCB) acquisition on the transformed score $\widetilde Q(\theta) := -\log_{10}(Q(\theta)+\varepsilon)$, multiplicatively weighted by the moment-GP posterior uncertainty:

$$
a(\theta)
=
\bigl[\,0.25+\widetilde{\mathrm{UCB}}_{\widetilde Q}(\theta)\,\bigr]
\cdot
\Bigl\|\boldsymbol\sigma_m(\theta)\,/\,\widehat{\mathrm{sd}}(m)\Bigr\|_2,
$$ (eq-smm_acquisition)

where $\widetilde{\mathrm{UCB}}_{\widetilde Q}$ is a quantile-scaled and clipped UCB score. The first factor exploits, biasing the design toward $(\beta,\varrho)$ pairs with small SMM criterion, while the second explores, requiring the design to also hit places where the moment GP is uncertain. The additive constant $0.25$ keeps the exploration term active even where the scaled UCB is zero, preventing pathological degeneracy in the acquisition.

##### Three-way comparison.

At a fixed design budget, one can compare pilot grid / naive Latin-hypercube / BoTorch-BAL designs along three axes: (i) leave-one-out error on the moment GPs; (ii) error on the recovered SMM criterion against a fresh reference grid; (iii) accuracy of the recovered estimate $(\hat\beta,\hat\varrho)$. Active designs typically give the most stable local moment surrogate at small budgets.

### The 2D SMM Criterion Surface and Partial Identification

Figure {numref}`fig-smm_2d_criterion` shows the direct SMM criterion on the joint rectangle. Two features are visible.

First, the criterion has a long, shallow ridge along the $\beta$ direction in the just-identified specification: the data are nearly uninformative about $\beta$ once $\varrho$ is fixed, so a wide range of $\beta$-values fits almost equally well. This is partial identification, in textbook form, visualised on the criterion surface. Economically, $\beta$ and $\varrho$ both shift the consumption-smoothing motive in similar directions on long horizons: raising patience and raising persistence each raise the mean savings rate and dampen consumption-growth autocorrelation, so a two-moment specification built from those two moments leaves the $(\beta,\varrho)$ ratio under-determined and produces the ridge.

Second, the ridge collapses to a localized minimum in the over-identified specification. In the synthetic CRN run, the recovered estimate sits very close to $(\beta_{\mathrm{true}},\varrho_{\mathrm{true}})=(0.96,0.90)$. This makes a useful pedagogical point: identification is a property of the moment selection, not of the estimator. The over-identified specification breaks the redundancy by adding growth volatility, which is sensitive to $\varrho$ through the shock-persistence channel but only weakly to $\beta$, and output autocorrelation, which is sensitive to $\varrho$ directly.

```{figure} figures/joint_criterion_contour.pdf
:name: fig-smm_2d_criterion

Direct SMM criterion for the joint Brock–Mirman estimation. The left panel uses the just-identified two-moment specification and displays a shallow ridge along β, signalling that patience is only partially identified by those two moments. The right panel uses the over-identified four-moment specification, which adds volatility and output-persistence information and produces a localized minimum near the synthetic truth. Generated by notebook 03b.
```

In the research-scale extension, the second-layer GP fitted to the joint moment map provides a closed-form, microseconds-per-call substitute for forward simulation: subsequent SMM evaluations, bootstrap replications, and Bayesian post-processing run on the GP rather than on the simulator. The TikZ architecture diagram in Figure {numref}`fig-smm_two_layer_surrogate` already encodes the cost cascade; the rendered GP-objective surface itself is not produced by the core notebooks and is therefore not displayed here.

```{prf:remark}

Notebook `lecture_15_03_Structural_Estimation_BM.ipynb` fits the scalar persistence exercise: a 3-input pseudo-state policy net, common-random-number simulation across a $\varrho$-grid, and an interior SMM estimate with a moment-Jacobian diagnostic. Notebook `lecture_15_03b_Structural_Estimation_BM_Joint.ipynb` performs joint $(\beta,\varrho)$ estimation and visualises the partial-identification ridge of Figure {numref}`fig-smm_2d_criterion` for the shallow-ridge two-moment specification and the over-identified specification. The second-layer GP-moment-map extension above is left as a research-scale companion.
```


(sec-beyond_smm)=
## Beyond SMM: Indirect Inference and Simulation-Based Inference
SMM matches a hand-picked vector of moments. Two close cousins are worth knowing because they often dominate SMM when moment selection is awkward or when one wants the full likelihood.

##### Indirect inference.

{cite:t}`smith1993estimating` and {cite:t}`gourieroux1993indirect` replace the moment vector $m(\theta)$ with the parameters of a tractable *auxiliary model* (e.g. a low-order VAR or a flexible regression) fitted to both the data and to model-simulated data. Estimation matches the auxiliary parameters rather than raw moments; the resulting estimator is asymptotically equivalent to ML when the auxiliary model is sufficiently rich, and the auxiliary parameters often summarize the distribution far more efficiently than a hand-picked moment list. Indirect inference is the natural choice in macro-finance applications where standard moments are weakly identifying but a structural VAR or a near-likelihood auxiliary is available.

##### Simulation-based inference (SBI).

In settings where the simulator is differentiable or fast but the likelihood $p(y \mid \theta)$ is intractable, modern SBI {cite:p}`cranmer2020frontier` learns a neural conditional density estimator $q_\phi(\theta \mid y)$ (or its likelihood/likelihood-ratio counterpart) directly from $(\theta_i, y_i)$ pairs simulated under the prior. The resulting object is an amortised *Bayesian* posterior usable for any future observation $y^\star$ at cost of one forward pass. SBI generalizes Approximate Bayesian Computation, sidesteps moment selection entirely, and naturally pairs with the deep-surrogate machinery of Chapter {ref}`ch-gp`. In the surrogate-then-estimate framing of this chapter, the most direct SBI variant is *neural posterior estimation* (NPE), where the pseudo-state DEQN provides the simulator and the GP moment surrogate of {ref}`sec-smm_gp_moments` is replaced by a learned posterior $q_\phi(\theta\mid y)$; {prf:ref}`ex-ch10-4` contrasts SMM with SBI in algorithmic terms.

*When to choose what.* SMM remains the workhorse when a small number of structural moments are well-identified and economists want a transparent, interpretable objective. Indirect inference dominates when an informative auxiliary model is available. SBI is the natural tool in environments where the model is expensive to simulate but a one-time training run unlocks Bayesian inference at *evaluation* time, precisely the setting in which the rest of this script deploys deep surrogates.

##### Why this matters for the next chapter.

Climate--economy integrated assessment models (Chapter {ref}`ch-climate`) are the prototypical setting where surrogate-based estimation pays off. Credible policy analysis requires evaluating the model over many climate-sensitivity, damage-elasticity, and discount-rate scenarios. Treating the parameter vector as a pseudo-state and training a single deep surrogate, exactly as in the SMM exercise above, turns repeated re-solves into repeated forward passes and is the technical bridge between this chapter and the next.

```{prf:remark}

- SMM matches simulated moments to data moments by minimizing a weighted quadratic objective; it is GMM with simulation {cite:p}`mcfadden1989method,pakes1989simulation`.

- The pseudo-state surrogate trick (treat parameters $\theta$ as additional network inputs) replaces a re-solve at every candidate $\theta$ with a single forward pass; this is what makes SMM with a deep model tractable.

- Stacking a Gaussian-process layer over the moment map ({ref}`sec-smm_gp_moments`) turns SMM into a two-stage surrogate problem: each oracle call is one forward simulation, each subsequent objective evaluation is one GP posterior, the same expensive-oracle / supervised-learning logic that motivates GP-based VFI in {ref}`sec-gp_dp`.

- Common random numbers across $\theta$-candidates are essential in the classroom exercises: they remove simulation noise from the objective and let optimizers see a smooth landscape {cite:p}`glasserman2004monte`.

- Indirect inference and modern simulation-based inference {cite:p}`smith1993estimating,gourieroux1993indirect,cranmer2020frontier` are the natural neighbors of SMM and dominate in their respective regimes.
```


(further-reading)=
## Further Reading
- {cite:t}`mcfadden1989method` {cite}`pakes1989simulation,duffie1993simulated`, the foundational SMM trio.

- {cite:t}`kase2022estimating`, neural-network estimation of nonlinear heterogeneous-agent models; {cite:t}`chen2026Deep`, deep surrogates for finance and option pricing.

- {cite:t}`cranmer2020frontier`, contemporary simulation-based inference.

(exercises)=
## Exercises
Worked solutions and guidance for these exercises appear in Appendix {ref}`app-solutions`.

1.   **[Computational\] Identification.** In notebook `lecture_15_03_Structural_Estimation_BM.ipynb`, choose two candidate moments and compute the finite-difference Jacobian $\partial m/\partial\varrho$ at $\varrho_{\mathrm{true}}=0.90$. Which moment provides stronger local identification?

2.   **[Core\] Optimal weighting.** Show that under standard regularity conditions, $W^\star=\Omega^{-1}$ minimizes the asymptotic variance of $\hat\theta_{\mathrm{SMM}}$, where $\Omega$ is the covariance of the moment discrepancy. Why does identity weighting still appear in the first stage?

3.   **[Computational\] Common random numbers.** In the scalar Brock--Mirman exercise, plot the SMM objective as a function of $\varrho$ with and without common random numbers. Quantify the objective noise across repeated Monte Carlo panels under the same candidate grid.

4.   **[Core\] SMM vs. SBI.** Outline the algorithmic difference between estimating $\theta$ by SMM (one optimization per dataset) and by neural simulation-based inference (one training run plus one posterior evaluation per dataset). In which regime does SBI dominate?

5.   **[Advanced/project\] $J$-statistic and overidentification.** In notebook `lecture_15_03b_Structural_Estimation_BM_Joint.ipynb`, use the over-identified specification with $q=4$ moments and $p=2$ parameters. (i) State the asymptotic distribution of the $J$-statistic under correct specification when $W=\Omega^{-1}$. (ii) Compute $J(\hat\theta)$ on the original synthetic sample and report whether the $\chi^2_2$ test rejects at $\alpha=0.05$. (iii) Repeat across Monte Carlo samples generated at the truth and compare the empirical distribution with $\chi^2_2$. (iv) Introduce a structural break in one model parameter and verify that the $J$ distribution shifts to the right.

6.   **[Advanced/project\] Bootstrap confidence intervals.** Compare three confidence-interval procedures for $\hat\theta_\mathrm{SMM}$: (a) plug-in sandwich standard errors; (b) moving-block or stationary bootstrap of the time-series sample; (c) parametric bootstrap, drawing new samples under the simulated model at $\hat\theta$. Report the confidence intervals and coverage across repeated Monte Carlo replications.

7.   **[Advanced/project\] Maximum likelihood vs. SMM efficiency.** Suppose the productivity process $\log z_t$ is observed. Implement the Gaussian AR(1) MLE for $\varrho$ and compare it with the SMM estimator based on the moments in notebook `lecture_15_03_Structural_Estimation_BM.ipynb`. On Monte Carlo replications at several sample sizes, report bias, variance, and MSE. Explain why MLE is efficient for this observed-shock likelihood, while SMM reaches the GMM efficiency bound only for the chosen moment vector. As an optional extension, repeat the beta-only MLE comparison in the full-depreciation log-utility special case where the policy has a closed form.

[^1]: A resource-based variant in which the savings rate is applied to total resources $R_t = Y_t + (1-\delta)K_t$, allowing disinvestment relative to the depreciated stock, is a straightforward alternative; the SMM moments and notebook outputs in this chapter use the output-based savings rate above.
