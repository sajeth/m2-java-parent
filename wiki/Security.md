# Security

Only the **latest published version** of each parent POM is supported.

## Report a vulnerability

Do **not** open a public issue for security bugs.

1. Open a [private security advisory](https://github.com/sajeth/m2-java-parent/security/advisories/new)
2. Include artifact, version, impact, and reproduction steps

Full policy: [SECURITY.md](https://github.com/sajeth/m2-java-parent/blob/master/SECURITY.md)

## Automation

| Tool                   | Role                                                                 |
|------------------------|----------------------------------------------------------------------|
| Dependabot             | Actions + Maven update PRs                                           |
| Dependency Upgrade     | Minor/patch bumps for `<properties>` via mvnrepository links → PR    |
| Latest Releases        | Same as above, including major bumps → PR                            |
| OWASP Dependency-Check | Fails on CVSS ≥ 7                                                    |
| CycloneDX              | SBOM on each release                                                 |

Property entries must include a `https://mvnrepository.com/artifact/...` comment
link (see root [SECURITY.md](../SECURITY.md)).
