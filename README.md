# Community Library of Baseline Economic Models

The Community Library is an open-source library of baseline models in computational economics, implemented and documented across the toolkits that can solve them.
For each model the library documents the model statement and the calibration, so that implementations in different toolkits can be compared side by side.
Each implementation is authored and maintained by the project that built the toolkit and is open to review by the community.

The library is hosted by QuantEcon and published at **<https://quantecon.github.io/community-library/>**. It is run in collaboration with the [SCE Working Group 1 on Language and Formal Semantics](https://github.com/econ-ark/sce-wg-1).
This repository holds the community website, the shared model descriptions and the implementations submitted by participating projects.

## Start with a model

Read the [buffer stock model description](models/buffer-stock/model-description.md)
or its [PDF](models/buffer-stock/model-description.pdf), which covers model theory,
calibration and numerical solution. The
[HARK notebook](projects/HARK/BST/tutorial.ipynb) provides a runnable example
with short explanations; its [instructions](projects/HARK/BST/README.md)
give the installation and run commands.

Keep the model and calibration fixed, and choose your own prose, solution
method and runnable format. The [submission guide](models/buffer-stock/README.md#what-to-submit)
explains where to put an implementation and how to document its use. The
guide's CSV formats, metadata example and draft comparison tolerances are optional.

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
| `projects/<toolkit>/<model>/` | A runnable implementation in the project's chosen format, with supporting code and results. |
| `docs/` | The library website. |
| `templates/` | The page layout used to produce model PDFs. |

For example, `projects/HARK/BST/` contains the HARK buffer stock implementation.
Questions about a shared model description belong in
the [working group issue tracker](https://github.com/econ-ark/sce-wg-1/issues).

## Website maintenance

The website consists of static HTML, CSS and JavaScript in `docs/`. Its
appearance follows the [QuantEcon book theme](https://github.com/QuantEcon/quantecon-book-theme).
Edit `docs/index.html` for text, `docs/site.css` for appearance and
`docs/site.js` for the contents navigation.

The [publishing workflow](.github/workflows/publish.yml) checks local file
links, links to sections and the contents navigation on every push and pull
request. It publishes `docs/` to GitHub Pages from `main`; pull requests
provide a downloadable site preview. These checks cover the website;
notebook execution is not yet automated.

Publishing requires **Settings → Pages → Build and deployment → Source:
GitHub Actions**. The [buffer stock guide](models/buffer-stock/README.md)
gives the commands for generating the PDF from the model description.

## Licensing

Text is CC-BY; code is released under an OSI-approved licence. Contributions remain
authored and maintained by their projects. The library publishes the work
with attribution and does not rank the toolkits.
