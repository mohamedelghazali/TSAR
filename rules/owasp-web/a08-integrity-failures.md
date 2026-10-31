# A08: Software and Data Integrity Failures

## Controls
- Signed releases and artifacts (Sigstore/cosign).
- Subresource Integrity (SRI) for third-party scripts.
- Deserialization of untrusted data forbidden; use safe formats (JSON with schema).
- CI/CD pipelines isolated with least-privilege service accounts.
- Deployment artifacts verified before execution.

## Forbidden
- \`pickle.loads\`, \`yaml.load\` (unsafe), \`marshal.loads\` on untrusted data.
- Unsigned container images in production.
