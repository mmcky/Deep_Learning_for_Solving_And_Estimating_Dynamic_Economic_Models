---
title: "Itô Calculus, Brownian Motion, and Ergodicity"
label: app-stoch
---

This appendix collects the stochastic-calculus background needed for Chapters {ref}`ch-pinn`--{ref}`ch-ct_theory`. For the longer, example-driven exposition see {ref}`sec-stoch_calc`; for a full textbook treatment, see {cite:t}`shreve2004stochasticii`.

## Brownian motion

A standard Brownian motion $B_t$ has independent Gaussian increments $B_t - B_s \sim \mathcal{N}(0, t-s)$, continuous paths almost surely, and quadratic variation $\langle B\rangle_t = t$. Equivalently, the simple-random-walk scaling limit $X_{t+\Delta t} = X_t + \sqrt{\Delta t}\,\varepsilon_t$ converges in distribution to $B_t$ as $\Delta t \to 0$ (Donsker).

## Itô's lemma

For $X_t$ following $dX_t = \mu\,dt + \sigma\,dB_t$ and $f \in C^2$: $$df(X_t) = \bigl[f'(X_t)\mu + \tfrac{1}{2}f''(X_t)\sigma^2\bigr]dt + f'(X_t)\sigma\,dB_t.$$ The differential algebra is $dt\cdot dt = dt\cdot dB_t = 0$, $dB_t \cdot dB_t = dt$. (Throughout the script, the stochastic integral is interpreted in the Itô sense; the Stratonovich convention would replace the drift correction $\tfrac{1}{2}f''(X_t)\sigma^2$ by $0$.)

## Ergodicity in one paragraph

A Markov process with stationary distribution $\pi$ is *ergodic* if the time-average along any sample path converges almost surely to the spatial average against $\pi$: $\tfrac{1}{T}\int_0^T \varphi(X_t)\,dt \xrightarrow{T\to\infty} \int \varphi\,d\pi$ for every bounded measurable $\varphi$. In economic models with bounded state spaces and aperiodic dynamics, ergodicity is what justifies replacing population integrals by simulation-time averages in DEQN training (Chapter {ref}`ch-deqn`, {ref}`sec-deqn_algo`).
