# m2-java-parent

Maven **parent POM** hierarchy for **Java 25** projects — Spring Boot, Spring Cloud, gRPC, Kafka, and related stacks.

There is no application source in this repository. Artifacts are published as `io.github.sajeth:*` parent POMs
to [GitHub Packages](https://github.com/sajeth/m2-java-parent/packages).

## About

|                     |                                                                                                                |
|---------------------|----------------------------------------------------------------------------------------------------------------|
| **License**         | [Apache-2.0](LICENSE)                                                                                          |
| **Security policy** | [SECURITY.md](SECURITY.md) · [Advisory form](https://github.com/sajeth/m2-java-parent/security/advisories/new) |
| **Activity**        | [Recent activity](https://github.com/sajeth/m2-java-parent/activity)                                           |
| **Wiki**            | [Documentation wiki](https://github.com/sajeth/m2-java-parent/wiki)                                            |
| **Releases**        | [CalVer releases](https://github.com/sajeth/m2-java-parent/releases) (weekly, Mondays)                         |

## Hierarchy (summary)

```
m2-java-parent
├── m2-core-parent → m2-commons-parent, m2-selenium-parent
└── m2-springboot-parent
    ├── m2-kafka-parent, m2-ai-parent, m2-reactive-data-parent
    ├── m2-cloud-native-parent, m2-native-parent, m2-testcontainers-parent
    └── m2-webapp-parent → grpc, batch, quic, soap, websocket, graphql
```

Full module map: [Wiki · POM Hierarchy](https://github.com/sajeth/m2-java-parent/wiki/POM-Hierarchy).

## Consume

```xml
<parent>
  <groupId>io.github.sajeth</groupId>
  <artifactId>m2-commons-parent</artifactId>
  <version>YYYY.M.R</version>
</parent>
```

See [Wiki · Consuming Parents](https://github.com/sajeth/m2-java-parent/wiki/Consuming-Parents).

## Jackson (Boot 4 / tools.jackson)

`m2-springboot-parent` owns Jackson versions for all Boot apps:

| Family | BOM / pin | Notes |
|--------|-----------|--------|
| Jackson 3 | `tools.jackson:jackson-bom` (`jackson.version`) | databind/core/dataformat under `tools.jackson.*` |
| Annotations | `com.fasterxml.jackson.core:jackson-annotations` **2.22+** | Shared with Jackson 3; required for `JsonApplyView` |
| Jackson 2 leftovers | `com.fasterxml.jackson:jackson-bom` (`fasterxml.jackson.version`) | Versions only for transitive springdoc/Serenity/jjwt |

Fat jars exclude `com.fasterxml.jackson.core:jackson-databind` / `jackson-core` via
`spring-boot-maven-plugin` so apps do not dual-ship Jackson 2+3. **Do not** re-pin
`jackson-annotations` or re-add those fat-jar excludes in application POMs.

## Security

Only the latest published version of each parent is supported. Report vulnerabilities privately
via [GitHub Security Advisories](https://github.com/sajeth/m2-java-parent/security/advisories/new) — do not open a
public issue for security bugs. Details: [SECURITY.md](SECURITY.md).
