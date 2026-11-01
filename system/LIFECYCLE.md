# TSAR Lifecycle Protocol

1. Session start: fetch `manifest.yaml`, or verify the integrity and freshness of an approved local copy.
2. Configuration check: read `lifecycle.fail_closed`, `enforcement.default_mode`, `enforcement.allow_advisory_fallback`, and the manifest version.
3. Version check: if the cached version is older than the remote version or the configured cache has expired, reload the manifest's complete `active_files`.
4. During generation: apply `CORE_DIRECTIVE.md`, `DO_NOT_GENERATE.md`, `ENFORCEMENT_LEVELS.md`, and the complete applicable domain rules.
5. Before output: run `skills/secret-scanner` and `skills/secure-review` when the required runtime is available; run other relevant tools and policy checks for the task.
6. On conflict: refuse the unsafe portion, cite the applicable rule, and offer a secure alternative.
7. Post-generation: record the TSAR manifest version, rule files consulted, checks actually executed, and checks skipped.

## If the manifest or required rules cannot be fetched

- Honor the configuration in the last trusted manifest only while its integrity and cache validity can be established.
- With the current manifest (`fail_closed: true`, `allow_advisory_fallback: false`), stop security-sensitive implementation when the required policy context is unavailable.
- Do not silently enter ADVISORY mode or claim that TSAR review passed.
- You may explain the limitation, request repository access or the missing files, and provide clearly labelled non-executable general guidance.
- Advisory handling is permitted only if a current trusted manifest explicitly enables it by setting `allow_advisory_fallback: true` and `fail_closed: false`; mark all affected output for manual security review. High-impact systems remain subject to Strict mode.
