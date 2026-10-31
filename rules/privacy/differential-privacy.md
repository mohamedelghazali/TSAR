# Differential Privacy

## When to Use
- Aggregate statistics on sensitive populations.
- Machine learning on personal data.
- Public dashboards with demographic breakdowns.

## Parameters
| Use Case | Epsilon | Notes |
|---|---|---|
| Public release | <= 1.0 | Strong privacy |
| Internal analytics | <= 3.0 | Balanced |
| Model training | <= 8.0 | Utility-focused |

## Mechanisms
- Laplace for numeric queries.
- Gaussian for high-dimensional or (epsilon, delta) guarantees.
- Exponential for categorical selection.

## Composition
- Track privacy budget per user per period.
- Sequential composition: sum of epsilons.
- Parallel composition: max of epsilons per disjoint subset.
- Advanced composition for many queries; use a privacy accountant.

## Implementation
- Use vetted libraries: OpenDP, Google DP, Opacus (PyTorch).
- Never implement mechanisms manually.
- Test with membership inference attacks.

## Forbidden
- Releasing DP results without tracking budget.
- Reusing the same randomness across queries.
- Epsilon > 10 without explicit approval.
