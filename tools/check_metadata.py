"""Check the library's versions and disclosure records against its rules.

  * Each models/<model>/model-description.md states its version, status and
    AI disclosure in its front matter `options`, and the newest entry in its
    CHANGELOG.md is for that version and date.
  * Each solution, solutions/<model>/<NNN>-<toolkit>-<method>/, is named in
    that form with a number not used by another solution of the model, and
    has a metadata.yml that satisfies schemas/solution-metadata.schema.json
    and follows a version its model description has had.
  * The library table in docs/index.html has a slot for every solution,
    labelled with its toolkit, method, submitter and version, and showing the
    AI category and verification its metadata.yml records.
  * The contributing page, docs/contributing/index.html, shows each AI
    category with the word and summary the schema gives it.

CONTRIBUTING.md explains the rules. The publishing workflow runs this check on
every push and pull request; to run it locally, from the repository root:

    python -m pip install -r tools/requirements.txt
    python tools/check_metadata.py
"""
import datetime
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent.parent
SCHEMA = ROOT / "schemas" / "solution-metadata.schema.json"
CHANGELOG_ENTRY = re.compile(r"^## (\d+\.\d+) — (\d{4}-\d{2}-\d{2})$", re.M)
# A solution's directory: its submission number within the model, then a
# label for people browsing. The metadata, not the name, is the record.
SOLUTION_NAME = re.compile(r"^(\d{3})-[a-z0-9]+(-[a-z0-9]+)+$")
DISCLOSURE_FIELDS = ("ai_level", "ai_used_for", "verified_by", "verified_date", "verified_version")


def plain(value):
    """YAML reads an unquoted 2026-10-20 as a date; the schema expects text."""
    if isinstance(value, dict):
        return {key: plain(item) for key, item in value.items()}
    if isinstance(value, list):
        return [plain(item) for item in value]
    if isinstance(value, datetime.date):
        return value.isoformat()
    return value


def schema_problems(validator, data, where):
    problems = []
    for error in sorted(validator.iter_errors(data), key=str):
        message = error.message
        if error.validator == "pattern" and "description" in error.schema:
            # The schema's own description says what is allowed; a regex does not.
            message = f"{error.instance!r} is not valid. {error.schema['description']}"
        problems.append(f"{where}: {'.'.join(map(str, error.absolute_path)) or 'top level'}: {message}")
    return problems


def description_validator(schema):
    """Descriptions share the solutions' disclosure fields and rules."""
    return Draft202012Validator({
        "type": "object",
        "required": ["version", "status", "ai_level"],
        "properties": {
            "version": {"type": "string", "pattern": r"^[0-9]+\.[0-9]+$"},
            "status": {"enum": ["draft", "released"]},
            **{field: schema["properties"][field] for field in DISCLOSURE_FIELDS},
        },
        "dependentRequired": schema["dependentRequired"],
        "if": schema["if"],
        "then": schema["then"],
    })


def check_descriptions(problems, validator):
    """Return each model's current version and every version it has had."""
    descriptions = {}
    for path in sorted(ROOT.glob("models/*/model-description.md")):
        where = path.relative_to(ROOT)
        front = yaml.safe_load(path.read_text(encoding="utf-8").split("---\n", 2)[1])
        options = plain(front.get("options") or {})
        found = schema_problems(validator, options, f"{where}, options")
        problems += found
        if found:
            continue
        version = options["version"]
        if (version.split(".")[0] == "0") != (options["status"] == "draft"):
            expected = "draft" if version.startswith("0.") else "released"
            problems.append(f"{where}: version {version} should have status {expected}")
        changelog = path.parent / "CHANGELOG.md"
        entries = CHANGELOG_ENTRY.findall(changelog.read_text(encoding="utf-8")) if changelog.exists() else []
        if not entries:
            problems.append(f"{changelog.relative_to(ROOT)}: add an entry headed '## {version} — {plain(front['date'])}'")
        elif entries[0] != (version, plain(front["date"])):
            problems.append(
                f"{changelog.relative_to(ROOT)}: the newest entry is for {entries[0][0]} ({entries[0][1]}), "
                f"but {where} is version {version} ({plain(front['date'])})"
            )
        descriptions[path.parent.name] = {
            "version": version,
            "all": {entry[0] for entry in entries},
            "verified": verified(options, version),
        }
    return descriptions


def check_solutions(problems, validator, descriptions):
    """Return each solution's metadata, keyed by its directory."""
    solutions, numbers = {}, {}
    for directory in sorted(path for path in ROOT.glob("solutions/*/*") if path.is_dir()):
        where = directory.relative_to(ROOT).as_posix()
        model = directory.parent.name
        name = SOLUTION_NAME.match(directory.name)
        if not name:
            problems.append(
                f"{where}: name the directory <NNN>-<toolkit>-<method>, such as 001-hark-egm, "
                "with the next free three-digit number for the model"
            )
        else:
            other = numbers.setdefault((model, name.group(1)), where)
            if other != where:
                problems.append(f"{where}: number {name.group(1)} is already used by {other}; take the next free number")
        path = directory / "metadata.yml"
        if not path.exists():
            problems.append(f"{where}: add a metadata.yml; CONTRIBUTING.md lists the required fields")
            continue
        data = plain(yaml.safe_load(path.read_text(encoding="utf-8")) or {})
        found = schema_problems(validator, data, f"{where}/metadata.yml")
        problems += found
        if found:
            continue
        if data.get("model", model) != model:
            problems.append(f"{where}/metadata.yml: model is {data['model']!r}, but the directory says {model!r}")
        if model not in descriptions:
            problems.append(f"{where}: there is no model description at models/{model}/")
        elif data["model_description_version"] not in descriptions[model]["all"]:
            problems.append(
                f"{where}/metadata.yml: model_description_version {data['model_description_version']} is not a "
                f"version of models/{model}/; its CHANGELOG.md lists {', '.join(sorted(descriptions[model]['all']))}"
            )
        solutions[where] = data
    return solutions


class LibraryTable(HTMLParser):
    """Collect the elements of docs/index.html that carry library records."""

    def __init__(self):
        super().__init__()
        self.records, self.open = [], []

    VOID = {"br", "img", "input", "wbr", "hr", "meta", "link"}

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        for record in self.open:
            record["depth"] += tag not in self.VOID
            if "ai-chip" in (attrs.get("class") or "").split():
                record["ai_level"] = attrs.get("data-level")
        if "data-solution" in attrs or "data-model-description" in attrs:
            self.open.append({"attrs": attrs, "text": "", "depth": 0})

    def handle_endtag(self, tag):
        for record in list(self.open):
            if record["depth"] == 0:
                self.open.remove(record)
                self.records.append(record)
            else:
                record["depth"] -= 1

    def handle_data(self, data):
        for record in self.open:
            record["text"] += data


def verified(record, version):
    return bool(record.get("verified_by")) and record.get("verified_version") == version


def slot_label(record):
    """Toolkit, method and submitter: the project, or the first author's surname."""
    submitter = record.get("project") or record["authors"][0]["name"].split()[-1]
    return f"{record['toolkit']} · {record['method']} · {submitter} · v{record['model_description_version']}"


def check_site(problems, descriptions, solutions, words):
    table = LibraryTable()
    table.feed((ROOT / "docs" / "index.html").read_text(encoding="utf-8"))
    shown = set()
    for element in table.records:
        attrs, text = element["attrs"], " ".join(element["text"].split())
        if "data-model-description" in attrs:
            model = attrs["data-model-description"]
            description = descriptions.get(model, {})
            version = description.get("version")
            if attrs.get("data-version") != version or f"v{version}" not in text:
                problems.append(f"docs/index.html: the {model} description should show v{version}, as its front matter says")
            wanted = "true" if description.get("verified") else "false"
            if attrs.get("data-verified") != wanted:
                problems.append(
                    f"docs/index.html: the {model} description button has data-verified "
                    f"{attrs.get('data-verified')!r}; its front matter gives {wanted!r}"
                )
            continue
        where = attrs["data-solution"]
        record = solutions.get(where)
        if record is None:
            problems.append(f"docs/index.html: {where} has a slot but no valid metadata.yml")
            continue
        shown.add(where)
        version = record["model_description_version"]
        if slot_label(record) not in text:
            problems.append(f"docs/index.html: label the slot for {where} '{slot_label(record)}', as its metadata.yml says")
        if words[record["ai_level"]] not in text:
            problems.append(f"docs/index.html: the slot for {where} should show '{words[record['ai_level']]}', as its metadata.yml says")
        expected = {
            "data-version": (attrs.get("data-version"), version),
            "AI category": (element.get("ai_level"), str(record["ai_level"])),
            "data-verified": (attrs.get("data-verified"), "true" if verified(record, version) else "false"),
        }
        for name, (found, wanted) in expected.items():
            if found != wanted:
                problems.append(f"docs/index.html: the slot for {where} has {name} {found!r}; its metadata.yml gives {wanted!r}")
        # The Verified badge is drawn from data-verified; until then the slot
        # tells screen readers it is not yet verified.
        if ("not yet verified" in text) == verified(record, version):
            state = "remove its 'not yet verified' text" if verified(record, version) else "add ', not yet verified' for screen readers"
            problems.append(f"docs/index.html: the slot for {where} should {state}, as its metadata.yml says")
    for where in sorted(set(solutions) - shown):
        problems.append(f"docs/index.html: add a slot for {where} to the library table")


def check_guide(problems, categories):
    """The contributing page repeats the AI categories by hand; keep it in step."""
    page = (ROOT / "docs" / "contributing" / "index.html").read_text(encoding="utf-8")
    for category in categories:
        shown = f'<span class="ai-chip" data-level="{category["level"]}">{category["word"]}</span>'
        summary = f'<span class="ai-summary">{category["summary"]}</span>'
        if shown not in page or summary not in page:
            problems.append(
                f"docs/contributing/index.html: show category {category['level']} as "
                f"'{category['word']}' with the summary '{category['summary']}', as the schema says"
            )


def main():
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    problems = []
    descriptions = check_descriptions(problems, description_validator(schema))
    solutions = check_solutions(problems, Draft202012Validator(schema), descriptions)
    categories = schema["properties"]["ai_level"]["x-categories"]
    words = {category["level"]: category["word"] for category in categories}
    check_site(problems, descriptions, solutions, words)
    check_guide(problems, categories)
    for problem in problems:
        print(f"::error::{problem}")
    if problems:
        sys.exit(1)
    print(f"ok — {len(descriptions)} model description(s) and {len(solutions)} solution(s) "
          "carry valid versions and disclosure, and the library table matches them")


if __name__ == "__main__":
    main()
