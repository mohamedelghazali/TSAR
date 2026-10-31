# LLM05: Data and Model Poisoning

## Risk
Malicious or corrupted data in training, fine-tuning, or RAG can alter model
behavior, introduce backdoors, or degrade safety.

## Controls
- Provenance tracking for every dataset: source, author, timestamp, hash.
- Source reputation scoring; allow-list of vetted sources.
- Statistical anomaly detection on dataset distribution before training.
- Label consistency checks; human review for edge cases.
- Differential testing: compare new model against baseline on safety benchmarks.
- RAG ingestion filtering: strip instructions, reject binary blobs, sanitize HTML/JS.
- Model artifact signing; verify before load.

## Detection
- Trigger-based backdoor probes (rare tokens, specific phrases).
- Embedding distribution drift detection.
- Benchmark regression on safety and truthfulness.
- Red-team evaluation before deployment.

## Response
- Quarantine suspect data and models.
- Roll back to last known-good checkpoint.
- Investigate source; update allow-list.
- Notify downstream consumers if a deployed model is affected.

## Forbidden
- Training on unvetted scraped data without filtering.
- Loading model weights from unverified sources.
- Deploying fine-tuned models without safety evaluation.
- Sharing poisoned datasets downstream.
