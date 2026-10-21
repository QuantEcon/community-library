"""Build a web page for each model description.

For every models/<model>/model-description.md this writes
docs/models/<model>/index.html and copies the description's PDF beside it.
The page is built from the same Markdown as the PDF, shares the site's
stylesheet and header, and shows the same version box: the version, status
and date, the AI-assistance level and the human-verification record, all
read from the front matter's `options`. MathJax renders the equations, as it
does when GitHub shows the Markdown.

The publishing workflow runs this before it checks and deploys docs/, so the
generated pages are not committed. To preview them, run from the repository
root:

    python -m pip install -r tools/requirements.txt
    python tools/build_pages.py
"""
import datetime
import html
import json
import shutil
import string
from pathlib import Path

import yaml
from markdown_it import MarkdownIt
from mdit_py_plugins.anchors import anchors_plugin
from mdit_py_plugins.dollarmath import dollarmath_plugin
from mdit_py_plugins.footnote import footnote_plugin

ROOT = Path(__file__).resolve().parent.parent
REPOSITORY = "https://github.com/QuantEcon/community-library"
SITE = "https://quantecon.github.io/community-library"

# The word and one-line summary for each AI-assistance category, from the
# schema. CONTRIBUTING.md defines the categories, and
# templates/plain_latex_wide/template.tex prints the same words in the PDF.
SCHEMA = ROOT / "schemas" / "solution-metadata.schema.json"
AI_CATEGORIES = {
    category["level"]: category
    for category in json.loads(SCHEMA.read_text(encoding="utf-8"))["properties"]["ai_level"]["x-categories"]
}


def split_front_matter(text):
    """Return the YAML front matter and the Markdown body of a description."""
    _, front, body = text.split("---\n", 2)
    return yaml.safe_load(front), body


def render_math(content, options):
    """Leave the TeX for MathJax, with its delimiters, escaped for HTML."""
    if options["display_mode"]:
        return f'<div class="math-display">\\[{html.escape(content)}\\]</div>\n'
    return f"\\({html.escape(content)}\\)"


def markdown():
    md = MarkdownIt("commonmark").enable("table")
    md.use(dollarmath_plugin, renderer=render_math)
    md.use(footnote_plugin)
    md.use(anchors_plugin, min_level=2, max_level=3, permalink=True, permalinkSymbol="#")
    return md


def long_date(value):
    day = datetime.date.fromisoformat(str(value))
    return f"{day.day} {day:%B %Y}"


def status_box(options, date):
    """The version box: version, AI category and verification, as in the PDF."""
    version = str(options["version"])
    status = "Released" if options["status"] == "released" else "Draft"
    category = AI_CATEGORIES[int(options["ai_level"])]
    level = category["level"]
    # The category's position between people and AI, then its word and summary.
    stops = "".join('<i class="at"></i>' if stop == level else "<i></i>" for stop in range(len(AI_CATEGORIES)))
    lines = [
        f'<p class="doc-version"><strong>Version {version}</strong> · {status} · {long_date(date)}</p>',
        f'<p class="doc-ai"><span class="ai-position" aria-hidden="true">Human <span class="track">{stops}</span> AI</span>'
        f' <span class="ai-chip" data-level="{level}">{category["word"]}</span></p>',
        f'<p class="doc-ai-summary">{category["summary"]}</p>',
    ]
    if level > 0:
        lines.append(f'<p class="doc-ai-uses">Used for: {html.escape(options["ai_used_for"])}</p>')
    if options.get("verified_by") and str(options.get("verified_version")) == version:
        lines.append(
            '<p class="doc-verified is-verified">Human verified · '
            f'{html.escape(options["verified_by"])}, {long_date(options["verified_date"])}</p>'
        )
    else:
        lines.append(f'<p class="doc-verified">Not yet verified for version {version}</p>')
    return "\n".join(lines)


def build(model_dir, md, template):
    front, body = split_front_matter((model_dir / "model-description.md").read_text(encoding="utf-8"))
    project = yaml.safe_load((model_dir / "myst.yml").read_text(encoding="utf-8"))["project"]
    content = md.render(body)
    # Wide tables scroll inside their own box on a phone instead of the page.
    content = content.replace("<table>", '<div class="table-wrap"><table>').replace("</table>", "</table></div>")
    model = model_dir.name
    page = template.substitute(
        title=html.escape(front["title"]),
        description=html.escape(project["description"]),
        url=f"{SITE}/models/{model}/",
        status_box=status_box(front["options"], front["date"]),
        changelog=f"{REPOSITORY}/blob/main/models/{model}/CHANGELOG.md",
        source=f"{REPOSITORY}/blob/main/models/{model}/model-description.md",
        guide=f"{REPOSITORY}/blob/main/models/{model}/README.md",
        levels="../../contributing/#ai",
        license=html.escape(front["license"]),
        content=content,
    )
    out = ROOT / "docs" / "models" / model
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(page, encoding="utf-8")
    shutil.copyfile(model_dir / "model-description.pdf", out / "model-description.pdf")
    return out / "index.html"


def main():
    md = markdown()
    template = string.Template((ROOT / "tools" / "model-page.html").read_text(encoding="utf-8"))
    for model_dir in sorted((ROOT / "models").iterdir()):
        if (model_dir / "model-description.md").exists():
            print(f"built {build(model_dir, md, template).relative_to(ROOT)}")


if __name__ == "__main__":
    main()
