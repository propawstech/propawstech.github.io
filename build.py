#!/usr/bin/env python3
"""
build.py — generate static HTML for propawstech.com from the templated
markdown sources in /Docs.

Why a build step instead of writing HTML by hand:
  Legal documents change. We want exactly one source of truth (the
  markdown in /Docs) so the in-app `LegalDocSheet`, the App Store
  Connect privacy URL, the hosted page, and any future README links all
  reflect identical wording. Hand-maintaining duplicate HTML drifts.

Why templating:
  As of 2026-04-26 the portfolio includes multiple apps (BeagleBay,
  GoldenGrin, …). The legal text is identical across them except for
  the app name itself. Source markdown uses `{{APP_NAME}}` placeholders;
  this script substitutes per app at build time.

Usage:
  python3 site/build.py

Outputs (per app in APPS):
  site/<slug>/privacy/index.html
  site/<slug>/terms/index.html
  site/<slug>/support/index.html

The file `site/CNAME`, the root landing page (`site/index.html`), and
the per-app marketing landing pages (`site/<slug>/index.html`) are NOT
regenerated — those are static and edited by hand.

Bundled iOS legal markdown (`BeagleSnootScoot/Resources/Legal/`) is
currently shared between targets and gets the FIRST app in APPS as its
substitution. When a second app gets close to ship, split this into
per-target Legal directories.
"""

import sys
from pathlib import Path

try:
    import markdown
except ImportError:
    print(
        "ERROR: python `markdown` package not installed.\n"
        "Install with:  pip3 install --user markdown",
        file=sys.stderr,
    )
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "Docs"
SITE = ROOT / "site"
# Bundled iOS resources — kept in sync with /Docs so the in-app
# `LegalDocSheet` always matches what's on propawstech.com, even when
# the device is offline.
BUNDLED_LEGAL = ROOT / "BeagleSnootScoot" / "Resources" / "Legal"
CSS = (SITE / "_shared.css").read_text(encoding="utf-8")

# Per-app config. `slug` is the URL path segment AND the local site/
# directory name. `name` is the user-visible product name substituted
# into every {{APP_NAME}} placeholder in the markdown sources. Add a
# new app by appending here — no other code changes needed.
APPS = [
    {"slug": "beaglebay",  "name": "BeagleBay"},
    {"slug": "goldengrin", "name": "GoldenGrin"},
]

# (source markdown filename, output sub-directory under site/<slug>/,
# page <title> template — `{name}` interpolated per app)
PAGES = [
    ("PRIVACY_POLICY.md",   "privacy", "{name} · Privacy Policy"),
    ("TERMS_OF_SERVICE.md", "terms",   "{name} · Terms of Service"),
    ("SUPPORT.md",          "support", "{name} · Support"),
]

# Markdown extras worth enabling:
#   tables      — our policy has rights/data tables
#   fenced_code — for any code blocks
#   sane_lists  — strict list parsing
EXTENSIONS = ["tables", "fenced_code", "sane_lists"]

TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="robots" content="index,follow">
    <title>{title}</title>
    <style>
{css}
    </style>
</head>
<body>
<main>
    <header>
        <a class="brand" href="/{slug}/">{name}</a>
        <nav>
            <a href="/{slug}/privacy">Privacy</a>
            <a href="/{slug}/terms">Terms</a>
            <a href="/{slug}/support">Support</a>
        </nav>
    </header>
    {body}
    <footer>
        © ProPawsTech. {name} is built independently and not
        affiliated with Apple Inc., the American Kennel Club, or any
        breed registry.
    </footer>
</main>
</body>
</html>
"""


def substitute(md_text: str, app: dict) -> str:
    """Replace `{{APP_NAME}}` (and any future placeholders) per app."""
    return md_text.replace("{{APP_NAME}}", app["name"])


def build_one_page(app: dict, source_md: str, sub_dir: str, title_template: str) -> Path:
    src = DOCS / source_md
    if not src.exists():
        raise FileNotFoundError(f"Missing source: {src}")
    md_raw = src.read_text(encoding="utf-8")
    md_text = substitute(md_raw, app)
    html_body = markdown.markdown(md_text, extensions=EXTENSIONS)
    rendered = TEMPLATE.format(
        title=title_template.format(name=app["name"]),
        css=CSS,
        slug=app["slug"],
        name=app["name"],
        body=html_body,
    )
    out = SITE / app["slug"] / sub_dir / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(rendered, encoding="utf-8")
    return out


def write_bundled_for_first_app() -> list[Path]:
    """Mirror substituted markdown into the iOS bundle's Resources/Legal/.
    Currently only the first app in APPS gets bundled — both targets
    share this directory at the moment, so this matches whatever app
    is shipping closest. Split into per-target Legal dirs when the
    second app is close to ship."""
    if not APPS:
        return []
    first = APPS[0]
    BUNDLED_LEGAL.mkdir(parents=True, exist_ok=True)
    written = []
    for source_md, _, _ in PAGES:
        src = DOCS / source_md
        md_text = substitute(src.read_text(encoding="utf-8"), first)
        bundled = BUNDLED_LEGAL / source_md
        bundled.write_text(md_text, encoding="utf-8")
        written.append(bundled)
    return written


def main() -> int:
    print(f"build.py: docs source    = {DOCS}")
    print(f"build.py: site output    = {SITE}")
    print(f"build.py: bundled legal  = {BUNDLED_LEGAL}")
    print(f"build.py: apps           = {[a['slug'] for a in APPS]}")
    print()

    for app in APPS:
        print(f"  [{app['name']}]")
        for src, sub_dir, title in PAGES:
            html_path = build_one_page(app, src, sub_dir, title)
            print(f"    ✓ {src:24}  →  {html_path.relative_to(ROOT)}")

    print()
    print(f"  [bundled legal — first app: {APPS[0]['name']}]")
    for path in write_bundled_for_first_app():
        print(f"    ✓ {path.relative_to(ROOT)}")

    print()
    print("Done. Commit and push site/ and (if changed) Resources/Legal/ to publish.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
