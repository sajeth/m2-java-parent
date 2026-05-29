# Security Policy

## Supported Versions

Only the **latest published version** of each parent POM receives security updates.
Older versions are not patched — consumers should always pin to the latest release.

| Artifact | Supported |
|----------|-----------|
| `com.saji.m2.parent:m2-java-parent` (latest) | ✅ |
| `com.saji.m2.parent:m2-springboot-parent` (latest) | ✅ |
| `com.saji.m2.parent:m2-core-parent` (latest) | ✅ |
| Any version that is not the latest | ❌ |

## Reporting a Vulnerability

**Please do not open a public GitHub issue for security vulnerabilities.**

Report vulnerabilities privately via [GitHub Security Advisories](https://github.com/sajeth/m2-java-parent/security/advisories/new).
Include as much detail as possible:

- The affected artifact and version
- A description of the vulnerability and its potential impact
- Steps to reproduce or a proof-of-concept (if available)
- Any suggested fix or workaround

## Response Timeline

| Stage | Target |
|-------|--------|
| Acknowledgement | Within **3 business days** |
| Initial assessment | Within **7 business days** |
| Patch release (confirmed vulnerabilities) | Within **14 business days** |

If a vulnerability requires coordination with an upstream dependency (e.g. Spring, Netty), the
timeline may extend while waiting for an upstream patch.

## Scope

### In Scope

- Vulnerable **dependency version choices** declared in any `pom.xml` in this repository
- Missing or incorrect **transitive dependency overrides** that expose consumers to known CVEs
- Insecure **default plugin configurations** inherited by child projects

### Out of Scope

- Vulnerabilities in **upstream dependencies** that have no available fix — please report those to the upstream maintainer
- Issues arising from a **consumer's own configuration** overriding the defaults set here
- Vulnerabilities that only affect **test-scoped** dependencies and cannot reach a production classpath
- General questions about dependency versions — open a regular GitHub issue instead

## Security Measures

This repository uses automated tooling on every pull request and release:

| Tool | Purpose |
|------|---------|
| **OWASP Dependency Check** | Scans all declared and transitive dependencies against the NVD (fails on CVSS ≥ 7) |
| **Semgrep** (`p/java`, `p/owasp-top-ten`) | SAST scan of POM and CI configuration |
| **SpotBugs / PMD / Checkstyle** | Static analysis for inherited Java code quality rules |
| **Dependabot** | Keeps GitHub Actions versions current |
| **Weekly dependency upgrade** | Proposes minor/patch bumps via automated PRs with OWASP pre-check |
| **CycloneDX SBOM** | Software Bill of Materials attached to every release |

## Acknowledgements

Responsibly disclosed vulnerabilities will be credited in the release notes unless the reporter requests otherwise.
