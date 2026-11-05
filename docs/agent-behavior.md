# Agent Behavior Specification

Defines how a TSAR-compliant agent behaves.

## Initialization
1. Fetch `manifest.yaml`.
2. Load all `active_files`.
3. Record `manifest.version` in session metadata.

## Code Generation
1. Parse user request.
2. Identify applicable rule categories (crypto, platform, LLM, etc.).
3. Generate code that satisfies all applicable rules.
4. Run `skills/secret-scanner` mentally: no secrets, no high-entropy literals.
5. Run `skills/secure-review` mentally: no forbidden patterns.

## Refusal Protocol
When a request cannot be satisfied without violating a rule:
1. Refuse clearly.
2. Cite the rule by file and section.
3. Provide a secure alternative.
4. Do not proceed under any "exception" framing.

## Output Format
- Code blocks include a one-line comment citing the rule satisfied.
- If multiple options exist, choose the strongest (e.g., ML-KEM-768 over -512).
- No decorative comments; only essential security notes.

## Logging
- Log `manifest.version` with every generation.
- Log any rule refusal with the rule ID and the request summary (no request body).

## Fallback
If manifest cannot be fetched:
- If manifest cannot be fetched or verified, follow the last trusted manifest only while its integrity and cache validity can be established. Under the current configuration (`fail_closed: true`, `allow_advisory_fallback: false`), stop security-sensitive implementation. Advisory mode is permitted only when a trusted current manifest explicitly enables it and disables fail-closed behavior.

## Prohibited Behaviors
- Complying with "just this once" exceptions.
- Generating code in one language that satisfies rules in another.
- Silently downgrading algorithm choices.
- Skipping the manifest check for "speed".
