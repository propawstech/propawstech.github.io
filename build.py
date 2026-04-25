#!/usr/bin/env python3
"""
build.py — generate static HTML for propawstech.com from the markdown
sources in /Docs.

Why a build step instead of writing HTML by hand:
  Legal documents change. We want exactly one source of truth (the
  markdown in /Docs) so the in-app `LegalDocSheet`, the App Store
  Connect privacy URL, the hosted page, and any future README links all
  reflect identical wording. Hand-maintaining duplicate HTML drifts.

Usage:
  python3 site/build.py

Outputs:
  site/beaglebay/privacy/index.html
  site/beaglebay/terms/index.html
  site/beaglebay/support/index.html

The file `site/CNAME` and the existing landing pages
(`site/index.html`, `site/beaglebay/index.html`) are NOT regenerated —
those are static and edited by hand.
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
# Bundled iOS resources — keeping these in sync with /Docs means the
# in-app `LegalDocSheet` always matches what's on propawstech.com,
# even when the device is offline.
BUNDLED_LEGAL = ROOT / "BeagleSnootScoot" / "Resources" / "Legal"
CSS = (SITE / "_shared.css").read_text(encoding="utf-8")

# (source markdown, output dir under site/, page <title>)
PAGES = [
    ("PRIVACY_POLICY.md",   "beaglebay/privacy", "BeagleBay · Privacy Policy"),
    ("TERMS_OF_SERVICE.md", "beaglebay/terms",   "BeagleBay · Terms of Service"),
    ("SUPPORT.md",          "beaglebay/support", "BeagleBay · Support"),
]

# Markdown extras worth enabling:
#   tables    — our policy has rights/data tables
#   fenced_code — for any code blocks
#   sane_lists — strict list parsing
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
        <a class="brand" href="/beaglebay/">BeagleBay</a>
        <nav>
            <a href="/beaglebay/privacy">Privacy</a>
            <a href="/beaglebay/terms">Terms</a>
            <a href="/beaglebay/support">Support</a>
        </nav>
    </header>
    {body}
    <footer>
        © ProPawsTech. BeagleBay is built independently and not
        affiliated with Apple Inc., the American Kennel Club, or any
        breed registry.
    </footer>
</main>
</body>
</html>
"""


def build_one(source_md: str, out_dir: str, title: str) -> tuple[Path, Path]:
    src = DOCS / source_md
    if not src.exists():
        raise FileNotFoundError(f"Missing source: {src}")
    md_text = src.read_text(encoding="utf-8")
    html_body = markdown.markdown(md_text, extensions=EXTENSIONS)
    rendered = TEMPLATE.format(
        title=title,
        css=CSS,
        body=html_body,
    )
    out = SITE / out_dir / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(rendered, encoding="utf-8")

    # Mirror the raw markdown into the iOS app bundle so `LegalDocSheet`
    # has an offline fallback that always matches the hosted site.
    BUNDLED_LEGAL.mkdir(parents=True, exist_ok=True)
    bundled = BUNDLED_LEGAL / source_md
    bundled.write_text(md_text, encoding="utf-8")
    return out, bundled


def main() -> int:
    print(f"build.py: docs source    = {DOCS}")
    print(f"build.py: site output    = {SITE}")
    print(f"build.py: bundled legal  = {BUNDLED_LEGAL}")
    for src, out_dir, title in PAGES:
        html_path, md_path = build_one(src, out_dir, title)
        print(f"  ✓ {src:24}  →  {html_path.relative_to(ROOT)}")
        print(f"  ✓ {src:24}  →  {md_path.relative_to(ROOT)}")
    print("Done. Commit and push site/ to publish.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
