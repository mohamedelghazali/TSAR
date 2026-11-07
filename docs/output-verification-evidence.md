# Output Verification and Compliance Evidence

## Purpose

The `output_verification.OutputGate` API evaluates actual changed files against named mandatory checks and emits a machine-readable evidence record. A task is returned as accepted only when every required check is present and has status `PASS`. Missing, failed, blocked, or not-run checks block acceptance. A skipped check is recorded with its reason and never converted to PASS.

## Evidence contents

Each `tsar/output-evidence/v1` record binds:
- task ID, UTC timestamp, agent/runtime and adapter version;
- immutable TSAR commit SHA, manifest version and SHA-256;
- hashes of loaded policy files, selected domains and claimed enforcement level;
- SHA-256 hashes of the actual changed files;
- check names, tool/version, status, exit code and optional artifact hash;
- required, skipped, missing and failed check lists;
- final PASS or BLOCKED decision and a canonical evidence digest.

Use `OutputGate.evaluate(..., output_path=...)` to write the record atomically. On BLOCKED, the evidence is written before `OutputGateError` is raised, so callers can inspect why acceptance was denied.

## Host integration requirements

1. Construct provenance only from the same immutable upstream snapshot used by preflight; never accept model-supplied hashes as trusted facts.
2. Obtain changed-file paths from the host's version-control diff and run scanners/tests against those exact files or the corresponding complete repository state.
3. Define mandatory check names in trusted host configuration. Do not let the model remove or downgrade required checks.
4. Populate each CheckResult from observed process execution, including real exit code, tool version and artifact digest where available.
5. Treat every exception, unavailable scanner, missing result, non-zero exit, or NOT_RUN status as a blocking outcome for required checks.
6. Persist evidence in a protected CI artifact or audit store. The JSON digest detects accidental or unauthorized edits only when compared with a trusted copy; it is not a digital signature or tamper-proof attestation.
7. Keep human review for logic, threat-model and scanner false-negative risks.

## Enforcement claim

This API is an E4 output-gate building block. It does not automatically intercept an agent's file writes, discover all changed files, run scanners, or enforce a merge rule by itself. An integration may claim E4 only after its real host path invokes the gate on every covered change, protects the required-check configuration and evidence destination, blocks acceptance on errors, and passes host-level bypass tests. Otherwise report the API as available but E4 as not yet enforced.

## Example

```python
gate = OutputGate(
    task_id=run_id,
    agent=agent_name,
    adapter_version=adapter_version,
    tsar_commit_sha=verified_commit_sha,
    manifest_version=verified_manifest_version,
    manifest_sha256=verified_manifest_sha256,
    policy_hashes=verified_loaded_policy_hashes,
    domains=selected_domains,
    enforcement_level="E4",
)
evidence = gate.evaluate(
    changed_files=git_changed_paths,
    checks=observed_check_results,
    required_checks={"secret-scan", "secure-review", "tests", "policy"},
    skipped=skipped_with_reasons,
    output_path=".tsar/evidence/output.json",
)
```

A PASS means the configured checks were observed to pass for the recorded files and provenance. It does not prove absence of all vulnerabilities.
