# Community Library of Baseline Economic Models

The Community Library is an open-source library of baseline models in computational economics, implemented and documented across the toolkits that can solve them.
For each model the library documents the model statement and the calibration, so that implementations in different toolkits can be compared side by side.
Each solution is authored and maintained by its submitters, whether a toolkit's project or individual contributors, and is open to review by the community.

The library is hosted by QuantEcon and published at **<https://quantecon.github.io/community-library/>**. It is run in collaboration with the [SCE Working Group 1 on Language and Semantics](https://github.com/econ-ark/sce-wg-1).
This repository holds the community website, the shared model descriptions and the solutions submitted by toolkit projects and individual contributors.

## Start with a model

Read the [buffer stock model description](https://quantecon.github.io/community-library/models/buffer-stock/)
or its [PDF](models/buffer-stock/model-description.pdf), which covers model theory,
calibration, numerical solution and the results each implementation
reports. The
[HARK notebook](solutions/buffer-stock/001-hark-egm/tutorial.ipynb) provides a runnable example
with short explanations; its [instructions](solutions/buffer-stock/001-hark-egm/README.md)
give the installation and run commands.

Keep the model and calibration fixed, and choose your own prose, solution
method and runnable format. The [submission guide](models/buffer-stock/README.md#what-to-submit)
explains where to put a solution, which results to report and how to
document its use. Every solution includes a short `metadata.yml`
recording its authors, the description version it follows and its AI
disclosure; the [contributing guide](CONTRIBUTING.md) explains these, and the
guide's CSV formats and draft comparison tolerances are optional.

The working group has proposed five baseline models. Projects choose one or
more that their toolkit can solve and also contribute a tutorial on a model
of their own choosing.

| Baseline model | Model class | Description |
| --- | --- | --- |
| [Buffer stock saving](models/buffer-stock/README.md) | Partial-equilibrium consumption–saving under income risk | Draft available |
| Aiyagari · Krusell–Smith | Incomplete-markets heterogeneous agents | In preparation |
| A two-asset HANK model | Heterogeneous-agent New Keynesian | In preparation |
| A small New Keynesian DSGE model | Representative-agent DSGE | In preparation |
| A baseline agent-based macro model | Macro from interacting heterogeneous agents | In preparation |

## Where files belong

| Directory | Purpose |
| --- | --- |
| `models/<model>/` | The shared model description, its PDF and the submission guide. |
| `solutions/<model>/<NNN>-<toolkit>-<method>/` | A runnable solution in its submitters' chosen format, with its `metadata.yml`, supporting code and results. |
| `docs/` | The library website. |
| `templates/` | The page layout used to produce model PDFs. |
| `schemas/` | The schema each solution's `metadata.yml` follows. |
| `tools/` | Scripts that build the model description pages and check versions and disclosure records. |

A model has the same directory name in both places, and its solutions are
numbered in submission order: the buffer-stock description is in
`models/buffer-stock/` and the HARK solution in
`solutions/buffer-stock/001-hark-egm/`.
Questions about a shared model description belong in
the [working group issue tracker](https://github.com/econ-ark/sce-wg-1/issues).

## Website maintenance

The website consists of static HTML, CSS and JavaScript in `docs/`. Its
appearance follows the [QuantEcon book theme](https://github.com/QuantEcon/quantecon-book-theme).
Edit `docs/index.html` for text, `docs/site.css` for appearance and
`docs/site.js` for the contents navigation. `docs/contributing/index.html` is
the contributing guide for people; `CONTRIBUTING.md` holds the full rules, for
contributors and coding agents, so a change to a rule there updates the page
too. `docs/sce-wg1-2026-10-01.html`
is the Project B talk to SCE Working Group 1 (1 October 2026), a
self-contained reveal.js deck.

Each model description also gets a page at `docs/models/<model>/`, built from
its `model-description.md` by `tools/build_pages.py` with the PDF alongside.
The pages are built when the site is published, not committed. To preview
them:

```sh
python -m pip install -r tools/requirements.txt
python tools/build_pages.py
```

The [publishing workflow](.github/workflows/publish.yml) builds those pages
and runs `tools/check_metadata.py`, which checks that the descriptions, each
solution's `metadata.yml` and the library table agree on versions and
disclosure. It then checks local file links, links to sections and the
contents navigation on every push and pull request. It publishes `docs/` to
GitHub Pages from `main`; pull requests provide a downloadable site preview.
Notebook execution is not yet automated.

Publishing requires **Settings → Pages → Build and deployment → Source:
GitHub Actions**. The [buffer stock guide](models/buffer-stock/README.md)
gives the commands for generating the PDF from the model description.

## Licensing

Text is CC-BY; code carries an OSI-approved licence. Contributions remain authored and maintained by their submitters — the library curates and publishes; it does not own anyone's work or rank the toolkits.
