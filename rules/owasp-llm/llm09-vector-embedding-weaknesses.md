# LLM09: Vector and Embedding Weaknesses

## Risk
Weaknesses in embedding generation, vector storage, indexing, retrieval, or tenant isolation can enable data leakage, cross-tenant retrieval, poisoned context, unauthorized access, and manipulation of model responses.

## Controls
- Enforce authorization before retrieval; never rely on similarity scores as access control.
- Apply tenant and document-level isolation to vector records and metadata filters.
- Authenticate and encrypt vector database traffic and storage.
- Validate and scan ingestion sources; preserve provenance and content hashes.
- Restrict who can add, update, delete, export, or rebuild embeddings and indexes.
- Version embedding models, preprocessing, chunking, and index configuration.
- Detect anomalous ingestion, duplicate poisoning patterns, and unexpected index changes.
- Prevent sensitive data from entering embeddings unless explicitly approved.
- Apply deletion and retention controls to source documents, chunks, and derived vectors.
- Test retrieval against cross-tenant and unauthorized-document probes.

## Testing
- Attempt cross-tenant nearest-neighbor retrieval.
- Inject poisoned or adversarial documents and measure retrieval influence.
- Verify document revocation and deletion propagate to vectors and caches.
- Test metadata-filter bypass, index tampering, and embedding-version drift.

## Forbidden
- Treating vector similarity as an authorization decision.
- Shared indexes without enforceable tenant isolation.
- Unauthenticated vector-store access or unrestricted index mutation.
- Ingestion without provenance, validation, and deletion lifecycle controls.
