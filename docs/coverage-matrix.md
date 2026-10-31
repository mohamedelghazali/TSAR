# TSAR Coverage Matrix

## By Platform
| Platform | Rules | Examples | Tests |
|---|---|---|---|
| Web | rules/platform/web.md, rules/owasp-web/ | examples/secure/node/ | test_scanners.py |
| iOS | rules/platform/mobile-ios.md | — | — |
| Android | rules/platform/mobile-android.md | — | — |
| Desktop | rules/platform/desktop.md | — | — |
| Embedded | rules/platform/embedded-firmware.md | — | — |
| Kubernetes | rules/platform/kubernetes.md | — | — |
| IoT | rules/platform/iot.md | — | — |
| Serverless | rules/platform/serverless-edge.md | — | — |
| Distributed | rules/platform/distributed-systems.md | — | — |

## By Language
| Language | Secure example | Scanners apply |
|---|---|---|
| Python | examples/secure/python/ | yes |
| Node.js | examples/secure/node/ | yes |
| Go | examples/secure/go/ | yes |
| Rust | examples/secure/rust/ | yes |
| Java | — | yes |
| Swift | — | yes |
| Kotlin | — | yes |

## By Threat Category
| Category | Rules | Scanner rule |
|---|---|---|
| Injection | A03, LLM01 | sql_injection, command_injection, eval_usage |
| Broken Auth | A01, A07 | — |
| Crypto Failure | A02, rules/crypto/ | weak_crypto, weak_random |
| SSRF | A10 | ssrf |
| Supply Chain | A06, LLM04 | — |
| Agentic | LLM03, agentic-ai/ | — |
| Hardware | rules/hardware/ | — |
