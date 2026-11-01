---
name: secure-review
description: Run a lightweight regex-based static review for selected unsafe code patterns, including injection sinks, unsafe deserialization, HTML injection, selected SSRF/path patterns, disabled TLS verification, weak crypto identifiers, and weak random-number calls. Use as an initial heuristic check, not as a complete security audit.
---

# Secure Review Skill

## Purpose
Perform a fast, pattern-based review of source files before output or commit. Findings require contextual human review; the scanner can produce false positives and false negatives.

## Invocation
`python skills/secure-review/review.py <file-or-directory>`

## Checks implemented by the current script
- SQL injection patterns involving interpolated or concatenated query arguments.
- Command-injection patterns involving selected process-execution APIs and concatenation.
- Calls to `eval()`.
- `pickle.load(s)` usage.
- Selected unsafe `yaml.load()` call patterns.
- Assignments to `innerHTML` and use of `dangerouslySetInnerHTML`.
- Selected SSRF patterns where `requests.get`, `fetch`, or `axios.get` receives an argument beginning with `req.`, `request.`, or `params.`.
- Selected path-traversal patterns involving concatenation or interpolation in `open()`.
- Disabled TLS verification patterns, including `verify=False`, `InsecureSkipVerify: true`, and `rejectUnauthorized: false`.
- Weak-cryptography identifiers (MD5, SHA-1, DES, RC4, ECB) and selected non-cryptographic random-number calls.

The script does not scan for hardcoded secrets and does not invoke `secret-scanner`. Run `skills/secret-scanner/scanner.py` separately for its supported credential patterns.

## Action
- Exit with status 1 when one or more HIGH findings are detected.
- Report file, line, category, severity, and remediation hint.
- Treat this as an initial heuristic check only; it is not a complete SAST engine, penetration test, or proof of security.
