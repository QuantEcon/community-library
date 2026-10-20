# Buffer stock saving

Read the [model description](https://quantecon.github.io/community-library/models/buffer-stock/)
(its [source](model-description.md)) or its [PDF](model-description.pdf) for the theory, calibration and numerical solution. Keep the stated
model and calibration fixed, and choose the solution method, prose and
runnable format that suit your toolkit. The
[HARK notebook](../../solutions/buffer-stock/001-hark-egm/tutorial.ipynb) is one example.

## What to submit

Add a runnable solution in a directory of its own under `solutions/buffer-stock/`,
named `<NNN>-<toolkit>-<method>` with the next free number, as the
[contributing guide](../../CONTRIBUTING.md#submitting-a-solution) explains. A notebook,
a MyST document with code, or another format is welcome. Include the code
and instructions needed to reproduce the results.

1. Link to the shared model description and use its calibration. Explain any part of the model that your toolkit cannot represent.
2. Report the results listed at the end of the model description: consumption at the sixteen common values of $m$, the target $\hat m$ and the MPC at the target with step $h=0.01$. Any format will do; the HARK files below are one.
3. Document the software versions, numerical settings, and installation and run commands where readers can find them.
4. Add a `metadata.yml` recording the authors, the version of this description you follow and your AI disclosure; see [the metadata file](#the-metadata-file).
5. Run the solution from a fresh session and open a pull request adding its directory.

## The HARK example

The solution at `solutions/buffer-stock/001-hark-egm/` uses the following
files. Apart from `metadata.yml`, their names and arrangement are an example;
each solution chooses its own files.

| File | Content |
| --- | --- |
| `tutorial.ipynb` | Runnable calculations, explanations and figures. |
| `metadata.yml` | Authors, the description version followed, AI disclosure, software versions and numerical settings. |
| `results/cfunc.csv` | Consumption at a common set of resource values. |
| `results/scalars.csv` | Target resources, MPCs and permanent-shock moments. |
| `results/conditions.csv` | The seven model conditions. |

HARK also includes an environment file and optional numerical checks.
The CSV layouts and tolerances below are **optional draft comparison
conventions**. Every solution reports the numbers in item 2 above;
submitters can present them in these files or in another way. Every
solution also includes a `metadata.yml`.

## Optional comparison files

These tables express resources and consumption relative to permanent income
and use the solver's shock approximation for expectations.

### Consumption

The HARK file `results/cfunc.csv` has columns `m,c`, with one row for each value

$$
m\in\{0.25,0.5,0.75,1,1.25,1.5,2,2.5,3,4,5,6,8,10,15,20\}.
$$

Plot consumption over $m\in[0,20]$ and check that it is increasing and
concave. The limiting MPCs below give the bounds
$\underline\kappa m\leq\mathrm{c}(m)\leq\overline\kappa m$.
Use the limiting value $\mathrm{c}(0)=0$ at the origin.

### Target, MPCs and shock moments

The HARK file `results/scalars.csv` has columns `name,value`. Define the absolute
patience factor $\text{Þ}=(\mathsf{R}\beta)^{1/\gamma}$, where $\gamma$ is
relative risk aversion.

| Row name | Quantity |
| --- | --- |
| `m_target` | Target $\hat m$ solving the model's conditional expected resource-growth equation. |
| `mpc_at_target` | $[\mathrm{c}(\hat m+h)-\mathrm{c}(\hat m-h)]/(2h)$ with $h=0.01$. |
| `kappa_min` | $\underline\kappa=\max\{0,1-\text{Þ}/\mathsf{R}\}$. |
| `kappa_max` | $\overline\kappa=1-\wp^{1/\gamma}\text{Þ}/\mathsf{R}$. |
| `E_psi_inv` | $\mathbb{E}[\psi^{-1}]$ under the solver's shock approximation. |
| `E_psi_1mgamma` | $\mathbb{E}[\psi^{1-\gamma}]$ under the solver's shock approximation. |

Check that expected resource growth is positive at $\hat m-0.5$ and negative
at $\hat m+0.5$. The target differs from a balanced-growth pseudo-target and
from the mean of the stationary distribution.

### Conditions

The HARK file `results/conditions.csv` has columns `name,holds`, using `true`
or `false`. Its notebook also displays the corresponding factors.

| Row name | Condition | Factor below one when the condition holds |
| --- | --- | --- |
| `FVAC` | Finite value of autarky | $\beta\mathcal{G}^{1-\gamma}\mathbb{E}[\psi^{1-\gamma}]$ |
| `AIC` | Absolute impatience | $\text{Þ}$ |
| `RIC` | Return impatience | $\text{Þ}/\mathsf{R}$ |
| `WRIC` | Weak return impatience | $\wp^{1/\gamma}\text{Þ}/\mathsf{R}$ |
| `FHWC` | Finite human wealth | $\mathcal{G}/\mathsf{R}$ |
| `GIC` | Growth impatience | $\text{Þ}/\mathcal{G}$ |
| `GICMod` | Strong growth impatience | $(\text{Þ}/\mathcal{G})\mathbb{E}[\psi^{-1}]$ |

## The metadata file

Every solution includes a `metadata.yml`. The required fields are the
toolkit, the method, the authors, the maintainers, the description version
followed, and the AI-assistance level with what AI was used for. `project` is
added for a solution submitted on behalf of a toolkit's project, and the
verification fields once a person has verified the solution. The
[contributing guide](../../CONTRIBUTING.md#submitting-a-solution)
explains each one, and the pull request's checks report any that are missing.
The remaining fields below follow the HARK file and are optional. Replace the
descriptions in angle brackets with your details.

```yaml
# Required
toolkit: "<toolkit, or the language if none>"
method: "<short method name, such as EGM>"
authors:
  - name: "<author>"
maintainers: ["<GitHub username>"]
model_description_version: "0.1"
ai_level: <level, 0 to 4>
ai_used_for: "<uses, such as drafting, code; when the level is above 0>"
# When submitted on behalf of a toolkit's project
project: "<project name>"
# Once a person has verified the solution
verified_by: "<name>"
verified_date: "<YYYY-MM-DD>"
verified_version: "0.1"
# Optional
toolkit_version: "<version>"
model: "buffer-stock"
date: "<YYYY-MM-DD>"
model_description: "https://github.com/QuantEcon/community-library/tree/buffer-stock/v0.1/models/buffer-stock"
software:
  "<language>": "<version>"
  "<package>": "<version>"
method_details: "<solution method and convergence criterion>"
discretisation: "<shock approximation, number of points, and zero-income treatment>"
grid: "<grid variables, bounds, number of points, and spacing>"
target_mpc: "<how the MPC at the target is computed>"
```

Describe settings in words if your method has no grid or does not discretise
the shocks. Retain the source-paper citations and CC-BY attribution, and
state the licence for your code.

## Optional comparison tolerances

The [HARK results](../../solutions/buffer-stock/001-hark-egm/results/) provide one comparison.
Its [numerical checks](../../solutions/buffer-stock/001-hark-egm/checks/sensitivity.md) show
how grids, shock approximations and interpolation affect the results.

The following optional draft thresholds can guide discussion of numerical
differences between implementations:

| Quantity | Suggested threshold for discussion |
| --- | --- |
| Consumption at any common resource value | Greater than 0.02 |
| Target resources | Greater than 0.02 |
| MPC at the target | Greater than 0.01 |
| Either limiting MPC | Greater than $10^{-6}$ |
| Any condition result | Disagreement |

The two shock moments help explain differences and have no separate
tolerance. Use each implementation's own shock approximation for the target.
These conventions remain optional and provisional. The library does not rank
toolkits or compare run times.

## Maintaining the model description

Edit `model-description.md` and build its PDF from `models/buffer-stock/`:

```sh
myst build --pdf
```

The build requires LaTeX and uses `../../templates/plain_latex_wide/`. The
library website builds the description's web page from the same file. Each
change raises the version in the front matter's `options` and adds an entry
to [CHANGELOG.md](CHANGELOG.md); the
[contributing guide](../../CONTRIBUTING.md#versioning-model-descriptions)
gives the steps. Each solution is maintained by its own maintainers in its
own directory.
