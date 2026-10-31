# Fuzzing

## Targets
- Parsers (JSON, XML, protobuf, YAML, binary formats).
- Protocol handlers (HTTP, gRPC, WebSocket).
- Crypto implementations (via test vectors and differential fuzzing).
- Authentication flows.

## Tools
- AFL++, libFuzzer, honggfuzz for native code.
- Atheris for Python, jazzer for Java, go-fuzz for Go.
- RESTler for REST APIs, GraphQLer for GraphQL.

## Coverage
- Minimum 70% line coverage on fuzz targets.
- Corpus maintained and minimized.
- Regression corpus for every found bug.

## Continuous Fuzzing
- OSS-Fuzz for open source.
- ClusterFuzzLite in CI for projects.
- Long-running fuzzers for high-value targets.

## Triage
- Crashes reproducible with the provided input.
- Security impact assessed.
- Fix + regression test in the corpus.

## Forbidden
- Fuzzing without sanitizers (ASan, UBSan, MSan).
- Ignoring crashes without investigation.
