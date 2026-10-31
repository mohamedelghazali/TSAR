# TSAR Lifecycle Protocol

1. Session start: fetch `manifest.yaml`.
2. Version check: if cached < remote, reload all `active_files`.
3. During generation: apply `CORE_DIRECTIVE.md` and relevant `rules/`.
4. Before output: run `skills/secret-scanner` and `skills/secure-review`.
5. On conflict: refuse, cite rule, offer secure alternative.
6. Post-generation: log TSAR version used.

If remote fetch fails:
- Enter ADVISORY mode.
- Mark output "requires manual security review".
- Do not silently fall back to unsafe defaults.
