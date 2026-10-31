# Contributing to TSAR

## Language and Style
- **English only.** No emojis, no decorative text.
- **Comments**: only when explaining non-obvious security reasoning.
- **Tables** for enumerable rules; prose for rationale.
- **Consistent heading levels**; no skipped levels.

## Repository Structure
```
system/         — core policy
rules/          — 37 domains
skills/         — runnable scanners
tools/          — CLI, orchestrator, LSP, web, report
integrations/   — CI/CD templates
prompts/        — 15 agents
docs/           — guides, compliance, architecture
examples/       — secure and anti-pattern code
tests/          — pytest suite
policies/       — OPA/Cedar
scripts/        — automation
```

## Adding a Rule

1. Choose the correct domain under `rules/`.
2. Create `rules/<domain>/<name>.md` with:
   - Title
   - Risk description (one paragraph)
   - `## Controls` (bullet list of must-dos)
   - `## Forbidden` (bullet list of must-nots)
   - `## Testing` (how to verify)
3. Reference the file in `manifest.yaml` under `active_files`.
4. Add a test in `tests/test_<domain>_rules.py`.
5. Run `python scripts/lint_rules.py`.
6. Run `pytest tests/`.
7. Open a PR with the `rule-addition` label.

## Adding a Skill

1. Create `skills/<name>/SKILL.md` documenting purpose, invocation, detections, actions.
2. Implement the script (`<name>.py` or equivalent).
3. Add a test in `tests/test_skills.py`.
4. Reference in `docs/`.
5. Open a PR.

## Adding an Agent Prompt

1. Create `prompts/<agent>.md` following existing patterns.
2. Reference the manifest URL and `CORE_DIRECTIVE.md`.
3. Add to `docs/agent-compatibility-matrix.md`.
4. Add to `tools/tsar-cli/tsar.py` in `--agent` choices.
5. Update `README.md`.
6. Open a PR.

## Adding a Compliance Mapping

1. Create `docs/compliance/<framework>.md`.
2. Reference only existing files in `rules/`.
3. Add to `docs/compliance/README.md`.
4. Add to `tests/test_compliance_docs.py` FRAMEWORKS list.
5. Run `pytest tests/test_compliance_docs.py`.
6. Open a PR.

## Adding an Integration

1. Create `integrations/<platform>/<file>`.
2. Document in `docs/ci-cd.md`.
3. Test in a sample repository before merging.
4. Add a note about fail-closed behavior.

## Code Contributions

- All Python scripts require tests.
- All tests must pass in CI.
- No new dependencies without discussion.
- Follow existing patterns for style and structure.

## Commit Messages

Follow Conventional Commits:
```
feat(scope): description
fix(scope): description
docs(scope): description
chore(scope): description
test(scope): description
```

## Review Process

- Rule changes require one maintainer review.
- Core policy changes require two.
- Security-sensitive changes require a security reviewer.
- All PRs must pass CI.

## Testing Requirements

Every PR must:
- Pass `pytest tests/`.
- Pass `python scripts/lint_rules.py`.
- Pass the orchestrator (`python tools/tsar-orchestrator/orchestrator.py examples/secure`).
- Not introduce secrets (checked by secret-scanner).
- Not introduce HIGH findings (checked by secure-review).

## Contributor Licensing

By submitting a contribution, you confirm that you have the right to submit it
and agree to the contribution license grant described in the repository
`LICENSE`. You retain copyright ownership; no copyright assignment is implied.
Do not submit third-party material unless its license permits inclusion under
the project's licensing terms. A separate written agreement controls where one
exists.

The project uses a custom source-available license. It is not an OSI-approved
Open Source license. Commercial use requires prior written authorization and a
separate commercial license. Review `LICENSE` before contributing.

## Reporting Security Issues

See `SECURITY.md`. Do not open public issues for exploitable findings.
