# Serverless / Edge Security

## Functions
- Least-privilege IAM per function.
- No secrets in environment variables; use secret manager references.
- Timeout and memory limits enforced.
- Egress restricted to allow-list.

## Edge
- Signed edge logic; no unsigned dynamic code.
- Per-request isolation where possible.
- Cache keys include tenant identity to prevent cross-tenant leakage.

## Supply Chain
- Pinned runtimes and dependencies.
- SBOM per function bundle.
