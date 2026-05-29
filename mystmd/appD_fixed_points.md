---
title: "Fixed Points, Contraction Mappings, and the Bellman Operator"
label: app-fixed_points
---

The classical numerical-economics toolkit rests on Banach's contraction-mapping theorem; this appendix recalls the statement and one short proof sketch for completeness. A reference is {cite:t}`stokeylucas1989`.

## Banach's theorem

Let $(X, d)$ be a complete metric space and let $T: X \to X$ be a contraction with modulus $\beta < 1$, i.e. $d(T x, T y) \le \beta\, d(x, y)$ for all $x, y$. Then $T$ has a unique fixed point $x^\star$, and for every starting point $x_0$ the iterates $x_{n+1} = Tx_n$ satisfy $d(x_n, x^\star) \le \beta^n\, d(x_0, x^\star)$.

## The Bellman operator is a contraction

For a discount factor $\beta \in (0,1)$ and bounded utility, the Bellman operator $T V(x) = \max_a \{u(x,a) + \beta\,\E V(x') \mid x_t = x, a_t = a\}$ is a contraction with modulus $\beta$ on the space of bounded continuous functions equipped with the supremum norm. Hence value-function iteration converges geometrically. The same logic underpins *policy iteration*, the dual algorithm that converges in finite steps for finite-state problems.

## Why this matters for DEQNs

DEQNs do *not* iterate a Bellman operator. Instead, they apply gradient descent to a residual loss that vanishes at the equilibrium policy. The contraction property therefore disappears as a tool for proving convergence, and theoretical guarantees come from neural-network optimization theory rather than fixed-point analysis: convergence arguments rest on universal approximation plus loss-landscape and NTK-style analyses of stochastic gradient descent on overparameterized networks, surveyed alongside the DEQN-specific open questions in Chapter {ref}`ch-outlook`.
