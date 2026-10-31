# AI Training Pipeline Security

## Data
- Provenance tracking for every dataset.
- Poisoning detection: statistical anomaly, label consistency, source reputation.
- PII removal and licensing verification before training.
- Dataset versioning and hashing.

## Training Environment
- Isolated compute with no outbound internet.
- Signed training code and dependencies.
- Reproducible builds with pinned seeds and versions.

## Model Artifacts
- Model hashing and signing (Sigstore/cosign).
- SBOM + AI-BOM attached to every release.
- Access control on model registry; no public read unless intended.

## Forbidden
- Training on unvetted scraped data without filtering.
- Loading model weights from unverified sources.
- Retaining raw PII in training checkpoints.
