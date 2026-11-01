---
name: secure-review
description: Perform static security review of source code for injection, path traversal, SSRF, unsafe deserialization, XSS, weak cryptography, and hardcoded secrets. Use when reviewing, generating, or modifying application code and security-sensitive changes.
---

# Secure Review Skill

## Purpose
Static analysis of generated code before output.

## Invocation
`python skills/secure-review/review.py <path>`

## Checks
- SQL injection (string concatenation into query).
- Command injection (shell exec with user input).
- Path traversal (`../` in file paths).
- SSRF (URL fetched from user input without allow-list).
- Unsafe deserialization (`pickle`, `yaml.load`, `eval`).
- XSS (unsanitized innerHTML / dangerouslySetInnerHTML).
- Weak crypto (MD5, SHA1, ECB).
- Hardcoded secrets (delegates to secret-scanner).

## Action
- BLOCK output on any HIGH finding.
- Report file, line, category, remediation hint.
