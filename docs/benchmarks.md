# Benchmarks and Comparison

## Scope
TSAR is a governance layer, not a full SAST. This document defines what
TSAR detects and where it complements dedicated tools.

## Detection Coverage
| Category | TSAR scanner | Typical SAST |
|---|---|---|
| Hardcoded secrets | Yes (20+ patterns + entropy) | Yes (rule-based, entropy) |
| SQL injection | Yes (string concat patterns) | Yes (dataflow) |
| Command injection | Yes (exec/shell patterns) | Yes (dataflow) |
| Path traversal | Yes (open + concat) | Yes (taint analysis) |
| SSRF | Yes (user input to HTTP client) | Yes (taint analysis) |
| Weak crypto | Yes (algorithm names) | Yes (multiple rules) |
| TLS bypass | Yes | Yes |
| Unsafe deserialization | Yes (pickle, yaml.load) | Yes |
| XSS | Partial (innerHTML, dangerous) | Yes (template-aware) |
| Business logic flaws | No | No (requires manual review) |
| Dataflow-taint analysis | No | Yes (some) |
| Semantic model checking | No | Yes (advanced tools) |

## Recommendation
Use TSAR **together with**:
- A full SAST (Semgrep, CodeQL, SonarQube).
- An SCA (Dependabot, Snyk, Trivy).
- A DAST (OWASP ZAP, Burp).
- A secret scanner at scale (TruffleHog, GitGuardian).

## TSAR Advantages
- Enforced at agent generation time, before code exists.
- Portable across 15 AI agents.
- Enforces governance, not just detection.
- Versioned, updatable, fail-closed.

## TSAR Limitations
- No deep dataflow analysis.
- No template-engine awareness.
- No runtime protection.
- Depends on pattern quality; broad rules reduce false negatives but may miss
  obfuscated patterns.
