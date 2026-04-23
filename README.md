# propawstech.com — static site

Hosts the marketing landing page, Privacy Policy, Terms of Service, and
Support page for SnootScoot (and eventually GoldenGlide). Served via
**GitHub Pages** with a custom domain so the URLs match what's hardcoded
in `BeagleSnootScoot/Utilities/Config.swift`:

- `https://propawstech.com/snootscoot/privacy`
- `https://propawstech.com/snootscoot/terms`
- `https://propawstech.com/snootscoot/support`

## Layout

```
site/
  CNAME                                # propawstech.com — required by GH Pages
  _shared.css                          # source-of-truth CSS, inlined by build.py
  build.py                             # markdown → HTML for legal pages
  index.html                           # propawstech.com root landing
  snootscoot/
    index.html                         # /snootscoot — app landing (hand-edited)
    privacy/index.html                 # generated from Docs/PRIVACY_POLICY.md
    terms/index.html                   # generated from Docs/TERMS_OF_SERVICE.md
    support/index.html                 # generated from Docs/SUPPORT.md
```

The legal pages have **one source of truth**: the markdown files in `/Docs`.
Run `python3 site/build.py` after editing them.

## First-time deployment (GitHub Pages, custom domain)

This repo is `propawstech/snootscoot-ios`. GitHub Pages can serve from any
branch + folder. The cleanest setup for path-based URLs is:

### Option A — separate `propawstech.github.io` repo (recommended)

Best for keeping the iOS source repo focused on iOS code.

1. Create a new public repo on GitHub: `propawstech/propawstech.github.io`
2. Copy the contents of `site/` (everything inside, not the folder itself)
   into the root of that repo, then push to `main`.
3. In repo Settings → Pages → Source = `Deploy from a branch`, branch =
   `main`, folder = `/`. Save.
4. In repo Settings → Pages → Custom domain → enter `propawstech.com`.
   Save. Tick **Enforce HTTPS** once it lights up (a few minutes).
5. In your domain registrar's DNS settings for `propawstech.com`, add:
   ```
   A     @   185.199.108.153
   A     @   185.199.109.153
   A     @   185.199.110.153
   A     @   185.199.111.153
   AAAA  @   2606:50c0:8000::153
   AAAA  @   2606:50c0:8001::153
   AAAA  @   2606:50c0:8002::153
   AAAA  @   2606:50c0:8003::153
   CNAME www propawstech.github.io.
   ```
   These are GitHub's published Pages IPs and don't change. Propagation
   takes 5–60 minutes.
6. Visit `https://propawstech.com/snootscoot/privacy` to verify.

### Option B — serve directly from this repo

Faster but mixes concerns. Useful if you want to ship today and migrate
later.

1. In `propawstech/snootscoot-ios` Settings → Pages → Source = branch
   `main`, folder = `/site`. Save.
2. Custom domain + DNS as above.
3. URL pattern is the same — `/site` becomes the served root.

The `CNAME` file inside `site/` is what tells GitHub Pages which custom
domain to serve, so it works for both options.

## Updating legal copy

```bash
# 1. Edit the markdown
vim Docs/PRIVACY_POLICY.md

# 2. Regenerate HTML
python3 site/build.py

# 3. Commit both the markdown and the generated HTML
git add Docs/PRIVACY_POLICY.md site/snootscoot/privacy/index.html
git commit -m "Update privacy policy: <what changed>"
git push
```

GitHub Pages picks up the change within a minute or two.

## When you change brand copy or styling

- **CSS** → edit `site/_shared.css`, then `python3 site/build.py` to inline
  it into every legal page. Hand-edited landing pages
  (`site/index.html`, `site/snootscoot/index.html`) have their own inline
  styles — update those manually if you want them to match.
- **Landing page copy** → edit `site/snootscoot/index.html` directly. It
  is not regenerated.

## Build dependencies

- Python 3.x (ships with macOS)
- `markdown` package: `pip3 install --user markdown`
