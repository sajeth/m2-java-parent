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
m2-java-parent                        (root — Java 25, Lombok, JaCoCo, Surefire, static-analysis plugins,
│                                       reproducible-build, license-report pluginManagement)
├── m2-core-parent                    (Spring Framework 7.x, Jakarta Persistence, Spring Data)
│   ├── m2-commons-parent             (spring-web, jackson-databind 3.x)
│   └── m2-selenium-parent            (Selenium 4.43, OpenTelemetry SDK 1.63, Netty, async-http-client)
└── m2-springboot-parent              (Spring Boot 4.0.6, Spring Cloud 2025.1.1, Spring Security 7.x)
    ├── m2-kafka-parent               (spring-kafka, Resilience4j)
    ├── m2-ai-parent                  (Spring AI 2.0.0-RC2: spring-ai-model, ChatClient autoconfigure)
    ├── m2-reactive-data-parent       (R2DBC, reactive Redis, reactive MongoDB, WebFlux)
    ├── m2-cloud-native-parent        (Spring Cloud Gateway, Config, Eureka, LoadBalancer, Circuit Breaker)
    ├── m2-native-parent              (GraalVM native-maven-plugin 0.10.6, AOT processing)
    ├── m2-testcontainers-parent      (Testcontainers BOM 1.21.1, @ServiceConnection, common containers)
    └── m2-webapp-parent              (SpringDoc 3, MapStruct 1.6, Cucumber 7, Serenity, Gatling 3.15)
        ├── m2-grpc-parent            (spring-grpc 1.0.3, grpc-services, WebFlux)
        ├── m2-batch-parent           (Spring Batch, Quartz)
        ├── m2-quic-parent            (HTTP/3 via Netty QUIC 0.0.75, gRPC, WebFlux, BoringSSL)
        ├── m2-soap-parent            (Spring WS, JAXB 4, WSS4J, Apache Santuario)
        ├── m2-websocket-parent       (spring-boot-starter-websocket, spring-security-messaging)
        └── m2-graphql-parent         (spring-boot-starter-graphql, graphql-java-extended-scalars)
```

Each level inherits and extends the one above it. Downstream projects pick the most specific parent that matches their tech stack (e.g. a Kafka consumer inherits `m2-kafka-parent`; a REST API inherits `m2-webapp-parent`; a cloud-native gateway inherits `m2-cloud-native-parent`).

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
- If a CVE cannot be fixed (e.g. a shaded internal copy), add a suppression entry in `.github/owasp-suppressions.xml` with a full explanation of why the risk is accepted and when to revisit. **Every suppression MUST include `until: YYYY-MM-DD` in the `<notes>` element** — the `stale-suppression-audit.yml` workflow opens a GitHub issue when a date is reached.
- The OWASP Dependency Check is configured to fail the build on CVSS ≥ 7.

**Two Jackson families are in use:**
- `tools.jackson.core` (3.x) — the new groupId used by Spring Boot 4.x
- `com.fasterxml.jackson.core` (2.x) — still pulled in transitively by some libraries (springdoc, Serenity)
Both need to be patched independently when a Jackson CVE lands.

## GitHub Workflows

| Workflow | Trigger | Purpose |
|---|---|---|
| `publish.yml` | Schedule (1st/15th) or manual | CalVer release to Maven Central + SBOM + SLSA |
| `release-on-merge.yml` | PR with `release` label merged to master | Triggers `publish.yml` for ad-hoc releases |
| `java-analysis.yml` | PRs | SpotBugs, PMD, Checkstyle, JaCoCo, OWASP, Semgrep SAST |
| `dependency-upgrade.yml` | Weekly Monday | Minor/patch bumps → PR with OWASP pre-check |
| `stale-suppression-audit.yml` | Weekly Monday | Checks `.github/owasp-suppressions.xml` for expired `until:` dates |
| `auto-merge.yml` | All PRs opened/updated | Auto-approve (Dependabot only) + enable squash auto-merge for all PRs |
| `dependabot-gate.yml` | Called by other workflows | Serializes Dependabot PRs — only the oldest open one runs checks |
| `pr-discussion.yml` | PR opened against master | Creates a GitHub Discussion linked to the PR |
| `cleanup-packages.yml` | After publish.yml | Prunes old GitHub Packages versions |
| `scorecard.yml` | Push to master + weekly | OpenSSF Scorecard supply-chain analysis |
| `qodana_code_quality.yml` | PRs + push to master | JetBrains Qodana static analysis |

The `release` Maven profile (activated by `-Prelease`) adds GPG signing, attaches sources, and routes deployment to Maven Central via the Sonatype Central Portal plugin instead of the GitHub Packages default.

## GitHub Discussions

Discussions are created automatically by `pr-discussion.yml` whenever a non-draft PR is opened against `master`. The label on the PR determines which Discussion category is used:

| PR Label | Discussion Category |
|---|---|
| `security` | Announcements |
| `feature`, `enhancement` | Ideas |
| `bug`, `fix` | Q&A |
| `ci` | Show and tell |
| `polls` | Polls |
| `dependency`, `chore` | *(skipped — no discussion created)* |
| *(anything else / no label)* | General |

**One-time repository setup:** Enable GitHub Discussions in repository Settings → General → Features, then create the following categories exactly as spelled: `Announcements`, `General`, `Ideas`, `Polls`, `Q&A`, `Show and tell`. The workflow falls back to `General` if a mapped category is missing.

## Wiki Maintenance

The repository wiki (`sajeth/m2-java-parent.wiki`) documents the POM hierarchy, version history, dependency rationale, and workflow design.

**When a PR is merged, update the wiki if the PR:**
- Adds, removes, or renames a parent POM module → update the POM Hierarchy page
- Changes the release schedule or versioning scheme → update the Versioning page
- Adds, removes, or significantly changes a workflow → update the Workflows page
- Adds a CVE override or suppression → update the Security / Dependency Overrides page
- Changes static-analysis rules or thresholds → update the Static Analysis page

To edit the wiki locally:
```bash
git clone https://github.com/sajeth/m2-java-parent.wiki.git /tmp/m2-wiki
cd /tmp/m2-wiki
# edit or create *.md files, then:
git add . && git commit -m "docs: update wiki — <summary>"
git push origin master
```

Wiki pages use GitHub-Flavored Markdown. The home page is `Home.md`; each top-level topic is a separate `*.md` file (e.g. `POM-Hierarchy.md`, `Versioning.md`, `Workflows.md`, `Security.md`, `Static-Analysis.md`).

## Maven Wrapper

Use `./mvnw` (Unix) or `mvnw.cmd` (Windows) instead of a system Maven to ensure consistent Maven version (3.9.9). The wrapper auto-downloads Maven on first use to `~/.m2/wrapper/dists/`.

```bash
./mvnw install          # same as: mvn install
./mvnw verify           # same as: mvn verify
```

## Dev Container

`.devcontainer/devcontainer.json` provides a pre-configured environment with Java 25 (Temurin), Maven 3.9.9, GitHub CLI, and actionlint. Open in VS Code with the Dev Containers extension or on GitHub Codespaces.

## Reproducible Builds

`project.build.outputTimestamp` is set in the root POM so that Maven produces byte-identical JARs and POMs from the same source tree. The `maven-artifact-plugin:buildinfo` goal records build metadata to `target.nosync/*.buildinfo` on every `verify` run.

The `license-maven-plugin` (configured in root `pluginManagement`) can generate a `THIRD-PARTY.txt` listing transitive dependency licenses:

```bash
mvn org.codehaus.mojo:license-maven-plugin:aggregate-add-third-party -DskipTests
```

## Static Analysis Configuration

All tools are configured to **not fail the build** (`failOnError=false`, `failOnViolation=false`) — they run in advisory mode and post annotations on PRs via GitHub Actions:
- **Checkstyle:** enforces Google Java Style (`google_checks.xml`)
- **SpotBugs:** `effort=Max`, `threshold=Low`
- **JaCoCo:** 70% line/branch coverage threshold (advisory at this level; child projects may tighten it)
- **Semgrep:** `p/java` + `p/owasp-top-ten` rulesets; SARIF uploaded to GitHub Security tab
