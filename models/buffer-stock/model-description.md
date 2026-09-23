---
title: Buffer stock saving
subtitle: Model description, version 0.1 (draft)
date: '2026-09-14'
license: CC-BY-4.0
exports:
- format: pdf
  template: ../../templates/plain_latex_wide
  output: model-description.pdf
---

## 1. Model theory

We consider a consumer who saves in one risk-free asset and receives labour income with permanent and transitory shocks, following Carroll's buffer-stock models (1992, 1997).[^carroll] We use the model and notation of Carroll and Shanker, [*Theoretical Foundations of Buffer Stock Saving*](https://econ-ark.github.io/BufferStockTheory/BufferStockTheory.pdf), version of 5 December 2025. The stationary solution is the limit of finite-horizon solutions as the horizon lengthens; there is no mortality and no bequest motive. Implementations in the QuantEcon Community Library keep this model and calibration fixed.

[^carroll]: Carroll, C. D. (1992), [“The Buffer-Stock Theory of Saving: Some Macroeconomic Evidence”](https://www.brookings.edu/articles/the-buffer-stock-theory-of-saving-some-macroeconomic-evidence/), *Brookings Papers on Economic Activity*, 1992(2), 61–156; Carroll, C. D. (1997), [“Buffer-Stock Saving and the Life Cycle/Permanent Income Hypothesis”](https://academic.oup.com/qje/article-abstract/112/1/1/1870884), *Quarterly Journal of Economics*, 112(1), 1–55.

Bold Latin letters denote levels and upright letters denote functions. The consumer has CRRA utility $\mathrm{u}(c)=c^{1-\gamma}/(1-\gamma)$, with relative risk aversion $\gamma>1$ and discount factor $\beta>0$. Permanent income $\boldsymbol{p}_t$ grows by the realised growth factor $\tilde{\mathcal{G}}_{t+1}=\mathcal{G}\psi_{t+1}$, where $\mathcal{G}>0$ is the deterministic growth factor and $\psi_{t+1}$ the permanent shock. Labour income is $\boldsymbol{y}_t=\boldsymbol{p}_t\pmb{\xi}_t$, with transitory shock

$$
\pmb{\xi} =
\begin{cases}
0 & \text{with probability } \wp,\\
\theta/(1-\wp) & \text{with probability } 1-\wp,
\end{cases}
\qquad 0<\wp<1,
$$

where $\theta$ is the positive part of the transitory shock and bold $\pmb{\xi}$, following the paper, is the full shock including the zero-income event. The positive shocks $\psi$ and $\theta$ have mean one and are independent of each other and over time, as is the zero-income event, so $\mathbb{E}[\pmb{\xi}]=1$.

Within a period the shocks are realised; the bank balance $\boldsymbol{b}_t=\mathsf{R}\boldsymbol{a}_{t-1}$, with gross interest factor $\mathsf{R}>0$, and labour income form market resources $\boldsymbol{m}_t=\boldsymbol{b}_t+\boldsymbol{y}_t$ (hereafter resources); the consumer then chooses consumption $\boldsymbol{c}_t$ and carries end-of-period assets $\boldsymbol{a}_t=\boldsymbol{m}_t-\boldsymbol{c}_t$ into the next period. Divide resources, consumption and end-of-period assets by permanent income: $m_t=\boldsymbol{m}_t/\boldsymbol{p}_t$, $c_t=\boldsymbol{c}_t/\boldsymbol{p}_t$ and $a_t=\boldsymbol{a}_t/\boldsymbol{p}_t$. The normalised budget equations are

$$
a_t=m_t-c_t,\qquad
b_{t+1}=\tilde{\mathscr{R}}_{t+1}a_t,\qquad
m_{t+1}=b_{t+1}+\pmb{\xi}_{t+1},\qquad
\tilde{\mathscr{R}}_{t+1}=\frac{\mathsf{R}}{\tilde{\mathcal{G}}_{t+1}}.
$$

Here $b_{t+1}$ is the bank balance relative to next period's permanent income and $\tilde{\mathscr{R}}_{t+1}$ the growth-normalised return, the interest factor divided by the realised growth factor.

Because income may be zero in any period, debt could leave resources negative and no positive consumption feasible; zero assets is therefore the natural debt limit, and admissible plans satisfy $0<\boldsymbol{c}_t\leq\boldsymbol{m}_t$ after every shock history. At the terminal date $T$, $\mathrm{c}_T(m)=m$ and $\mathrm{v}_T(m)=\mathrm{u}(m)$. Before $T$, saving nothing risks having nothing to consume after a zero-income draw, and utility tends to minus infinity at zero consumption, so saving nothing is suboptimal and $0<\mathrm{c}_t(m)<m$.

Let $\mathrm{v}$ and $\mathrm{c}$ denote the stationary normalised value and consumption functions, with value in levels $\boldsymbol{\mathrm{v}}(\boldsymbol{m},\boldsymbol{p})=\boldsymbol{p}^{1-\gamma}\mathrm{v}(\boldsymbol{m}/\boldsymbol{p})$. The normalised Bellman equation is

$$
\mathrm{v}(m)=\max_{0<c<m}\left\{
\mathrm{u}(c)+\beta\,\mathbb{E}\!\left[
(\tilde{\mathcal{G}}')^{1-\gamma}
\mathrm{v}\!\left(\tilde{\mathscr{R}}'(m-c)+\pmb{\xi}'\right)
\right]\right\},\qquad m>0.
$$

Primes denote next-period quantities; expectations are over both income shocks. The factor $(\tilde{\mathcal{G}}')^{1-\gamma}$ converts next period's value, which scales with $(\boldsymbol{p}')^{1-\gamma}$, into units of this period's permanent income. For the reasons just given, the objective tends to minus infinity at both endpoints of the choice set, so the maximum is attained in the interior. The first-order and envelope conditions (the paper establishes that $\mathrm{v}$ is differentiable) give the normalised Euler equation

$$
\mathrm{c}(m)^{-\gamma}
=\beta\mathsf{R}\,\mathbb{E}\!\left[
(\tilde{\mathcal{G}}')^{-\gamma}\mathrm{c}(m')^{-\gamma}
\right],\qquad
m'=\tilde{\mathscr{R}}'\bigl(m-\mathrm{c}(m)\bigr)+\pmb{\xi}'.
$$

Precautionary saving becomes more attractive as resources fall, while impatience encourages consumers to spend down high resources. Under the calibration of section 2 these incentives produce a target level of resources $\hat m$, below which expected resources rise and above which they fall. By the budget equations and $\mathbb{E}[\pmb{\xi}]=1$, expected next-period resources are

$$
\mathbb{E}[m_{t+1}\mid m_t]=\bigl(m_t-\mathrm{c}(m_t)\bigr)
\frac{\mathsf{R}}{\mathcal{G}}\,\mathbb{E}[\psi^{-1}]+1,
$$

and the target is the fixed point $\mathbb{E}[m_{t+1}\mid m_t=\hat m]=\hat m$; it is not the mean of the stationary distribution of $m_t$. The paper's pseudo-target, at which the level of resources is expected to grow at the rate of permanent income, solves the same equation with $\mathbb{E}[\psi^{-1}]$ replaced by one and lies below $\hat m$; it is not reported here.

## 2. Calibration

We use the paper's annual calibration. Income growth and risk draw on the Panel Study of Income Dynamics (Carroll, 1992); preferences and the interest rate are conventional.

| Parameter | Symbol | Value |
| --- | --- | --- |
| Income growth factor | $\mathcal{G}$ | 1.03 |
| Gross interest factor | $\mathsf{R}$ | 1.04 |
| Discount factor | $\beta$ | 0.96 |
| Relative risk aversion | $\gamma$ | 2 |
| Probability of zero income | $\wp$ | 0.005 |
| Standard deviation of $\log\psi$ | $\sigma_\psi$ | 0.1 |
| Standard deviation of $\log\theta$ | $\sigma_\theta$ | 0.1 |

The positive shocks are log-normal with means normalised to one, $\log\psi\sim N(-\sigma_\psi^2/2,\sigma_\psi^2)$ and $\log\theta\sim N(-\sigma_\theta^2/2,\sigma_\theta^2)$.

## 3. Numerical solution

Every implementation retains the calibration but approximates the two shock distributions with finitely many values of its own choosing that preserve their means and the zero-income probability. The paper's existence results require positive shocks bounded above and away from zero, which finite approximations with strictly positive $\psi$ and $\theta$ satisfy and the log-normal laws do not. Under this assumption, weak return impatience and finite value of autarky give a finite value function and a positive limiting consumption function,

$$
\wp^{1/\gamma}\frac{\text{\textbf{Þ}}}{\mathsf{R}}<1,\qquad
\beta\mathcal{G}^{1-\gamma}\mathbb{E}[\psi^{1-\gamma}]<1,
\qquad \text{\textbf{Þ}}=(\mathsf{R}\beta)^{1/\gamma},
$$

where $\text{\textbf{Þ}}$ is the absolute patience factor, the growth factor of consumption under perfect foresight. Adding strong growth impatience, $(\text{\textbf{Þ}}/\mathcal{G})\mathbb{E}[\psi^{-1}]<1$, gives a unique target $\hat m$. The table lists these and the paper's four other conditions, each holding when its factor is below one, with values at the calibration from the continuous laws; all seven also hold under a seven-point equiprobable approximation, and each implementation evaluates them and the target equation with its own shock approximation.

| Condition | Factor | Value at the calibration |
| --- | --- | --- |
| Finite value of autarky | $\beta\mathcal{G}^{1-\gamma}\mathbb{E}[\psi^{1-\gamma}]$ | 0.941 |
| Absolute impatience | $\text{\textbf{Þ}}$ | 0.999 |
| Return impatience | $\text{\textbf{Þ}}/\mathsf{R}$ | 0.961 |
| Weak return impatience | $\wp^{1/\gamma}\text{\textbf{Þ}}/\mathsf{R}$ | 0.068 |
| Finite human wealth | $\mathcal{G}/\mathsf{R}$ | 0.990 |
| Growth impatience | $\text{\textbf{Þ}}/\mathcal{G}$ | 0.970 |
| Strong growth impatience | $(\text{\textbf{Þ}}/\mathcal{G})\mathbb{E}[\psi^{-1}]$ | 0.980 |

The consumption function is increasing and concave. Under weak return impatience its marginal propensity to consume (MPC) tends to $\overline\kappa$ as resources tend to zero and to $\underline\kappa$ as resources tend to infinity, where

$$
\underline\kappa=\max\!\left\{0,1-\frac{\text{\textbf{Þ}}}{\mathsf{R}}\right\},\qquad
\overline\kappa=1-\wp^{1/\gamma}\frac{\text{\textbf{Þ}}}{\mathsf{R}},\qquad
\underline\kappa m\leq\mathrm{c}(m)\leq\overline\kappa m.
$$

The lower limit is the perfect-foresight MPC; the upper limit falls short of one because a consumer with few resources still saves against the zero-income event.

The solution method is free; value function iteration is one option. The [paper's own notebook](https://github.com/econ-ark/BufferStockTheory/blob/master/Code/Python/BufferStockTheory-Problems-and-Solutions-Source.ipynb) uses the endogenous grid method, linear interpolation and 960 asset grid points, iterating from the terminal consumption rule to convergence. Several figures in that notebook use other parameter values; implementations keep the calibration of section 2.

The stopping tolerance alone does not measure accuracy. Useful checks are a finer shock approximation, the extrapolated consumption function above the top of the asset grid, Euler residuals, monotonicity, concavity and the bounds on $\mathrm{c}(m)$; the paper's notebook re-solves under greater permanent-income risk with a wider asset range, a denser grid and a tighter tolerance. Because a piecewise-linear consumption function has a kink at every grid point, every implementation reports the MPC at the target as the central difference $[\mathrm{c}(\hat m+h)-\mathrm{c}(\hat m-h)]/(2h)$ with $h=0.01$.
