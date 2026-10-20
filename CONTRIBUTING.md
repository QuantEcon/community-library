# Contributing to the Community Library

The library takes pull requests from anyone, whether or not they are a member
of the working group. A solution, a runnable implementation of one of the
library's model descriptions, can come from a toolkit's project or from
individual contributors, and one project can submit several. This guide
covers what every solution records: which version of the model description it
follows, who maintains it, how much AI was involved in producing it, and
whether a person has verified it. Each model's submission guide, such as
[the one for buffer stock](models/buffer-stock/README.md), covers what to
implement and report. How submissions are reviewed is being settled in
[#6](https://github.com/QuantEcon/community-library/issues/6).

## Submitting a solution

Put the solution in its own directory under `solutions/<model>/`, using the
model's directory name from `models/`. Name the directory
`<NNN>-<toolkit>-<method>`, in lowercase with hyphens:

- `<NNN>` is the next free three-digit number among the model's solutions, so
  numbers record the order of submission and no two solutions share a name.
  If another pull request takes the same number first, take the next one.
- `<toolkit>-<method>` is a label for people browsing the repository, such as
  `hark-egm` or `julia-vfi`. Two solutions can share it. The `metadata.yml`
  is the record of the toolkit and method.

The HARK example is `solutions/buffer-stock/001-hark-egm/`. A directory keeps
its name for good, so links to it keep working.

Include a `metadata.yml` in the directory. These fields are required; any
others are welcome.

| Field | Content |
| --- | --- |
| `toolkit` | The toolkit the solution uses, or the language and main libraries if it uses none, such as `Julia (no toolkit)`. |
| `method` | A short name for the method, such as `EGM`, `VFI` or `time iteration`. |
| `authors` | A list of the solution's authors, each with a `name`. |
| `maintainers` | The GitHub usernames of the people who maintain the solution and approve changes to it. |
| `model_description_version` | The version of the model description the solution follows, such as `"0.1"`. |
| `ai_level` | How the text and code were produced, from 0 to 3: No AI, AI-edited, AI-assisted or AI-generated; see [AI disclosure and verification](#ai-disclosure-and-verification). |
| `ai_used_for` | What AI was used for, when `ai_level` is above 0. |

Two more fields are added when they apply:

| Field | Content |
| --- | --- |
| `project` | The toolkit project the solution is submitted on behalf of, such as `Econ-ARK`. Leave it out for a solution submitted by individuals. |
| `verified_by`, `verified_date`, `verified_version` | Who verified the solution, when, and against which description version. Leave all three out until someone has. |

[`schemas/solution-metadata.schema.json`](schemas/solution-metadata.schema.json)
defines these fields, and the HARK example's
[`metadata.yml`](solutions/buffer-stock/001-hark-egm/metadata.yml) shows them
in use. Every pull request runs `tools/check_metadata.py`, which names any
missing or invalid field. To run it before you push:

```sh
python -m pip install -r tools/requirements.txt
python tools/check_metadata.py
```

The check also asks for the solution's slot in the library table on the
website, which a maintainer can add. The slot is labelled with the toolkit,
the method, the submitter (the `project`, or else the first author's surname)
and the description version, such as `HARK · EGM · Econ-ARK · v0.1`.

A solution belongs to its authors. Changes to it, by anyone, need the
approval of one of its maintainers.

## Versioning model descriptions

Each model description has its own version number, MAJOR.MINOR.

- **A new major version** means solutions must re-run: the model, the
  calibration or the results every solution reports have changed.
- **A new minor version** is a touch-up, such as clarified wording, a
  corrected typo or an added note, and leaves the results unchanged.
- **0.x is a draft; 1.0 is the working group's release.** While a description
  is a draft, every change raises the minor version, and its changelog entry
  says whether solutions need to re-run.

The version, its status (`draft` or `released`) and the AI disclosure live in
the `options` block of the description's front matter, with the version's
date in `date`. The PDF and the description's web page both show them in a
box at the top right. To release a new version:

1. Raise `version`, set `date`, and update the disclosure fields; a new
   version is not verified until someone verifies it.
2. Add an entry to the model's `CHANGELOG.md`, headed `## <version> — <date>`,
   saying what changed and whether solutions need to re-run.
3. Rebuild the PDF from `models/<model>/` with `myst build --pdf`.
4. After the pull request merges, tag the merge commit `<model>/v<version>`,
   such as `buffer-stock/v0.1`, and publish a GitHub release for the tag:
   - attach the PDF taken from the merge commit, so the release carries
     exactly the tagged PDF;
   - mark a draft (0.x) as a pre-release;
   - in the notes, say what the version contains (its changelog entry), link
     the description's web page, give its status, AI category and
     verification, name the solutions that follow it, and say whether
     solutions need to re-run.

   [AGENTS.md](AGENTS.md) has the commands.

A solution states the version it follows in `model_description_version` and
can link to that version's tag in `model_description`.

## AI disclosure and verification

Model descriptions and solutions each record how much AI was involved in
producing them and whether a person has verified them. Both describe the
process. Neither claims that a document is free of errors, and neither ranks
documents, toolkits or submitters.

### AI-assistance category

| `ai_level` | Category | Meaning |
| --- | --- | --- |
| 0 | No AI | No AI was used in the text or code. |
| 1 | AI-edited | People wrote every passage; AI suggested wording, grammar or consistency fixes. |
| 2 | AI-assisted | AI drafted some or most of it to the authors' outline and decisions, and people rewrote or edited it throughout. |
| 3 | AI-generated | AI drafted it, and people edited it lightly. |

- The category describes how the text and code were produced. Choices about
  the model, the calibration and the results always belong to the authors.
- Report the highest category that applies to any substantial part, such as
  one section or the code, so that one AI-drafted section is not averaged
  away.
- When `ai_level` is above 0, list what AI was used for in `ai_used_for`,
  comma-separated, from: `drafting`, `editing`, `code`, `derivation checks`,
  `literature`, `figures`.

Authors state the category in their pull request, and the reviewer confirms it.

### Human verification

A document is human verified when a named person has read it end to end and
checked it against its sources: a model description against the papers it
cites, a solution against the model description. Record the person in
`verified_by`, the date in `verified_date` and the version they verified in
`verified_version`. When a description moves to a new version, or a solution
to a new description version, it shows as not yet verified until someone
verifies the new one.

### How they are shown

Readers see the category's word, never the number. Each slot in the website's
library table shows it in a neutral outlined chip, such as `AI-assisted`. The
version box on the PDF and on the description's web page also shows a marker
on a line from Human to AI at the category's position, and the category's
one-line summary. The chip and the marker use one neutral colour: the category
describes how the work was produced, so there is no scale to fill and no
red-to-green judgement.

In the version box, verification is a small label with a solid blue border
once a person has verified the current version and a dashed grey one until
then, matching the filled and open slots of the library table; the label's
words say which. In the library table, a verified solution's slot, and a
verified description's button, carry a "✓ Verified" badge. A maintainer adds
it by setting the element's `data-verified` to `"true"` and, for a slot,
removing its "not yet verified" text; the metadata check reports any element
that disagrees with the records.
