# Buffer stock saving with HARK

Open [tutorial.ipynb](tutorial.ipynb) for the runnable example. The notebook
contains the HARK settings and calculations; it imports no local Python modules.
The theory and calibration are in the [model description](../../../models/buffer-stock/model-description.md).
The calculation follows the [paper's HARK notebook](https://github.com/econ-ark/BufferStockTheory/blob/master/Code/Python/BufferStockTheory-Problems-and-Solutions-Source.ipynb).

Install the packages, then open the notebook in Jupyter or your editor using
the same Python environment:

```sh
python -m pip install -r requirements.txt
```

Restart the kernel and run all cells. The notebook solves the model, plots
consumption and expected resource growth, and checks the solution. Its final
cell saves optional comparison tables and software settings in the working
directory. Run it from this directory to refresh the files below.

| File or directory | Purpose |
| --- | --- |
| `tutorial.ipynb` | HARK implementation, plots and computed results. |
| `requirements.txt` | Notebook packages and optional test tools. |
| `metadata.yml`, `results/` | Saved settings and optional comparison tables. |
| `checks/` | Optional numerical tests and a sensitivity study. |

The calculation uses HARK 0.17.1, seven positive values per income shock
plus zero income, and 960 asset grid points between 0.001 and 20.
Consumption is linearly interpolated and iteration uses tolerance 1e-6.
The notebook computes shock moments from the discretised distribution and
uses a central difference with step 0.01 for the MPC at the target.

HARK's `mNrmTrg` is the individual target; `mNrmStE` is the balanced-growth
pseudo-target. The solution object's `MPCmin` is a finite-iteration slope,
so the reported limiting MPCs use the paper's closed forms.

## Optional numerical checks

The notebook can run without the `checks/` directory. To run the existing
tests or repeat the [sensitivity study](checks/sensitivity.md):

```sh
python -m pytest -q checks
python -m checks.sensitivity
```

`checks/hark_checks.py` contains the calculations used by those tests.
`python -m checks.hark_checks` also writes the three comparison tables.
`checks/expected.json` preserves an earlier verified HARK calculation for
regression tests. The independent EGM code in `checks/` supports the optional numerical
comparisons.

Other projects can choose their own prose, solution method and runnable
format while retaining the shared model and calibration. See the
[contribution guide](../../../models/buffer-stock/README.md).
