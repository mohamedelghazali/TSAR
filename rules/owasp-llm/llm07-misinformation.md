# LLM07: Misinformation

## Risk
Model outputs can be false, fabricated, stale, or expressed with unjustified confidence. Incorrect outputs can cause operational, legal, financial, medical, or safety harm.

## Controls
- Ground factual answers in authoritative, current sources where available.
- Preserve source provenance and distinguish retrieved facts from model inference.
- Require citations for externally verifiable claims in supported workflows.
- Communicate uncertainty; do not fabricate citations, quotes, or source details.
- Escalate high-impact decisions to qualified human review.
- Evaluate truthfulness, calibration, refusal behavior, and source faithfulness.
- Provide correction and feedback paths and retain review evidence.

## High-Impact Domains
| Domain | Minimum Safeguard |
|---|---|
| Medical | Qualified professional review |
| Legal | Jurisdiction-specific legal review |
| Financial | Verified data and authorized review |
| Safety-critical | Deterministic controls and accountable approval |
| Customer support | Grounding in approved knowledge sources |

## Testing
- Run known-answer and adversarial hallucination evaluations.
- Verify citations resolve and support the associated claims.
- Test stale, conflicting, and missing source conditions.
- Measure calibration and abstention when evidence is insufficient.

## Forbidden
- Invented citations or fabricated evidence.
- Presenting uncertain generated content as verified fact.
- Autonomous high-impact decisions without accountable oversight.
