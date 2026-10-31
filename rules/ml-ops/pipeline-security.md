# MLOps Pipeline Security

## Scope
Training pipelines, experiment tracking, model registries, feature stores,
serving infrastructure.

## Pipeline Isolation
- Each pipeline stage runs in an isolated container with a dedicated service account.
- No shared credentials across stages.
- Stages communicate via signed artifacts, not shared filesystems.
- Network egress restricted to allow-listed endpoints.

## Artifact Integrity
- Every artifact (dataset, model, config) hashed at creation (SHA-256).
- Hash verified before consumption.
- Artifacts stored in versioned, immutable registries.
- Lineage tracked: dataset -> training code -> hyperparameters -> model -> deployment.

## Secrets
- Data source credentials from KMS/Vault, injected at runtime.
- Never in pipeline YAML, notebook cells, or environment variables visible to logs.
- Rotate credentials per pipeline run where supported.

## Code and Dependencies
- Pinned dependency versions with lockfiles.
- Training code versioned in Git with signed commits.
- Container images signed (cosign) and scanned (Trivy, Grype).
- SBOM + AI-BOM attached to every build.

## Access Control
- RBAC on experiment tracker (MLflow, W&B, etc.).
- No anonymous read access to datasets or models.
- Audit log for all artifact reads, writes, and deletions.

## Forbidden
- Training on production data without masking.
- Loading model weights from unverified URLs.
- Running notebooks as root.
- Storing raw PII in experiment tracker params or metrics.
