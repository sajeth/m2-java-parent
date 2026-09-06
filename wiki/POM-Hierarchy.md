# POM hierarchy

```
m2-java-parent                        (Java 25, Lombok, JaCoCo, Surefire, static analysis)
├── m2-core-parent                    (Spring Framework, Jakarta Persistence, Spring Data)
│   ├── m2-commons-parent             (spring-web, jackson-databind 3.x)
│   └── m2-selenium-parent            (Selenium, OpenTelemetry, Netty)
└── m2-springboot-parent              (Spring Boot, Spring Cloud, Spring Security)
    ├── m2-kafka-parent
    ├── m2-ai-parent
    ├── m2-reactive-data-parent
    ├── m2-cloud-native-parent
    ├── m2-native-parent
    ├── m2-testcontainers-parent
    └── m2-webapp-parent
        ├── m2-grpc-parent
        ├── m2-batch-parent
        ├── m2-quic-parent
        ├── m2-soap-parent
        ├── m2-websocket-parent
        └── m2-graphql-parent
```

All modules use `<packaging>pom</packaging>` and publish to GitHub Packages under `io.github.sajeth`.
