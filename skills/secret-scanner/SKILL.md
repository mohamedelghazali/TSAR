---
name: secret-scanner
description: Run heuristic pattern matching for selected credentials, private-key markers, credential-bearing URLs, JWT-like strings, and high-entropy token-like values in credential-labelled lines. Use before sharing code or reviewing repositories for accidentally exposed secrets; this is not exhaustive secret detection.
---

# Secret Scanner Skill

## Purpose
Detect selected secret-like values in source code and generated files. The scanner is pattern-based and may miss credentials that do not match its supported patterns.

## Invocation
`python skills/secret-scanner/scanner.py <file-or-directory>`

## Detections implemented by the current script
- AWS access-key identifiers matching the configured `AKIA...` pattern.
- OpenAI-style and Anthropic-style API key patterns.
- GitHub classic personal access tokens matching the configured `ghp_...` pattern.
- Google API keys matching the configured `AIza...` pattern.
- Stripe live secret keys matching the configured `sk_live_...` pattern.
- RSA, EC, and OpenSSH private-key PEM header markers.
- Connection strings containing embedded username/password credentials.
- JWT-like three-part strings matching the configured pattern.
- High-entropy token-like strings on lines containing credential-related labels such as secret, token, API key, password, credential, or authorization.

## Action
- Exit with status 1 when findings are detected.
- Report file, line, and pattern class; never print the matched secret value.
- Replace exposed credentials with secret-manager references or environment-variable injection, and rotate/revoke any credential that may have been exposed.
- Do not interpret a clean scan as proof that no secrets exist; use additional scanners and manual review where appropriate.
