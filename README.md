# AWS EC2 instance type pricing comparison

**Use here 👉 [ec2instances.github.io](https://ec2instances.github.io)**

Built with:

1. EC2 pricing data from AWS (the same source their pricing page pulls it from).
2. [Tabulator](http://tabulator.info/) to convert the JSON data to a sortable table.
3. GitHub Actions and GitHub Pages - daily pricing snapshots stored alongside the site
4. [Open Props](https://open-props.style/) - minimalistic CSS framework (think Tailwind CSS, but based on CSS variables)

## Why build this?

Remember `https://ec2instances.info/` (now available at `https://instances.vantage.sh/`) ? Used to be a great website, but it has some unfixed bugs, lags updates etc.

I got tired of waiting for bugs to be fixed and created this.

## Pricing updates and hosting

`.github/workflows/pages.yml` downloads Linux and Windows pricing for every region
listed in AWS's metadata, combines each region into one JSON file, and deploys the
site and data together to GitHub Pages. It runs daily at 05:23 UTC, on pushes to
`main`, and through **Actions → Refresh pricing and deploy Pages → Run workflow**.
The page displays the time of the last successful snapshot.

For a local preview (Python 3.9+):

```sh
python3 scripts/build_site.py
python3 -m http.server 8000 --directory _site
```

Open http://localhost:8000. The build requires internet access to AWS; `_site/` is
generated and ignored by Git.

### Contributions welcome

---

&copy; Alex Yumashev https://ec2instances.github.io
