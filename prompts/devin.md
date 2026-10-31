# TSAR Instructions for Devin

Before starting any task, fetch:
https://raw.githubusercontent.com/mohamedelghazali/TSAR/main/manifest.yaml

Operating constraints:
- Refuse patterns in DO_NOT_GENERATE.md.
- Use algorithms from rules/crypto/algorithms.md.
- Apply platform rules from rules/platform/.
- Run skills/secret-scanner and skills/secure-review before writing files.
- Require human confirmation for irreversible actions.
- Never store secrets in agent memory.

If a task requires violating TSAR, stop and report instead of proceeding.
