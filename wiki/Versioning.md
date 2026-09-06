# Versioning

Releases use **CalVer**: `YYYY.M.R`

| Day of month | Release number |
|--------------|----------------|
| 1st | `.1` (e.g. `2026.9.1`) |
| 15th | `.2` (e.g. `2026.9.2`) |

- Scheduled by `.github/workflows/publish.yml`
- Ad-hoc: merge a PR labelled `release` (`release-on-merge.yml`)
- Manual: **Actions → Publish to GitHub Packages → Run workflow**

Tags are `vYYYY.M.R` and include a CycloneDX SBOM.
