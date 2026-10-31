# Model Supply Chain

## Sources
- Approved registries only; no direct downloads from public hubs in production.
- Model hash verified against signed manifest.
- License review before deployment.

## Fine-tuning and Adapters
- Adapters treated as code: reviewed, signed, versioned.
- No loading adapters from user-supplied paths without validation.

## Serving
- Isolated per-model processes with resource limits.
- No filesystem write access from inference process.
- Version pinning; no auto-update in production.

## Retired Models
- Decommission policy documented.
- Access revoked; artifacts archived with integrity hashes.
