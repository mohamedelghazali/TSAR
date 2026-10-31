# Contributing to TSAR

## Adding a Rule
1. Place the rule in the correct `rules/` subdirectory.
2. Reference it in `manifest.yaml` under the appropriate group.
3. Add required sections to `scripts/lint_rules.py` (REQUIRED_SECTIONS) if it is a core file.
4. Run `python scripts/lint_rules.py` locally; it must pass.
5. Open a PR; CI must pass before merge.

## Adding a Prompt File
1. Create `prompts/<agent>.md` following the shape of existing files.
2. Reference the manifest URL and CORE_DIRECTIVE.md.
3. Add the agent name to README.md supported list.

## Style
- English only.
- Comments: only when they explain non-obvious security reasoning.
- No Arabic, no emojis, no decorative text.
- Tables for enumerable rules; prose for rationale.

## Security Issues
Report vulnerabilities privately per SECURITY.md. Do not open public issues for exploitable findings.
