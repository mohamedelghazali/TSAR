# LLM09: Misinformation

## Risk
Model outputs may be factually wrong, confidently stated, or hallucinated.
Users relying on outputs for decisions face operational, legal, and safety
consequences.

## Controls
- Ground outputs in retrieved sources (RAG) with provenance.
- Cite sources for factual claims; refuse when no source supports the claim.
- Confidence indicators on outputs; flag low-confidence responses.
- Human review for high-stakes domains (medical, legal, financial, safety).
- Evaluation benchmarks on truthfulness, calibration, and refusal.
- Red-team probes for fabrication on key topics.

## High-Stakes Domains
| Domain | Control |
|---|---|
| Medical | Human review; cite guidelines |
| Legal | Human review; cite statute |
| Financial | Human review; cite data source |
| Safety | Deterministic rules only; no generative |
| Customer support | Cite knowledge base; escalate when uncertain |

## UI Patterns
- "This is AI-generated; verify before acting" banner on high-stakes answers.
- "Sources" section with clickable references.
- Feedback mechanism to flag errors.

## Testing
- Truthfulness benchmarks per domain.
- Hallucination probes with known-answer questions.
- Adversarial probes for confident wrong answers.

## Forbidden
- Presenting generated content as authoritative without sources.
- Generative models for safety-critical decisions.
- No human oversight for medical, legal, or financial outputs.
