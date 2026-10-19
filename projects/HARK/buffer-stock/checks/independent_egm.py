"""An endogenous grid method solver written from the template's equations
and independent of HARK; the oracle for the HARK consumption
function.  The policy is a piecewise-linear function through the points
(m_i, c_i) with the anchor (0, 0) at the natural borrowing constraint."""
import numpy as np
from scipy.stats import norm


def equiprobable_lognormal(sigma, n):
    """n equiprobable atoms of a mean-one log-normal with log standard
    deviation sigma, each atom the conditional mean of its segment."""
    if sigma == 0.0:
        return np.ones(1), np.ones(1)
    cuts = norm.ppf(np.linspace(0.0, 1.0, n + 1))
    # E[exp(sigma Z - sigma^2/2); a < Z < b] = Phi(b - sigma) - Phi(a - sigma)
    mass = norm.cdf(cuts[1:] - sigma) - norm.cdf(cuts[:-1] - sigma)
    return mass * n, np.full(n, 1.0 / n)


def income_atoms(params, n_psi, n_theta):
    """The joint discretisation of (psi, theta): psi equiprobable log-normal;
    theta zero with probability wp and otherwise Theta / (1 - wp) with Theta
    equiprobable log-normal (the paper's equation TranShkDef)."""
    psi_a, psi_p = equiprobable_lognormal(params["sigma_psi"], n_psi)
    th_a, th_p = equiprobable_lognormal(params["sigma_theta"], n_theta)
    wp = params["wp"]
    theta_vals = np.concatenate([[0.0], th_a / (1.0 - wp)])
    theta_prob = np.concatenate([[wp], th_p * (1.0 - wp)])
    psi = np.repeat(psi_a, theta_vals.size)
    theta = np.tile(theta_vals, psi_a.size)
    prob = np.repeat(psi_p, theta_vals.size) * np.tile(theta_prob, psi_a.size)
    return psi, theta, prob


def _policy(m, m_pol, c_pol):
    """Piecewise-linear consumption with linear extrapolation above the
    last knot at the last segment's slope."""
    c = np.interp(m, m_pol, c_pol)
    above = m > m_pol[-1]
    if np.any(above):
        slope = (c_pol[-1] - c_pol[-2]) / (m_pol[-1] - m_pol[-2])
        c = np.where(above, c_pol[-1] + slope * (m - m_pol[-1]), c)
    return c


def solve_egm(params, psi, theta, prob, a_max=50.0, a_count=3000,
              tol=1e-10, max_iter=5000, growth_factor=None):
    """Time iteration on the Euler equation with an exogenous grid on a.
    Returns the endogenous grid m and consumption c on it.  Passing
    growth_factor overrides G in the transition and discounting, which the
    tests use to confirm that the oracle reacts to a timing error."""
    G = params["G"] if growth_factor is None else growth_factor
    R, beta, rho = params["R"], params["beta"], params["rho"]
    a_grid = np.concatenate(
        [[0.0], np.exp(np.linspace(np.log(1e-4), np.log(a_max), a_count - 1))]
    )
    r_norm = R / (G * psi)                      # growth-normalised return per atom
    weight = prob * (G * psi) ** (-rho)         # discount weight per atom
    m_pol, c_pol = a_grid.copy(), a_grid.copy()  # start from c(m) = m
    for it in range(max_iter):
        m_next = r_norm[None, :] * a_grid[:, None] + theta[None, :]
        c_next = _policy(m_next, m_pol, c_pol)
        with np.errstate(divide="ignore"):
            rhs = beta * R * (weight[None, :] * c_next ** (-rho)).sum(axis=1)
        c_new = rhs ** (-1.0 / rho)             # zero where rhs is infinite (a = 0)
        m_new = a_grid + c_new
        gap = np.max(np.abs(c_new - c_pol))
        m_pol, c_pol = m_new, c_new
        if gap < tol:
            break
    else:
        raise RuntimeError(f"EGM did not converge in {max_iter} iterations; last gap {gap:.3e}")
    return m_pol, c_pol
