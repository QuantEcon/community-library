# A Community Library of Baseline Models

A community library of the field's baseline models, implemented and documented across the toolkits that can solve them — same model, multiple toolkits, side by side. Each implementation is authored and maintained by the project that built the toolkit.

The library is hosted and managed by QuantEcon and published at **<https://quantecon.github.io/community-library/>**. It began as Project B of [SCE Working Group 1 on Language and Formal Semantics](https://github.com/mmcky/sce-wg1) and now runs independently of the group, which continues to publish the baseline set and templates. This repository hosts the community website and the notebooks submitted by participating projects.

## How it works

The working group provides a set of baseline models. Each participating project chooses as many as its toolkit can solve — several or just one — and completes the model's template notebook in its own toolkit: the code, plus commentary where its method differs. The completed notebook is its tutorial. Baseline templates (a PDF and a notebook per model, with the model statement and explanatory text already written) are distributed from the working group website.

Four models seed the set:

| Baseline model | Model class |
| --- | --- |
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
| `docs/assets/` | images |

`.github/workflows/publish.yml` checks the site on every push and pull request — local references resolve, in-page anchors resolve, and the contents rail is still wired to its sections — then deploys `docs/` to GitHub Pages from `main`. Pull requests get the same checks plus the built site as a downloadable artifact, so a change can be reviewed rendered.

Publishing requires **Settings → Pages → Build and deployment → Source: GitHub Actions**.

## Status

The repository structure, contribution guidelines, and the first baseline templates are in preparation. Until then, discussion happens in the [working group issue tracker](https://github.com/mmcky/sce-wg1/issues).

## Licensing

Text is CC-BY; code carries an OSI-approved licence. Contributions remain authored and maintained by their projects — the library curates and publishes; it does not own anyone's work or rank the toolkits.
