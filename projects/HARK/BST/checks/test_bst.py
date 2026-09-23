"""Tests for the buffer stock HARK implementation.

Oracles, with provenance:
  * the seven calibrated parameters: Tables/Parameters.tex of the paper;
  * the derived factors: Tables/Calibration.tex of the paper, closed forms
    in the parameters with exact log-normal moments;
  * the limiting MPCs: equations MPCminDefn and MPCmaxDefn of the paper;
  * the bounds on c(m) and its shape: equation cBounds and Proposition
    cfuncprop of the paper, with the perfect-foresight upper bound;
  * the target: equation mTargImplicit of the paper;
  * the consumption function: an endogenous grid method written from the
    template's equations (independent_egm.py), on a finer grid.
"""
import csv
import json
import os
import platform
import shutil
import subprocess
import sys

import numpy as np
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
BST_DIR = os.path.dirname(HERE)
# Allow the checks to run from either the HARK implementation or repository directory.
sys.path.insert(0, BST_DIR)

from checks import independent_egm as egm
from checks import hark_checks as rm


@pytest.fixture(scope="session")
def params():
    return rm.baseline_parameters()


@pytest.fixture(scope="session")
def agent(params):
    return rm.solve_baseline(params)


@pytest.fixture(scope="session")
def cfunc(agent):
    return agent.solution[0].cFunc


@pytest.fixture(scope="session")
def atoms(agent):
    return rm.shock_atoms(agent)


PAPER_PARAMETERS = {  # Tables/Parameters.tex
    "G": 1.03, "R": 1.04, "beta": 0.96, "rho": 2.0, "wp": 0.005,
    "sigma_psi": 0.1, "sigma_theta": 0.1,
}

PAPER_FACTORS = {  # Tables/Calibration.tex, "Approximate Calculated Value"
    "FHWFac": 0.990, "PFVAFac": 0.932, "InvEPermShkInv": 0.990,
    "PermGroFacAdj": 1.020, "APFac": 0.999, "RPFac": 0.961,
    "GPFacRaw": 0.970, "GPFacMod": 0.980, "VAFac": 0.941,
    "wpAPFac": 0.071,  # the table prints wp^(1/rho) Thorn, not the WRIC factor wp^(1/rho) Thorn / R
}


def test_baseline_parameters_match_paper(params):
    for key, value in PAPER_PARAMETERS.items():
        assert params[key] == value


def test_evaluation_grid_is_the_proposed_one():
    grid = rm.evaluation_grid()
    assert list(grid) == [0.25, 0.5, 0.75, 1, 1.25, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10, 15, 20]


def test_shock_discretisation_is_mean_one_with_zero_income_event(atoms, params):
    psi, theta, prob = atoms
    # Means are exact identities of the equiprobable construction; 1e-12 is
    # floating-point accumulation over 56 joint shock outcomes.
    assert abs(prob.sum() - 1.0) < 1e-12
    assert abs((prob * psi).sum() - 1.0) < 1e-12
    assert abs((prob * theta).sum() - 1.0) < 1e-12
    zero = theta == 0.0
    assert abs(prob[zero].sum() - params["wp"]) < 1e-12
    # Code theta is the paper's full transitory shock, bold xi. Conditional
    # on positive income, its mean is 1 / (1 - wp).
    cond_mean = (prob[~zero] * theta[~zero]).sum() / prob[~zero].sum()
    assert abs(cond_mean - 1.0 / (1.0 - params["wp"])) < 1e-12


def test_derived_factors_match_paper_table(params):
    e_psi_inv, e_psi_1mrho = rm.exact_lognormal_moments(params["sigma_psi"], params["rho"])
    factors = rm.derived_factors(params, e_psi_inv, e_psi_1mrho)
    for key, value in PAPER_FACTORS.items():
        # The table prints three decimals; agreement to half a unit in the
        # third decimal is the strongest claim the table supports.
        assert abs(factors[key] - value) < 5e-4, (key, factors[key], value)


def test_conditions_hold_at_baseline_and_agree_with_hark(params, agent, atoms):
    out = rm.summarize_solution(params, agent)
    psi, _, prob = atoms
    e_psi_inv = float((prob / psi).sum())
    e_psi_1mrho = float((prob * psi ** (1 - params["rho"])).sum())
    assert out["E_psi_inv_discretised"] == pytest.approx(e_psi_inv, abs=1e-14)
    assert out["E_psi_1mrho_discretised"] == pytest.approx(e_psi_1mrho, abs=1e-14)
    # The finite shock law differs from the continuous lognormal law. Reports
    # must use the former even though both give the same Boolean conditions.
    assert abs(out["E_psi_inv_exact"] - e_psi_inv) > 1e-4
    assert out["derived_factors"] == pytest.approx(
        rm.derived_factors(params, e_psi_inv, e_psi_1mrho), rel=1e-13, abs=1e-14,
    )
    checks = out["conditions"]
    for name in ["FVAC", "AIC", "RIC", "WRIC", "GIC", "GICMod", "FHWC"]:
        assert checks[name] is True, name
    hark = agent.conditions
    assert hark["GICRaw"] == checks["GIC"]
    assert hark["GICMod"] == checks["GICMod"]
    assert hark["RIC"] == checks["RIC"]
    assert hark["WRIC"] == checks["WRIC"]
    assert hark["FHWC"] == checks["FHWC"]
    assert hark["AIC"] == checks["AIC"]


def test_limiting_mpcs_closed_form_vs_hark(params, agent):
    kappa_min, kappa_max = rm.limiting_mpcs(params)
    # HARK evaluates the same closed forms in check_conditions; 1e-10 is
    # floating-point rounding.
    assert abs(agent.bilt["MPCmin"] - kappa_min) < 1e-10
    assert abs(agent.bilt["MPCmax"] - kappa_max) < 1e-10
    # The solution object's MPCmin is the value after finitely many backward
    # steps: the recursion of Lemma MPC contracts at rate Thorn/R = 0.961,
    # and HARK stops when the policy on its grid moves by less than 1e-6,
    # long before the asymptotic slope has converged.  Its gap is recorded
    # in sensitivity.md; it is bounded here, not claimed to vanish.
    soln = agent.solution[0]
    assert abs(soln.MPCmax - kappa_max) < 1e-8
    assert 0.0 < soln.MPCmin - kappa_min < 2e-3


def test_consumption_function_theory_bounds(params, cfunc):
    grid = rm.evaluation_grid()
    c = cfunc(grid)
    kappa_min, kappa_max = rm.limiting_mpcs(params)
    h = rm.human_wealth(params)
    assert np.all(c >= kappa_min * grid)               # eq. cBounds, lower
    assert np.all(c <= kappa_max * grid)               # eq. cBounds, upper
    assert np.all(c <= kappa_min * (grid + h - 1.0))   # perfect-foresight bound
    assert np.all(np.diff(c) > 0)                      # increasing
    slopes = np.diff(c) / np.diff(grid)
    assert np.all(np.diff(slopes) <= 0)                # concave: chord slopes fall


def test_consumption_function_vs_independent_egm(params, cfunc, atoms):
    psi, theta, prob = atoms
    grid = rm.evaluation_grid()
    m_egm, c_egm = egm.solve_egm(params, psi, theta, prob)
    c_ref = np.interp(grid, m_egm, c_egm)
    gap = np.abs(cfunc(grid) - c_ref)
    # Both solvers use the same 56 joint shock outcomes, so the gap is interpolation
    # and grid error only.  Interior points (m <= 15) agree to 6e-6
    # (sensitivity.md, section 1); 2e-5 is three times that.  At m = 20, the
    # top of HARK's asset grid, HARK's value is 1.3e-4 above the converged
    # solution because its extrapolation beyond the grid uses the
    # unconverged MPCmin of the solution object (section 2: the gap falls
    # to 1.4e-5 when the grid top is 40); 2e-4 bounds it.
    interior = grid <= 15.0
    assert np.max(gap[interior]) < 2e-5, gap
    assert np.max(gap[~interior]) < 2e-4, gap


def test_independent_egm_is_sensitive_to_growth_normalisation(params, cfunc, atoms):
    psi, theta, prob = atoms
    grid = rm.evaluation_grid()
    m_bad, c_bad = egm.solve_egm(params, psi, theta, prob, growth_factor=1.0)
    gap = np.max(np.abs(cfunc(grid) - np.interp(grid, m_bad, c_bad)))
    # Dropping the growth factor from the transition must move c(m) by far
    # more than the agreement tolerance, or the oracle is not independent.
    assert gap > 1e-2, gap


def test_target_wealth_solves_implicit_equation(params, agent, cfunc, atoms):
    psi, theta, prob = atoms
    e_psi_inv = float((prob * psi ** -1).sum())
    m_hat = rm.target_wealth(cfunc, params, e_psi_inv)
    residual = rm.expected_next_m(cfunc, m_hat, params, e_psi_inv) - m_hat
    assert abs(residual) < 1e-10          # brentq with xtol 1e-12
    # HARK solves the same equation with the same c and shocks by Newton's
    # method; 1e-6 covers both root-finders' stopping rules.
    assert abs(m_hat - agent.solution[0].mNrmTrg) < 1e-6
    # Theorem target: E[m'] > m below the target and < m above it.
    assert rm.expected_next_m(cfunc, m_hat - 0.5, params, e_psi_inv) > m_hat - 0.5
    assert rm.expected_next_m(cfunc, m_hat + 0.5, params, e_psi_inv) < m_hat + 0.5


def test_mpc_at_target_between_limits(params, cfunc, atoms):
    psi, theta, prob = atoms
    e_psi_inv = float((prob * psi ** -1).sum())
    m_hat = rm.target_wealth(cfunc, params, e_psi_inv)
    kappa_min, kappa_max = rm.limiting_mpcs(params)
    kappa_hat = rm.mpc_central_difference(cfunc, m_hat)
    assert kappa_min < kappa_hat < kappa_max
    # The interpolant is piecewise linear, so its derivative is the slope of
    # the segment containing m_hat; a central difference with step 1e-4 can
    # straddle one knot, and the segment slopes change by less than 1e-3
    # near the target on a 960-point grid (see sensitivity.md).
    assert abs(kappa_hat - float(cfunc.derivative(m_hat))) < 1e-3


def test_euler_residuals_small_on_grid(params, cfunc, atoms):
    psi, theta, prob = atoms
    grid = rm.evaluation_grid()
    log10_resid = rm.euler_residuals(cfunc, grid, params, psi, theta, prob)
    # Linear interpolation of c on 960 points gives residuals of order 1e-4
    # or smaller away from the constraint; -3 is one order looser.
    assert np.all(log10_resid < -3.0), log10_resid


def test_recorded_hark_values_reproduce(params, agent, cfunc, atoms):
    """Keep the historical numerical record unchanged as a test fixture.

    Its derived factors used continuous lognormal moments; the current
    CSVs use the discrete moments, checked separately above.
    """
    path = os.path.join(HERE, "expected.json")
    with open(path) as f:
        stored = json.load(f)
    psi, theta, prob = atoms
    e_psi_inv = float((prob * psi ** -1).sum())
    grid = rm.evaluation_grid()
    fresh_c = cfunc(grid)
    assert np.max(np.abs(np.array(stored["c_on_grid"]) - fresh_c)) < 1e-10
    assert abs(stored["m_target"] - rm.target_wealth(cfunc, params, e_psi_inv)) < 1e-10
    m_hat = stored["m_target"]
    assert abs(stored["mpc_at_target"] - rm.mpc_central_difference(cfunc, m_hat, 1e-2)) < 1e-12
    assert stored["hark_version"] == "0.17.1"


def test_hark_checks_module_writes_three_csvs_in_project(tmp_path):
    """The optional calculation runs as a module and writes project results."""
    project_dir = tmp_path / "BST"
    checks_dir = project_dir / "checks"
    checks_dir.mkdir(parents=True)
    shutil.copyfile(os.path.join(HERE, "hark_checks.py"), checks_dir / "hark_checks.py")
    run = subprocess.run(
        [sys.executable, "-m", "checks.hark_checks"], cwd=project_dir,
        capture_output=True, text=True,
    )
    assert run.returncode == 0, run.stderr
    assert not (tmp_path / "results").exists()
    assert not (checks_dir / "results").exists()
    assert f"Python {platform.python_version()}" in run.stdout
    result_dir = project_dir / "results"
    assert {path.name for path in result_dir.iterdir()} == {
        "cfunc.csv", "scalars.csv", "conditions.csv",
    }
    with open(os.path.join(HERE, "expected.json")) as f:
        stored = json.load(f)
    with open(result_dir / "cfunc.csv") as f:
        reader = csv.DictReader(f)
        assert reader.fieldnames == ["m", "c"]
        rows = list(reader)
    assert [float(row["m"]) for row in rows] == stored["grid"]
    np.testing.assert_allclose(
        [float(row["c"]) for row in rows], stored["c_on_grid"], rtol=0, atol=1e-10,
    )
    with open(result_dir / "scalars.csv") as f:
        reader = csv.DictReader(f)
        assert reader.fieldnames == ["name", "value"]
        rows = list(reader)
    assert [row["name"] for row in rows] == [
        "m_target", "mpc_at_target", "kappa_min", "kappa_max", "E_psi_inv", "E_psi_1mrho",
    ]
    scalars = {row["name"]: float(row["value"]) for row in rows}
    for name in ("m_target", "mpc_at_target", "kappa_min", "kappa_max"):
        # Preserve the established calibration and step-0.01 target MPC;
        # 1e-10 allows differences from numerical library versions.
        assert abs(scalars[name] - stored[name]) < 1e-10
    assert abs(scalars["E_psi_inv"] - stored["E_psi_inv_discretised"]) < 1e-12
    # At baseline rho = 2, the two required discrete moments coincide.
    assert abs(scalars["E_psi_1mrho"] - scalars["E_psi_inv"]) < 1e-12
    with open(result_dir / "conditions.csv") as f:
        reader = csv.DictReader(f)
        assert reader.fieldnames == ["name", "holds"]
        rows = list(reader)
    assert [row["name"] for row in rows] == [
        "FVAC", "AIC", "RIC", "WRIC", "FHWC", "GIC", "GICMod",
    ]
    assert {row["name"]: row["holds"] for row in rows} == {
        name: str(value).lower() for name, value in stored["conditions"].items()
    }
