# Contributing to the Community Library

The library takes pull requests from anyone, whether or not they are a member
of the working group. This guide covers what every contribution records: which
version of a model description it follows, how much AI was involved in
producing it, and whether a person has verified it. Each model's submission
guide, such as [the one for buffer stock](models/buffer-stock/README.md),
covers what to implement and report. How submissions are reviewed is being
settled in [#6](https://github.com/QuantEcon/community-library/issues/6).

## Submitting an implementation

Put the implementation in `projects/<toolkit>/<model>/`, using the model's
directory name from `models/`, and include a `metadata.yml` beside it. These
fields are required; any others are welcome.

| Field | Content |
| --- | --- |
| `model_description_version` | The version of the model description the implementation follows, such as `"0.1"`. |
| `authors` | A list of the implementation's authors, each with a `name`. |
| `ai_level` | How much AI was involved, from 0 to 4; see [AI disclosure and verification](#ai-disclosure-and-verification). |
| `ai_used_for` | What AI was used for, when `ai_level` is above 0. |
| `verified_by`, `verified_date`, `verified_version` | Who verified the implementation, when, and against which description version. Leave all three out until someone has. |

[`schemas/implementation-metadata.schema.json`](schemas/implementation-metadata.schema.json)
defines these fields, and the HARK example's
[`metadata.yml`](projects/HARK/buffer-stock/metadata.yml) shows them in use.
Every pull request runs `tools/check_metadata.py`, which names any missing or
invalid field. To run it before you push:

```sh
python -m pip install -r tools/requirements.txt
python tools/check_metadata.py
```

The check also asks for the implementation's slot in the library table on the
website; a maintainer can add it.

## Versioning model descriptions

Each model description has its own version number, MAJOR.MINOR.

- **A new major version** means implementations must re-run: the model, the
  calibration or the results every implementation reports have changed.
- **A new minor version** is a touch-up, such as clarified wording, a
  corrected typo or an added note, and leaves the results unchanged.
- **0.x is a draft; 1.0 is the working group's release.** While a description
  is a draft, every change raises the minor version, and its changelog entry
  says whether implementations need to re-run.

The version, its status (`draft` or `released`) and the AI disclosure live in
the `options` block of the description's front matter, with the version's
date in `date`. The PDF and the description's web page both show them in a
box at the top right. To release a new version:

1. Raise `version`, set `date`, and update the disclosure fields; a new
   version is not verified until someone verifies it.
2. Add an entry to the model's `CHANGELOG.md`, headed `## <version> — <date>`,
   saying what changed and whether implementations need to re-run.
3. Rebuild the PDF from `models/<model>/` with `myst build --pdf`.
4. After the pull request merges, tag the merge commit `<model>/v<version>`,
   such as `buffer-stock/v0.1`, and publish a GitHub release for the tag with
   the PDF attached.

An implementation states the version it follows in `model_description_version`
and can link to that version's tag in `model_description`.

## AI disclosure and verification

Model descriptions and implementations each record how much AI was involved
in producing them and whether a person has verified them. Both describe the
process. Neither claims that a document is free of errors, and neither ranks
documents or toolkits.

### AI-assistance level

| Level | Meaning |
| --- | --- |
| 0 | No AI was used in the text or code. |
| 1 | AI-assisted editing: people wrote every passage, and AI suggested wording, grammar or consistency fixes. |
| 2 | AI-assisted drafting: people wrote most of it; AI drafted some passages, which people rewrote. |
| 3 | AI-drafted, human-directed: AI drafted most of it to an outline and decisions from people, who edited it throughout. |
| 4 | AI-drafted with light human editing. |

- The level describes how the text and code were produced. Choices about the
  model, the calibration and the results always belong to the authors.
- Report the highest level that applies to any substantial part, such as one
  section or the code, so that one AI-drafted section is not averaged away.
- When the level is above 0, list what AI was used for in `ai_used_for`,
  comma-separated, from: `drafting`, `editing`, `code`, `derivation checks`,
  `literature`, `figures`.

Authors state the level in their pull request, and the reviewer confirms it.

### Human verification

A document is human verified when a named person has read it end to end and
checked it against its sources: a model description against the papers it
cites, an implementation against the model description. Record the person in
`verified_by`, the date in `verified_date` and the version they verified in
`verified_version`. When a description moves to a new version, or an
implementation to a new description version, it shows as not yet verified
until someone verifies the new one.

### How they are shown

The PDF's version box, the description's web page and each slot in the
website's library table show the level as four segments, filled up to the
level, in one neutral colour. A red-to-green scale would suggest that more AI
means less trustworthy, which is the judgement these records avoid.

In the version box, verification is a small label with a solid blue border
once a person has verified the current version and a dashed grey one until
then, matching the filled and open slots of the library table; the label's
words say which. In the library table, a verified implementation's slot ends
in a check mark, and its tooltip gives the verification either way.
