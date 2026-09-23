"""Sensitivity of the HARK baseline to the solver's own settings and to
the shock discretisation.  Writes checks/sensitivity.md and checks/sensitivity.json.

Run from projects/HARK/BST: python -m checks.sensitivity
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
BST_DIR = os.path.dirname(HERE)
# Allow the checks to run from either the HARK implementation or repository directory.
sys.path.insert(0, BST_DIR)

from checks import independent_egm as egm
from checks import hark_checks as rm


def hark_run(p, **kw):
    agent = rm.solve_baseline(p, **kw)
    s = agent.solution[0]
    psi, theta, prob = rm.shock_atoms(agent)
    e_psi_inv = float((prob * psi**-1).sum())
    grid = rm.evaluation_grid()
    m_hat = rm.target_wealth(s.cFunc, p, e_psi_inv)
    return {
        "c": np.asarray(s.cFunc(grid), dtype=float),
        "m_hat": m_hat,
        "kappa_1e-4": rm.mpc_central_difference(s.cFunc, m_hat, 1e-4),
        "kappa_1e-3": rm.mpc_central_difference(s.cFunc, m_hat, 1e-3),
        "kappa_1e-2": rm.mpc_central_difference(s.cFunc, m_hat, 1e-2),
        "kappa_slope": float(s.cFunc.derivative(m_hat)),
        "MPCmin_solution_object": float(s.MPCmin),
        "atoms": (psi, theta, prob),
        "cfunc": s.cFunc,
    }


def egm_run(p, psi, theta, prob, a_count, a_max=50.0):
    m_e, c_e = egm.solve_egm(p, psi, theta, prob, a_max=a_max, a_count=a_count)
    grid = rm.evaluation_grid()
    cfunc = lambda m: np.interp(m, m_e, c_e)
    e_psi_inv = float((prob * psi**-1).sum())
    m_hat = rm.target_wealth(cfunc, p, e_psi_inv)
    return {"c": cfunc(grid), "m_hat": m_hat,
            "kappa_1e-4": rm.mpc_central_difference(cfunc, m_hat, 1e-4),
            "kappa_1e-2": rm.mpc_central_difference(cfunc, m_hat, 1e-2)}


def main():
    p = rm.baseline_parameters()
    grid = rm.evaluation_grid()
    base = hark_run(p)
    psi7, theta7, prob7 = base["atoms"]
    egm_fine = egm_run(p, psi7, theta7, prob7, a_count=12000)
    lines = ["# Sensitivity of the HARK baseline", "",
             "HARK baseline: seven positive values per shock plus zero transitory income (56 joint outcomes), 960 asset points, asset grid top 20. "
             "The tables compare consumption on the common grid, target wealth "
             "and the MPC at the target. Target differences retain their sign.", ""]
    out = {"grid": grid.tolist(), "baseline": {"c": base["c"].tolist(), "m_hat": base["m_hat"],
           "kappa_1e-4": base["kappa_1e-4"], "kappa_slope": base["kappa_slope"]}}

    # 1. HARK against the independent solver on the same atoms
    lines += ["## 1. HARK baseline against the independent EGM solver (same 56 joint shock outcomes, 12,000 knots to a = 50)", "",
              "| m | HARK | EGM | difference |", "| --- | --- | --- | --- |"]
    for m, a, b in zip(grid, base["c"], egm_fine["c"]):
        lines.append(f"| {m:g} | {a:.7f} | {b:.7f} | {a-b:+.1e} |")
    lines += ["", f"Target: HARK {base['m_hat']:.6f}, EGM {egm_fine['m_hat']:.6f}, difference {base['m_hat']-egm_fine['m_hat']:+.1e}.", ""]
    out["egm_fine"] = {"c": egm_fine["c"].tolist(), "m_hat": egm_fine["m_hat"]}

    # 2. HARK's own settings
    lines += ["## 2. HARK's own grid settings (56 joint shock outcomes throughout)", "",
              "| Setting | Maximum absolute consumption difference from baseline | Maximum absolute consumption difference from EGM | Target difference from baseline | MPC at target, step 1e-4 | MPC at target, interpolant slope | MPCmin of solution object |",
              "| --- | --- | --- | --- | --- | --- | --- |"]
    variants = [("baseline", {}), ("480 asset points", {"a_count": 480}), ("1920 asset points", {"a_count": 1920}),
                ("grid top 40", {"a_max": 40.0}), ("grid top 80", {"a_max": 80.0}),
                ("1920 points, top 40", {"a_count": 1920, "a_max": 40.0})]
    out["hark_settings"] = {}
    for name, kw in variants:
        r = base if not kw else hark_run(p, **kw)
        dc = float(np.max(np.abs(r["c"] - base["c"])))
        de = float(np.max(np.abs(r["c"] - egm_fine["c"])))
        lines.append(f"| {name} | {dc:.1e} | {de:.1e} | {r['m_hat']-base['m_hat']:+.1e} | {r['kappa_1e-4']:.5f} | {r['kappa_slope']:.5f} | {r['MPCmin_solution_object']:.5f} |")
        out["hark_settings"][name] = {"max_dc_vs_baseline": dc, "max_dc_vs_egm": de, "m_hat": r["m_hat"],
                                      "kappa_1e-4": r["kappa_1e-4"], "kappa_1e-3": r["kappa_1e-3"],
                                      "kappa_1e-2": r["kappa_1e-2"], "kappa_slope": r["kappa_slope"]}
    lines.append("")

    # 3. Shock discretisation (the element the template leaves free)
    lines += ["## 3. Shock discretisation, HARK (960 points, top 20)", "",
              "| positive values per shock | maximum absolute consumption difference from baseline | target difference from baseline | target |", "| --- | --- | --- | --- |"]
    out["hark_shocks"] = {}
    for n in [3, 5, 7, 11, 21]:
        r = base if n == 7 else hark_run(p, shock_count=n)
        dc = float(np.max(np.abs(r["c"] - base["c"])))
        lines.append(f"| {n} | {dc:.1e} | {r['m_hat']-base['m_hat']:+.1e} | {r['m_hat']:.6f} |")
        out["hark_shocks"][n] = {"max_dc_vs_7": dc, "m_hat": r["m_hat"]}
    lines += ["", "## 4. Shock discretisation, independent EGM (3,000 knots to a = 50, its own equiprobable atoms)", "",
              "| positive values per shock | maximum absolute consumption difference from baseline | target difference from baseline | target |", "| --- | --- | --- | --- |"]
    out["egm_shocks"] = {}
    ref = None
    for n in [3, 5, 7, 11, 21]:
        psi, theta, prob = egm.income_atoms(p, n, n)
        r = egm_run(p, psi, theta, prob, a_count=3000)
        if n == 7:
            ref = r
        out["egm_shocks"][n] = {"c": r["c"].tolist(), "m_hat": r["m_hat"]}
    for n in [3, 5, 7, 11, 21]:
        c = np.array(out["egm_shocks"][n]["c"]); mh = out["egm_shocks"][n]["m_hat"]
        lines.append(f"| {n} | {np.max(np.abs(c - ref['c'])):.1e} | {mh-ref['m_hat']:+.1e} | {mh:.6f} |")
    lines.append("")

    # 5. The MPC at the target under different finite-difference steps
    lines += ["## 5. The MPC at the target: finite-difference step", "",
              "| solution | step 1e-4 | step 1e-3 | step 1e-2 | interpolant slope |", "| --- | --- | --- | --- | --- |"]
    for name in ["baseline", "1920 asset points", "1920 points, top 40"]:
        r = out["hark_settings"][name]
        lines.append(f"| HARK, {name} | {r['kappa_1e-4']:.5f} | {r['kappa_1e-3']:.5f} | {r['kappa_1e-2']:.5f} | {r['kappa_slope']:.5f} |")
    lines.append(f"| EGM, 12,000 knots | {egm_fine['kappa_1e-4']:.5f} | — | {egm_fine['kappa_1e-2']:.5f} | — |")
    lines.append("")
    with open(os.path.join(HERE, "sensitivity.md"), "w") as f:
        f.write("\n".join(lines))
    with open(os.path.join(HERE, "sensitivity.json"), "w") as f:
        json.dump(out, f, indent=2)
    print("\n".join(lines))


if __name__ == "__main__":
    main()
