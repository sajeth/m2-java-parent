# Versioning

Releases use **CalVer**: `YYYY.M.W`

| Field | Meaning                                      |
|-------|----------------------------------------------|
| YYYY  | Calendar year                                |
| M     | Month (no zero-pad)                          |
| W     | Week of month (1–5), from the Monday publish |

Examples: `2026.9.1`, `2026.9.2`, `2026.9.5`

- Scheduled **every Monday** by `.github/workflows/publish.yml` (12:00 UTC)
- Ad-hoc: merge a PR labelled `release` (`release-on-merge.yml`)
- Manual: **Actions → Publish to GitHub Packages → Run workflow**

Tags are `vYYYY.M.W` and include a CycloneDX SBOM.

Dependency updates are fully autonomous via Dependabot (no human review required).
