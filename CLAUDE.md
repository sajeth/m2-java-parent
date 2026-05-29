# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repository Is

`io.github.sajeth:m2-java-parent` is a Maven parent POM hierarchy — there is no Java source code in this repo. Every artifact has `<packaging>pom</packaging>`. The sole output is a set of published parent POMs that downstream Java 25 projects inherit from.

## Build Commands

```bash
# Build and install all modules locally
mvn install

# Run tests and generate JaCoCo coverage report (output: target.nosync/site/jacoco/)
mvn verify

# Static analysis (run each independently; results posted as PR annotations)
mvn com.github.spotbugs:spotbugs-maven-plugin:spotbugs -DskipTests --batch-mode
mvn org.apache.maven.plugins:maven-pmd-plugin:pmd -DskipTests --batch-mode
mvn org.apache.maven.plugins:maven-checkstyle-plugin:checkstyle -DskipTests --batch-mode

# Generate CycloneDX SBOM (output: target.nosync/bom.{json,xml})
mvn org.cyclonedx:cyclonedx-maven-plugin:makeAggregateBom -DskipTests --batch-mode

# Bump all module versions (used by the release workflow)
mvn org.codehaus.mojo:versions-maven-plugin:2.17.1:set -DnewVersion=YYYY.M.R -DgenerateBackupPoms=false

# Preview available minor/patch dependency upgrades (does not apply them)
mvn org.codehaus.mojo:versions-maven-plugin:2.17.1:display-property-updates

# Publish to Maven Central (requires GPG key and Central credentials in env)
mvn deploy -Prelease -DskipTests --batch-mode
```

Build artifacts go to `target.nosync/` (not `target/`) across all modules. This is intentional to prevent macOS iCloud from syncing build output.

## POM Hierarchy

```
m2-java-parent                    (root — Java 25, Lombok, JaCoCo, Surefire, static-analysis plugins)
├── m2-core-parent                (Spring Framework 7.x, Jakarta Persistence, Spring Data)
│   ├── m2-commons-parent         (spring-web, jackson-databind 3.x)
│   └── m2-selenium-parent        (Selenium 4.43, OpenTelemetry SDK 1.62, Netty, async-http-client)
└── m2-springboot-parent          (Spring Boot 4.0.6, Spring Cloud 2025.1.1, Spring Security 7.x)
    ├── m2-kafka-parent            (spring-kafka, Resilience4j)
    └── m2-webapp-parent           (SpringDoc 3, MapStruct 1.6, Cucumber 7, Serenity, Gatling 3.15)
        ├── m2-grpc-parent         (spring-grpc 1.0.3, grpc-services, WebFlux)
        ├── m2-batch-parent        (Spring Batch, Quartz)
        └── m2-quic-parent         (HTTP/3 via Netty QUIC 0.0.75, gRPC, WebFlux, BoringSSL)
```

Each level inherits and extends the one above it. Downstream projects pick the most specific parent that matches their tech stack (e.g. a Kafka consumer inherits `m2-kafka-parent`; a REST API inherits `m2-webapp-parent`).

## Versioning

- **Development version in source:** `0.0.1`
- **Released versions:** CalVer `YYYY.M.R` — `R=1` on the 1st of the month, `R=2` on the 15th
- The `publish.yml` workflow bumps the version with the Versions Maven Plugin, commits, deploys, creates a GitHub Release with the SBOM attached, then generates a SLSA provenance attestation

## Security Conventions

This is a security-sensitive repository because every CVE fixed or introduced here propagates to all downstream consumers.

**When adding or updating a dependency:**
- Always document the reason inline with a comment: CVE ID, CVSS score, and what fixed it.
- When a transitive dependency carries a CVE that can be patched by pinning it in `<dependencyManagement>`, do so and add a comment explaining the override.
- Example pattern used throughout the codebase:
  ```xml
  <!-- Override spring-web to patch CVE-2026-22735 (CVSS 7.5), fixed in 7.0.7 -->
  <dependency>
      <groupId>org.springframework</groupId>
      <artifactId>spring-web</artifactId>
      <version>7.0.7</version>
  </dependency>
  ```
- If a CVE cannot be fixed (e.g. a shaded internal copy), add a suppression entry in `.github/owasp-suppressions.xml` with a full explanation of why the risk is accepted and when to revisit.
- The OWASP Dependency Check is configured to fail the build on CVSS ≥ 7.

**Two Jackson families are in use:**
- `tools.jackson.core` (3.x) — the new groupId used by Spring Boot 4.x
- `com.fasterxml.jackson.core` (2.x) — still pulled in transitively by some libraries (springdoc, Serenity)
Both need to be patched independently when a Jackson CVE lands.

## GitHub Workflows

| Workflow | Trigger | Purpose |
|---|---|---|
| `publish.yml` | Schedule (1st/15th) or manual | CalVer release to Maven Central + SBOM + SLSA |
| `java-analysis.yml` | PRs | SpotBugs, PMD, Checkstyle, JaCoCo, Semgrep SAST |
| `dependency-upgrade.yml` | Weekly Monday | Minor/patch bumps → PR with OWASP pre-check |
| `dependabot-auto-merge.yml` | Dependabot PRs | Auto-approve + squash-merge after checks pass |
| `dependabot-gate.yml` | Called by other workflows | Serializes Dependabot PRs — only the oldest open one runs checks |

The `release` Maven profile (activated by `-Prelease`) adds GPG signing, attaches sources, and routes deployment to Maven Central via the Sonatype Central Portal plugin instead of the GitHub Packages default.

## Static Analysis Configuration

All tools are configured to **not fail the build** (`failOnError=false`, `failOnViolation=false`) — they run in advisory mode and post annotations on PRs via GitHub Actions:
- **Checkstyle:** enforces Google Java Style (`google_checks.xml`)
- **SpotBugs:** `effort=Max`, `threshold=Low`
- **JaCoCo:** 70% line/branch coverage threshold (advisory at this level; child projects may tighten it)
- **Semgrep:** `p/java` + `p/owasp-top-ten` rulesets; SARIF uploaded to GitHub Security tab
