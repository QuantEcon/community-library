# Community Library of Baseline Economic Models

The Community Library is an open-source library of baseline models in computational economics, implemented and documented across the toolkits that can solve them.
For each model the library documents the model statement and the calibration, so that implementations in different toolkits can be compared side by side.
Each implementation is authored and maintained by the project that built the toolkit and is open to review by the community.

The library is hosted by QuantEcon and published at **<https://quantecon.github.io/community-library/>**. It is run in collaboration with the [SCE Working Group 1 on Language and Semantics](https://github.com/econ-ark/sce-wg-1).
This repository holds the community website and the notebooks submitted by participating projects.

## How it works

The working group provides a set of baseline models. Each participating project chooses as many as its toolkit can solve — several or just one — and writes its solution in its own toolkit and format: the code, plus commentary where its method differs. That notebook is its tutorial. Each model has a shared model description, published as a page and a PDF, that pins the model, its calibration and what each solution reports, and leaves the method to the project.

Buffer-stock saving comes first; four more are proposed:

| Baseline model | Model class |
| --- | --- |
| Buffer-stock saving | Consumption–saving under income risk |
| Aiyagari · Krusell–Smith | Incomplete-markets heterogeneous agents |
| A two-asset HANK model | Heterogeneous-agent New Keynesian |
| A small New Keynesian DSGE model | Representative-agent DSGE |
| A baseline agent-based macro model | Macro from interacting heterogeneous agents |

## The website

`docs/` holds the site — hand-written static HTML with no build step. Colours, typography and UI patterns come from the [QuantEcon book theme](https://github.com/QuantEcon/quantecon-book-theme), so the library sits alongside the lecture sites rather than beside them.

| Path | What it is |
| --- | --- |
| `docs/index.html` | the page |
| `docs/site.css` | design tokens and components |
| `docs/site.js` | contents-rail scrollspy |
| `docs/sce-wg1-2026-10-01.html` | the Project B talk to SCE Working Group 1 (1 October 2026), a self-contained reveal.js deck |
| `docs/assets/` | images |

`.github/workflows/publish.yml` checks the site on every push and pull request — local references resolve, in-page anchors resolve, and the contents rail is still wired to its sections — then deploys `docs/` to GitHub Pages from `main`. Pull requests get the same checks plus the built site as a downloadable artifact, so a change can be reviewed rendered.

Publishing requires **Settings → Pages → Build and deployment → Source: GitHub Actions**.

## Status

The repository structure, contribution guidelines, and the first model descriptions are in preparation; the buffer-stock saving description and a HARK solution are in review in #5. Until then, discussion happens in the [working group issue tracker](https://github.com/econ-ark/sce-wg-1/issues).

## Licensing

Text is CC-BY; code carries an OSI-approved licence. Contributions remain authored and maintained by their projects — the library curates and publishes; it does not own anyone's work or rank the toolkits.
