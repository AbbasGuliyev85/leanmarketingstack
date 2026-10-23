# LeanMarketingStack

Static site built with `python3 build.py` (no dependencies) into `dist/`. Every push to `main` rebuilds and deploys to GitHub Pages:
https://abbasguliyev85.github.io/leanmarketingstack/

## Adding affiliate links
Fill in the URLs in `affiliates.json`, then commit and push. Filled slugs render as `rel="sponsored nofollow"` links; empty ones fall back to the vendor homepage in `homepages.json`.
