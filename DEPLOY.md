# Deploying LeanMarketingStack for free

The site is plain static HTML. Running `python3 build.py` writes it to `dist/`. It needs no dependencies beyond Python 3.

## Before you deploy
1. Edit `site.json`: set `url` to your final address (for example `https://leanmarketingstack.pages.dev` or `https://<username>.github.io`), and set `contact_email`.
2. Replace the placeholders in `pages/about.md` and `pages/privacy.md` (`*_PLACEHOLDER`).
3. Paste your affiliate links into `affiliates.json` once you're approved. Until then they render as `#affiliate-<slug>`, and the build prints a warning.
4. Run `python3 build.py`. To preview locally, run `cd dist && python3 -m http.server 8000` and open http://localhost:8000.

## Option A: Cloudflare Pages (recommended, gives you a free `*.pages.dev` subdomain)
1. Create a free GitHub account and a new repository, then push this folder to it.
2. Create a free Cloudflare account, then go to **Workers & Pages > Create > Pages > Connect to Git** and choose the repo.
3. Build settings: Framework preset **None**, build command `python3 build.py`, output directory `dist`.
4. Deploy. Your site will be at `https://<project-name>.pages.dev`. Set `site.json` `url` to match, then push again.
   - Alternative with no Git: run `python3 build.py` locally, then choose **Upload assets** in Pages and drag in the `dist/` folder.

## Option B: GitHub Pages (`<username>.github.io`)
1. Name the repo `<username>.github.io` (this serves the site at the root, so `/style.css` paths work).
2. Add `.github/workflows/pages.yml`:
```yaml
name: Deploy
on: { push: { branches: [main] } }
permissions: { contents: read, pages: write, id-token: write }
jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: github-pages
    steps:
      - uses: actions/checkout@v4
      - run: python3 build.py
      - uses: actions/upload-pages-artifact@v3
        with: { path: dist }
      - uses: actions/deploy-pages@v4
```
3. In the repo, go to **Settings > Pages > Source: GitHub Actions**, then push to `main`.

## After going live (also free)
- Add the site to Google Search Console and Bing Webmaster Tools, and submit `https://<your-url>/sitemap.xml`.
- Optional: turn on Cloudflare Web Analytics, then update the privacy policy.
- Later, buy a custom domain (the first paid upgrade, about $10–15/yr) and point it at Pages.

## Adding articles
Add a Markdown file to `content/` with `title`, `description` and `date` front matter, keep the disclosure line at the top, then rebuild.
