# Security Policy

## Supported Versions

Only the **latest published version** of each parent POM receives security updates.
Older versions are not patched — consumers should always pin to the latest release.

| Artifact | Supported |
|----------|-----------|
| `io.github.sajeth:m2-java-parent` (latest) | ✅ |
| `io.github.sajeth:m2-springboot-parent` (latest) | ✅ |
| `io.github.sajeth:m2-core-parent` (latest) | ✅ |
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

## Secure Coding Principles

These principles apply to all contributors and are enforced (where automatable) by the CI pipeline.

### 1 — Dependency Hygiene

| Principle | How it is enforced |
|---|---|
| Pin every direct dependency to a specific version | `dependencyManagement` in each POM; Dependabot opens upgrade PRs |
| Override transitive dependencies that carry CVEs | `<dependencyManagement>` override + inline comment with CVE ID, CVSS score, and fix version |
| Never introduce a CVSS ≥ 7 dependency without an accepted suppression | OWASP Dependency Check fails the build at that threshold |
| Document every CVE suppression | `.github/owasp-suppressions.xml` — each entry must explain risk acceptance and a revisit date |
| Both Jackson families need independent patching | `tools.jackson.core` (3.x) and `com.fasterxml.jackson.core` (2.x) coexist; track CVEs for both |

**Comment pattern for every dependency change:**
```xml
<!-- Bump foo to 1.2.3 to patch CVE-2026-99999 (CVSS 8.1), fixed in 1.2.3 -->
<dependency>
    <groupId>com.example</groupId>
    <artifactId>foo</artifactId>
    <version>1.2.3</version>
</dependency>
```

### 2 — Supply Chain Security

- **SHA-pin every GitHub Actions reference** — use `uses: owner/action@<40-char-sha>  # vX.Y.Z`. Tag references are mutable and can be hijacked.
- **Sign every release** — the `release` Maven profile enforces GPG signing via the Sonatype Central Portal plugin; unsigned artifacts are rejected by Maven Central.
- **Attach a CycloneDX SBOM** to every release — consumers can audit the full dependency graph.
- **Generate SLSA provenance** after each publish — the `publish.yml` workflow creates a provenance attestation via the SLSA GitHub generator.
- **Use `permissions: {}` at the workflow level** — every workflow denies all token permissions by default; each job declares only what it needs.
- **No secrets in code or POMs** — credentials are injected via GitHub Actions secrets and repository variables only.

### 3 — CI/CD Hardening

- **Least-privilege tokens** — each job requests only the GitHub token scopes it actually uses (e.g. `contents: read`, `pull-requests: write`). Never use `permissions: write-all`.
- **Isolate Dependabot PRs** — `dependabot-gate.yml` serialises runs so only the oldest open Dependabot PR runs checks at any one time, preventing resource exhaustion.
- **Separate approval from merge** — Dependabot PRs are auto-approved after passing all checks; human PRs require an explicit merge action.
- **Scan on every PR** — OWASP, Semgrep, SpotBugs, PMD, Checkstyle, Qodana, and OpenSSF Scorecard all run before any code reaches `master`.

### 4 — Inherited Defaults for Consumers

Child projects that declare any module in this hierarchy as their `<parent>` automatically inherit:

| Default | Value | Purpose |
|---|---|---|
| JaCoCo line/branch coverage gate | 70% | Prevents shipping untested code |
| SpotBugs effort / threshold | Max / Low | Catches the widest set of bug patterns |
| Checkstyle ruleset | `google_checks.xml` | Consistent, reviewed style baseline |
| Dependency Check CVSS threshold | 7.0 | Blocks high-severity CVEs at build time |
| Surefire `forkCount` | `1C` (1× CPU count) | Prevents test interference |

Consumers **must not** weaken these thresholds without explicit justification. To tighten a threshold (e.g. raise coverage to 80%) override the relevant property in the child POM.

### 5 — Code Review Requirements

- All changes to any `pom.xml` that add, remove, or update a dependency require a description of **why** the change is needed.
- Any new CVE suppression must be reviewed for risk acceptance and include a concrete revisit date.
- Workflow changes (`.github/workflows/`) are linted by `actionlint` and reviewed for token-permission scope creep.

### Verification Checklist

Run these commands before opening a PR to verify no principles are violated:

```bash
# 1. Dependency vulnerability scan (must exit 0)
mvn org.owasp:dependency-check-maven:check -DskipTests --batch-mode

# 2. Static analysis — results posted as annotations, exit code is advisory
mvn com.github.spotbugs:spotbugs-maven-plugin:spotbugs \
    org.apache.maven.plugins:maven-pmd-plugin:pmd \
    org.apache.maven.plugins:maven-checkstyle-plugin:checkstyle \
    -DskipTests --batch-mode

# 3. Workflow lint
actionlint .github/workflows/*.yml

# 4. Verify all SHA-pinned actions have version comments
grep -rn 'uses:' .github/workflows/ | grep -v '#'  # should return nothing
```

## Acknowledgements

Responsibly disclosed vulnerabilities will be credited in the release notes unless the reporter requests otherwise.
