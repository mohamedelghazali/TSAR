# Rule Authoring Guide

## Anatomy of a Rule File
1. **Title** — the category or CWE it addresses.
2. **Risk** — one paragraph on the threat.
3. **Controls** — bullet list of must-do items.
4. **Forbidden** — bullet list of must-not-do items.
5. **Testing** — how to verify compliance.

## Naming
- Path: `rules/<domain>/<identifier>.md`
- Identifier: lowercase, hyphenated, stable.
- Never rename an identifier; add a new one.

## Machine-Checkable Sections
If the rule maps to a scanner pattern, add a `## Scanner Pattern` section
with the regex or AST check. The `secure-review` skill loads these.

## Review Checklist
- [ ] Addresses a known CWE or OWASP category.
- [ ] Contains at least one Forbidden item.
- [ ] Contains at least one Testing item.
- [ ] Referenced by `manifest.yaml`.
- [ ] Has a corresponding test in `tests/`.

## Deprecation
- Mark deprecated rules with `status: deprecated` in a YAML front-matter block.
- Keep the file for 12 months.
- Update `manifest.yaml` to drop it from `active_files`.
- Update `scripts/lint_rules.py` to allow the file to remain.
