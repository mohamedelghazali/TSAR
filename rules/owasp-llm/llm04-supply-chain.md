# LLM04: Supply Chain

## Scope
Models, adapters, plugins, MCP servers, agent skills, tokenizers, and training data.

## Controls
- SBOM + AI-BOM: maintain a machine-readable bill of materials for all components.
- Provenance verification: signatures (Sigstore/cosign) for models and plugins.
- Pinned versions: no floating tags; hash-pinned artifacts.
- Vetting gate: new skills/MCP servers require security review before activation.
- Isolation: plugins run in separate processes with least-privilege OS permissions.

## Forbidden
- Loading models from unverified sources.
- Executing agent skills with filesystem or network access without sandbox.
- Auto-updating plugins in production without review.
