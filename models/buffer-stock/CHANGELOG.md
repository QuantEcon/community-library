# Buffer stock saving: changelog

Each version of the [model description](model-description.md) has an entry
here, newest first. The [contributing guide](../../CONTRIBUTING.md#versioning-model-descriptions)
sets the rules: a new major version means implementations must re-run, and a
new minor version leaves their results unchanged. While the description is a
draft (0.x), every change raises the minor version, and its entry says whether
implementations need to re-run.

## 0.1 — 2026-10-20

The first draft: the model and notation of Carroll and Shanker, *Theoretical
Foundations of Buffer Stock Saving* (version of 5 December 2025), the paper's
annual calibration, the conditions the solution relies on, and the results
every implementation reports: consumption at sixteen common values of $m$, the
target $\hat m$ and the MPC at the target with step $h=0.01$.

Implementations: the first version; nothing to re-run.
