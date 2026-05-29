---
title: "Matrix Calculus and Automatic Differentiation"
label: app-ad
---

This appendix collects the few matrix-calculus identities used in the main text and gives a one-page summary of how automatic differentiation realizes them computationally.

## Matrix calculus identities

For $\bm A \in \R^{m\times n}$, $\bm x \in \R^n$, $\bm y = \bm A\bm x$: $$\frac{\partial \bm y}{\partial \bm x} = \bm A,\qquad
   \frac{\partial (\bm y^\top \bm y)}{\partial \bm x} = 2\bm A^\top \bm A\bm x.$$ For a quadratic form $f(\bm x) = \bm x^\top \bm Q \bm x$ with symmetric $\bm Q$, $\nabla f(\bm x) = 2\bm Q\bm x$ and $\nabla^2 f = 2\bm Q$. For a deep network $\bm{\hat y} = g_L(\bm W_L\, g_{L-1}(\cdots g_1(\bm W_1 \bm x + \bm b_1)\cdots))$, the chain rule gives $$\frac{\partial \bm{\hat y}}{\partial \bm W_l}
   \;=\;
   \underbrace{(\bm \delta^{(l)})}_{\substack{\text{backprop} \\ \text{delta}}}
   \,\bigl(\bm a^{(l-1)}\bigr)^{\!\top}$$ with $\bm \delta^{(l)} = \bigl(\bm W^{(l+1)\top}\bm \delta^{(l+1)}\bigr) \odot g'(\bm z^{(l)})$ ({ref}`sec-training`).

## Reverse-mode AD in one paragraph

Reverse-mode AD evaluates the function once forward, caches every intermediate value, and then traverses the computation graph backwards, accumulating the local Jacobian--vector products in linear time in the number of operations. For a scalar loss, one reverse sweep returns the gradient with respect to all parameters at a small constant multiple of the forward cost. The computation still scales with the size of the graph, but it does not require one separate derivative pass per parameter; this is what makes million-parameter networks trainable. See {cite:t}`baydin2018automatic` and {cite:t}`margossian2019review` for complete treatments.

## Higher-order AD

PINN losses involve second derivatives ($V_{SS}$ in Black--Scholes, Laplacians in Poisson equations, and second-order terms in diffusion HJBs). Higher-order derivatives are obtained by composing reverse-mode AD with itself, `torch.autograd.grad` of `grad` in PyTorch, `jax.grad` of `jax.grad` in JAX. Activation regularity matters: the network must be at least $C^k$ for the strong $k$-th-order residual to be well-defined.
