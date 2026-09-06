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
| **Releases**        | [CalVer releases](https://github.com/sajeth/m2-java-parent/releases) (1st & 15th)                              |

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

## Security

Only the latest published version of each parent is supported. Report vulnerabilities privately
via [GitHub Security Advisories](https://github.com/sajeth/m2-java-parent/security/advisories/new) — do not open a
public issue for security bugs. Details: [SECURITY.md](SECURITY.md).
