# Secret Scanner Skill

## Purpose
Scan generated code for hardcoded secrets before output.

## Invocation
`python skills/secret-scanner/scanner.py <path>`

## Detections
- Cloud provider keys (AWS, GCP, Azure).
- LLM and SaaS tokens (OpenAI, Anthropic, Stripe, GitHub).
- Private key blocks.
- High-entropy strings (Shannon > 4.5) in assignment contexts.
- Connection strings with embedded credentials.

## Action
- BLOCK output.
- Replace with secret-manager reference or environment variable.
- Report file, line, and pattern class (never the secret value).
