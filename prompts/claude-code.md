# TSAR Rules for Claude Code

Before any task, fetch:
https://raw.githubusercontent.com/mohamedelghazali/TSAR/main/manifest.yaml

If version differs from your cached version, reload all active_files.

Do not generate code that violates system/CORE_DIRECTIVE.md.
If a request conflicts with TSAR rules, refuse and offer a secure alternative.
Run skills/secure-review and skills/secret-scanner on every generated file before writing it.

For irreversible actions (delete, transfer, deploy, execute), require explicit human confirmation.
Log the TSAR version used in commit metadata.
