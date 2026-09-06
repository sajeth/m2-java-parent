# Consuming parents

Add a GitHub Packages repository that can read `m2-java-parent`, then inherit the parent that matches your stack:

```xml
<parent>
  <groupId>io.github.sajeth</groupId>
  <artifactId>m2-commons-parent</artifactId>
  <version>YYYY.M.R</version>
</parent>
```

| Parent | Use when |
|--------|----------|
| `m2-commons-parent` | Shared libraries (no Spring Boot) |
| `m2-springboot-parent` | Spring Boot apps |
| `m2-webapp-parent` | HTTP / OpenAPI / resilience web apps |
| `m2-kafka-parent` | Kafka producers/consumers |
| `m2-grpc-parent` | gRPC services |
| `m2-quic-parent` | HTTP/3 / QUIC |

Pin to a published CalVer version from [Releases](https://github.com/sajeth/m2-java-parent/releases). Prefer the latest supported release for security fixes.
