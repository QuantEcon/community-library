"""Optional HARK baseline calculation for numerical checks and sensitivity.

Run from projects/HARK/BST: python -m checks.hark_checks
This writes the three result CSVs to the project's results/ directory.
The tutorial notebook is self-contained and does not import this module.

Code names map to the template as follows: m is normalised market
resources, c consumption and a end-of-period assets. psi and theta are
the permanent and full transitory shocks (psi and bold xi in the paper);
rho is relative risk aversion (gamma in the paper). R is the interest
factor, G permanent-income growth, beta the discount factor and wp the
probability of the zero-income event. The paper
is Carroll and Shanker, "Theoretical Foundations of Buffer Stock Saving";
equation and table names refer to its LaTeX source.
"""
import copy
import csv
import datetime
import os
import platform

import numpy as np
from scipy.optimize import brentq

HERE = os.path.dirname(os.path.abspath(__file__))
BST_DIR = os.path.dirname(HERE)
RESULTS = os.path.join(BST_DIR, "results")


def baseline_parameters():
    """The seven calibrated parameters of Tables/Parameters.tex."""
    return {
        "G": 1.03,          # permanent income growth factor
        "R": 1.04,          # interest factor
        "beta": 0.96,       # discount factor
        "rho": 2.0,         # relative risk aversion
        "wp": 0.005,        # probability of zero income
        "sigma_psi": 0.1,   # standard deviation of the log permanent shock
        "sigma_theta": 0.1, # standard deviation of the log transitory shock
    }


def evaluation_grid():
    """The common grid of market-resource values on which c(m) is reported."""
    return np.array(
        [0.25, 0.5, 0.75, 1, 1.25, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10, 15, 20],
        dtype=float,
    )


def hark_parameters(params, a_count=960, shock_count=7, a_max=20.0):
    """HARK's parameter dictionary for the baseline: the paper's notebook
    settings (cell 39) on top of HARK's defaults."""
    from HARK.ConsumptionSaving.ConsIndShockModel import init_idiosyncratic_shocks

    p = copy.deepcopy(init_idiosyncratic_shocks)
    p.update(
        {
            "PermGroFac": [params["G"]],
            "Rfree": [params["R"]],
            "DiscFac": params["beta"],
            "CRRA": params["rho"],
            "UnempPrb": params["wp"],
            "IncUnemp": 0.0,                 # zero income in the unemployment event
            "PermShkStd": [params["sigma_psi"]],
            "TranShkStd": [params["sigma_theta"]],
            "PermShkCount": shock_count,
            "TranShkCount": shock_count,
            "LivPrb": [1.0],                 # no mortality
            "BoroCnstArt": None,             # natural borrowing constraint only
            "cycles": 0,                     # infinite horizon
            "T_cycle": 1,
            "aXtraCount": a_count,           # 20 x HARK's default of 48
            "aXtraMax": a_max,
            "aXtraMin": 0.001,
            "aXtraNestFac": 3,
            "CubicBool": False,              # linear interpolation of c
            "vFuncBool": False,
            "tolerance": 1e-6,
        }
    )
    return p


def solve_baseline(params, a_count=960, shock_count=7, a_max=20.0):
    """Solve the infinite-horizon problem in HARK, check the conditions and
    compute HARK's own stable points; returns the solved agent."""
    from HARK.ConsumptionSaving.ConsIndShockModel import IndShockConsumerType

    agent = IndShockConsumerType(**hark_parameters(params, a_count, shock_count, a_max))
    agent.solve()
    agent.check_conditions(verbose=False)
    agent.calc_stable_points()
    return agent


def shock_atoms(agent):
    """The discretised joint shock distribution HARK solved with:
    permanent atoms, transitory atoms and their probabilities."""
    d = agent.IncShkDstn[0]
    return (
        np.asarray(d.atoms[0], dtype=float),
        np.asarray(d.atoms[1], dtype=float),
        np.asarray(d.pmv, dtype=float),
    )


def exact_lognormal_moments(sigma_psi, rho):
    """E[psi^-1] and E[psi^(1-rho)] for psi = exp(sigma Z - sigma^2/2),
    using E[psi^k] = exp(k (k - 1) sigma^2 / 2)."""
    e_psi_inv = np.exp(sigma_psi**2)
    k = 1.0 - rho
    e_psi_1mrho = np.exp(k * (k - 1.0) * sigma_psi**2 / 2.0)
    return float(e_psi_inv), float(e_psi_1mrho)


def derived_factors(params, e_psi_inv, e_psi_1mrho):
    """The factors of Tables/Calibration.tex, in HARK's key names."""
    G, R, beta, rho, wp = (params[k] for k in ("G", "R", "beta", "rho", "wp"))
    thorn = (R * beta) ** (1.0 / rho)             # absolute patience factor
    psi_under = 1.0 / e_psi_inv                    # growth-compensated permanent shock
    psi_uunder = e_psi_1mrho ** (1.0 / (1.0 - rho))  # utility-compensated permanent shock
    return {
        "FHWFac": G / R,
        "PFVAFac": beta * G ** (1.0 - rho),
        "InvEPermShkInv": psi_under,
        "PermGroFacAdj": G * psi_under,
        "uInvEuPermShk": psi_uunder,
        "PermGroFacAdjU": G * psi_uunder,
        "APFac": thorn,
        "RPFac": thorn / R,
        "GPFacRaw": thorn / G,
        "GPFacMod": thorn / (G * psi_under),
        "VAFac": beta * G ** (1.0 - rho) * e_psi_1mrho,
        "WRPFac": (wp * R * beta) ** (1.0 / rho) / R,
        "wpAPFac": (wp * R * beta) ** (1.0 / rho),   # the table's last row, wp^(1/rho) Thorn
    }


def condition_checks(factors):
    """The paper's conditions at the calibration, each true when the
    corresponding factor is below one."""
    return {
        "FVAC": bool(factors["VAFac"] < 1.0),
        "AIC": bool(factors["APFac"] < 1.0),
        "RIC": bool(factors["RPFac"] < 1.0),
        "WRIC": bool(factors["WRPFac"] < 1.0),
        "GIC": bool(factors["GPFacRaw"] < 1.0),
        "GICMod": bool(factors["GPFacMod"] < 1.0),
        "FHWC": bool(factors["FHWFac"] < 1.0),
    }


def limiting_mpcs(params):
    """kappa_min and kappa_max of equations MPCminDefn and MPCmaxDefn."""
    R, beta, rho, wp = (params[k] for k in ("R", "beta", "rho", "wp"))
    rpf = (R * beta) ** (1.0 / rho) / R
    return max(0.0, 1.0 - rpf), 1.0 - wp ** (1.0 / rho) * rpf


def human_wealth(params):
    """Normalised human wealth including current income, 1 / (1 - G / R)."""
    return 1.0 / (1.0 - params["G"] / params["R"])


def expected_next_m(cfunc, m, params, e_psi_inv):
    """E[m' | m] = (m - c(m)) (R / G) E[psi^-1] + 1, equation mTargImplicit."""
    a = m - float(cfunc(m))
    return a * (params["R"] / params["G"]) * e_psi_inv + 1.0


def target_wealth(cfunc, params, e_psi_inv, bracket=(0.5, 60.0)):
    """The target m_hat solving E[m' | m_hat] = m_hat.  The bracket is
    guaranteed by the bounds of equation cBounds at the calibration."""
    f = lambda m: expected_next_m(cfunc, m, params, e_psi_inv) - m
    return float(brentq(f, bracket[0], bracket[1], xtol=1e-12, rtol=1e-12))


def mpc_central_difference(cfunc, m, step=1e-4):
    """The marginal propensity to consume at m by a central difference."""
    return float((cfunc(m + step) - cfunc(m - step)) / (2.0 * step))


def euler_residuals(cfunc, grid, params, psi, theta, prob):
    """log10 of the consumption-equivalent relative Euler residual:
    abs(c_implied / c - 1), where c_implied inverts the Euler right side."""
    G, R, beta, rho = (params[k] for k in ("G", "R", "beta", "rho"))
    c = np.asarray(cfunc(grid), dtype=float)
    a = grid - c
    m_next = (R / (G * psi))[None, :] * a[:, None] + theta[None, :]
    c_next = np.asarray(cfunc(m_next), dtype=float)
    with np.errstate(divide="ignore"):
        rhs = beta * R * (prob[None, :] * (G * psi)[None, :] ** (-rho) * c_next ** (-rho)).sum(axis=1)
    c_implied = rhs ** (-1.0 / rho)
    return np.log10(np.abs(c_implied / c - 1.0))


def summarize_solution(params, agent):
    """Report a solved HARK agent using its discretised shock distribution.

    First call agent.solve(), agent.check_conditions(verbose=False), and
    agent.calc_stable_points(), as in solve_baseline(). Exact lognormal
    moments are included only as diagnostics for the shock approximation.
    """
    import HARK
    import scipy

    p = dict(params)
    s = agent.solution[0]
    cfunc = s.cFunc
    psi, theta, prob = shock_atoms(agent)
    e_psi_inv_disc = float((prob * psi**-1).sum())
    e_psi_1mrho_disc = float((prob * psi ** (1.0 - p["rho"])).sum())
    e_psi_inv, e_psi_1mrho = exact_lognormal_moments(p["sigma_psi"], p["rho"])
    grid = evaluation_grid()
    c = np.asarray(cfunc(grid), dtype=float)
    m_hat = target_wealth(cfunc, p, e_psi_inv_disc)
    kappa_min, kappa_max = limiting_mpcs(p)
    factors = derived_factors(p, e_psi_inv_disc, e_psi_1mrho_disc)
    return {
        "template_version": "0.1",
        "computed_on": datetime.date.today().isoformat(),
        "hark_version": HARK.__version__,
        "python": platform.python_version(),
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "parameters": p,
        "solver_settings": {
            "shock_atoms_per_dimension": agent.PermShkCount,
            "asset_grid_points": agent.aXtraCount,
            "asset_grid_max": agent.aXtraMax,
            "asset_grid_min": agent.aXtraMin,
            "asset_grid_nesting": agent.aXtraNestFac,
            "interpolation": "cubic" if agent.CubicBool else "linear",
            "convergence_tolerance": agent.tolerance,
            "horizon": "infinite (cycles = 0)",
        },
        "grid": grid.tolist(),
        "c_on_grid": c.tolist(),
        "m_target": m_hat,
        "m_target_with_exact_E_psi_inv": target_wealth(cfunc, p, e_psi_inv),
        "mpc_at_target": mpc_central_difference(cfunc, m_hat, 1e-2),
        "mpc_at_target_definition": "central difference of c at m_target with step 1e-2",
        "mpc_at_target_central_difference_step_1e-4": mpc_central_difference(cfunc, m_hat, 1e-4),
        "mpc_at_target_interpolant_slope": float(cfunc.derivative(m_hat)),
        "kappa_min": kappa_min,
        "kappa_max": kappa_max,
        "derived_factors": factors,
        "conditions": condition_checks(factors),
        "E_psi_inv_exact": e_psi_inv,
        "E_psi_inv_discretised": e_psi_inv_disc,
        "E_psi_1mrho_exact": e_psi_1mrho,
        "E_psi_1mrho_discretised": e_psi_1mrho_disc,
        "hark_cross_checks": {
            "mNrmTrg": float(s.mNrmTrg),
            "mNrmStE": float(s.mNrmStE),
            "MPCmin_solution_object": float(s.MPCmin),
            "MPCmax_solution_object": float(s.MPCmax),
            "MPCmin_limit": float(agent.bilt["MPCmin"]),
            "MPCmax_limit": float(agent.bilt["MPCmax"]),
            "conditions": {k: bool(v) for k, v in agent.conditions.items()},
        },
        "euler_log10_relative_residuals_on_grid": euler_residuals(
            cfunc, grid, p, psi, theta, prob
        ).tolist(),
    }


def compute(a_count=960, shock_count=7, a_max=20.0):
    """Solve the baseline and return a report for the numerical checks."""
    params = baseline_parameters()
    agent = solve_baseline(params, a_count, shock_count, a_max)
    return summarize_solution(params, agent)


def write_results(out, directory=RESULTS):
    """Write cfunc.csv, scalars.csv and conditions.csv in directory."""
    os.makedirs(directory, exist_ok=True)
    with open(os.path.join(directory, "cfunc.csv"), "w", newline="") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(["m", "c"])
        writer.writerows(zip(out["grid"], out["c_on_grid"]))
    with open(os.path.join(directory, "scalars.csv"), "w", newline="") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(["name", "value"])
        for name in ("m_target", "mpc_at_target", "kappa_min", "kappa_max"):
            writer.writerow([name, out[name]])
        writer.writerow(["E_psi_inv", out["E_psi_inv_discretised"]])
        writer.writerow(["E_psi_1mrho", out["E_psi_1mrho_discretised"]])
    with open(os.path.join(directory, "conditions.csv"), "w", newline="") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(["name", "holds"])
        for name in ("FVAC", "AIC", "RIC", "WRIC", "FHWC", "GIC", "GICMod"):
            writer.writerow([name, str(out["conditions"][name]).lower()])


def main():
    out = compute()
    write_results(out)
    print(f"HARK {out['hark_version']}, Python {out['python']}, numpy {out['numpy']}, scipy {out['scipy']}")
    print("m       c(m)")
    for m, c in zip(out["grid"], out["c_on_grid"]):
        print(f"{m:6.2f}  {c:.6f}")
    print(f"target m_hat = {out['m_target']:.6f}  (with exact E[psi^-1]: {out['m_target_with_exact_E_psi_inv']:.6f})")
    print(f"MPC at target: {out['mpc_at_target']:.6f} (central difference, step 1e-2); "
          f"step 1e-4 {out['mpc_at_target_central_difference_step_1e-4']:.6f}; interpolant slope {out['mpc_at_target_interpolant_slope']:.6f}")
    print(f"kappa_min = {out['kappa_min']:.6f}, kappa_max = {out['kappa_max']:.6f}")
    print("conditions:", out["conditions"])
    print("HARK cross-checks:", {k: v for k, v in out["hark_cross_checks"].items() if k != "conditions"})
    print("log10 Euler residuals:", " ".join(f"{x:.1f}" for x in out["euler_log10_relative_residuals_on_grid"]))


if __name__ == "__main__":
    main()
