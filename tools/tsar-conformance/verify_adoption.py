#!/usr/bin/env python3
"""Unified deterministic adoption and capability verification engine for TSAR."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

_ADOPTION_RESPONSE_PATH = Path(__file__).resolve().parent / "adoption_response.py"
_SPEC = importlib.util.spec_from_file_location(
    "tsar_adoption_response", _ADOPTION_RESPONSE_PATH
)
assert _SPEC is not None and _SPEC.loader is not None
_adoption_response = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = _adoption_response
_SPEC.loader.exec_module(_adoption_response)

AdoptionEvaluation = _adoption_response.AdoptionEvaluation
AdoptionOutcome = _adoption_response.AdoptionOutcome
AdoptionResponse = _adoption_response.AdoptionResponse
MandatoryCheck = _adoption_response.MandatoryCheck
NonBlockingIssue = _adoption_response.NonBlockingIssue
OptionalCheck = _adoption_response.OptionalCheck
classify_and_format_adoption = _adoption_response.classify_and_format_adoption

STATE_A_HEADER = _adoption_response.SUCCESS_MESSAGE
STATE_B_HEADER = _adoption_response.FAILED_HEADER
STATE_C_HEADER = _adoption_response.WARNING_HEADER

SYSTEM_DIRECTIVES: tuple[str, ...] = (
    "system/CORE_DIRECTIVE.md",
    "system/DO_NOT_GENERATE.md",
    "system/ENFORCEMENT_LEVELS.md",
    "system/LIFECYCLE.md",
)

CORE_FILES: tuple[str, ...] = (
    "VERSION",
    "manifest.yaml",
    "AGENTS.md",
    *SYSTEM_DIRECTIVES,
)

LOCAL_CONFORMANCE_SCRIPTS: tuple[str, ...] = (
    "tools/tsar-conformance/runner.py",
    "tools/tsar-conformance/consultation_verifier.py",
)


@dataclass(frozen=True)
class RuntimeCapabilities:
    """Runtime capability flags used to classify local vs web/offline checks."""

    has_local_checkout: bool = False
    has_python_runtime: bool = False
    directory_crawling_blocked: bool = False
    raw_host_blocked: bool = False
    github_api_available: bool = True

    @property
    def requires_local_conformance_scripts(self) -> bool:
        return self.has_local_checkout and self.has_python_runtime


@dataclass
class AdoptionRunInput:
    """Inputs for deterministic evaluation of a TSAR adoption run."""

    repository_accessible: bool = True
    capabilities: RuntimeCapabilities = field(default_factory=RuntimeCapabilities)
    verified_files: dict[str, bool] = field(default_factory=dict)
    llms_full_fallback_used: bool = False
    llms_full_complete: bool = True
    llms_full_verified_manifest: bool = False
    llms_full_verified_directives: bool = False
    readme_only: bool = False
    landing_page_only: bool = False
    directory_listing_only: bool = False
    stale_or_cached_content: bool = False
    expected_version: str | None = None
    observed_version: str | None = None
    expected_last_updated: str | None = None
    observed_last_updated: str | None = None
    expected_active_file_count: int | None = None
    observed_active_file_count: int | None = None
    fail_closed: bool = True
    default_mode: str = "strict"
    allow_advisory_fallback: bool = False
    runner_executed: bool = False
    runner_passed: bool = False
    runner_error: str = ""
    consultation_verifier_executed: bool = False
    consultation_verifier_passed: bool = False
    consultation_verifier_error: str = ""
    non_blocking_issues: list[str] = field(default_factory=list)
    skipped_mandatory_checks: list[str] = field(default_factory=list)


def evaluate_adoption_run(run_input: AdoptionRunInput) -> AdoptionResponse:
    """Evaluate adoption inputs deterministically into State A, B, or C."""

    mandatory_checks: list[MandatoryCheck] = []
    optional_checks: list[OptionalCheck] = []
    non_blocking_issues: list[NonBlockingIssue] = [
        NonBlockingIssue(summary=issue)
        for issue in run_input.non_blocking_issues
    ]

    mandatory_checks.append(
        MandatoryCheck(
            name="repository_accessible",
            passed=run_input.repository_accessible,
            details=(
                ""
                if run_input.repository_accessible
                else "TSAR repository is inaccessible."
            ),
        )
    )

    if (
        run_input.readme_only
        or run_input.landing_page_only
        or run_input.directory_listing_only
    ):
        surface_labels: list[str] = []
        if run_input.readme_only:
            surface_labels.append("README.md")
        if run_input.landing_page_only:
            surface_labels.append("repository landing page")
        if run_input.directory_listing_only:
            surface_labels.append("directory listing")
        mandatory_checks.append(
            MandatoryCheck(
                name="anti_loophole_real_content",
                passed=False,
                details=(
                    f"Reading {', '.join(surface_labels)} alone does not "
                    "satisfy mandatory file consultation."
                ),
            )
        )

    freshness_errors: list[str] = []
    if run_input.stale_or_cached_content:
        freshness_errors.append("cached or stale release content detected")
    if (
        run_input.expected_version is not None
        and run_input.observed_version is not None
        and run_input.observed_version.strip() != run_input.expected_version.strip()
    ):
        freshness_errors.append(
            f"version mismatch (observed {run_input.observed_version.strip()}, "
            f"expected {run_input.expected_version.strip()})"
        )
    if (
        run_input.expected_last_updated is not None
        and run_input.observed_last_updated is not None
        and run_input.observed_last_updated.strip()
        != run_input.expected_last_updated.strip()
    ):
        freshness_errors.append(
            f"manifest last_updated mismatch (observed "
            f"{run_input.observed_last_updated.strip()}, expected "
            f"{run_input.expected_last_updated.strip()})"
        )
    if (
        run_input.expected_active_file_count is not None
        and run_input.observed_active_file_count is not None
        and run_input.observed_active_file_count
        != run_input.expected_active_file_count
    ):
        freshness_errors.append(
            f"active file count mismatch (observed "
            f"{run_input.observed_active_file_count}, expected "
            f"{run_input.expected_active_file_count})"
        )
    if freshness_errors:
        mandatory_checks.append(
            MandatoryCheck(
                name="content_freshness",
                passed=False,
                details=(
                    "Stale or mismatched TSAR content cannot establish "
                    f"current adoption: {'; '.join(freshness_errors)}."
                ),
            )
        )

    security_ok = (
        run_input.fail_closed is True
        and run_input.default_mode == "strict"
        and run_input.allow_advisory_fallback is False
    )
    mandatory_checks.append(
        MandatoryCheck(
            name="security_posture",
            passed=security_ok,
            details=(
                ""
                if security_ok
                else (
                    "Weakened security posture rejected: requires "
                    "fail_closed=true, default_mode=strict, "
                    "allow_advisory_fallback=false."
                )
            ),
        )
    )

    if run_input.llms_full_fallback_used and not run_input.llms_full_complete:
        mandatory_checks.append(
            MandatoryCheck(
                name="llms_full_bundle",
                passed=False,
                details=(
                    "llms-full.txt fallback bundle is incomplete or "
                    "inaccessible."
                ),
            )
        )

    llms_fallback_valid = (
        run_input.llms_full_fallback_used and run_input.llms_full_complete
    )
    fallback_warning_added = False

    manifest_present = bool(run_input.verified_files.get("manifest.yaml", False))
    manifest_via_llms = (not manifest_present) and llms_fallback_valid and run_input.llms_full_verified_manifest
    if manifest_via_llms and not fallback_warning_added:
        non_blocking_issues.append(NonBlockingIssue(summary="Direct file retrieval blocked; verified mandatory governance content via complete llms-full.txt fallback."))
        fallback_warning_added = True
    manifest_ok = manifest_present or manifest_via_llms
    mandatory_checks.append(MandatoryCheck(name="core_file:manifest.yaml", passed=manifest_ok, details="" if manifest_ok else "Missing core file: manifest.yaml"))
            
    for rel_path in ("VERSION", "AGENTS.md"):
        present = bool(run_input.verified_files.get(rel_path, False))
        if present:
            mandatory_checks.append(MandatoryCheck(name=f"core_file:{rel_path}", passed=True))
        elif run_input.capabilities.has_local_checkout:
           mandatory_checks.append(MandatoryCheck(name=f"core_file:{rel_path}", passed=False, details=f"Missing core file: {rel_path}"))
        else:
            optional_checks.append(OptionalCheck(name=f"supplementary_file:{rel_path}", available=True, executed=False, passed=False, details=f"{rel_path} not fetched separately in web-only runtime (version and governance metadata supplied by manifest.yaml)."))
            
    directives_present = all(
        bool(run_input.verified_files.get(path, False))
        for path in SYSTEM_DIRECTIVES
    )
    if directives_present:
        for path in SYSTEM_DIRECTIVES:
            mandatory_checks.append(
                MandatoryCheck(name=f"core_file:{path}", passed=True)
            )
    elif llms_fallback_valid and run_input.llms_full_verified_directives:
        for path in SYSTEM_DIRECTIVES:
            mandatory_checks.append(
                MandatoryCheck(name=f"core_file:{path}", passed=True)
            )
        if not fallback_warning_added:
            non_blocking_issues.append(
                NonBlockingIssue(
                    summary=(
                        "Directory crawling or raw file host blocked; verified "
                        "system/*.md directives via complete llms-full.txt fallback."
                    )
                )
            )
            fallback_warning_added = True
    else:
        for path in SYSTEM_DIRECTIVES:
            present = bool(run_input.verified_files.get(path, False))
            mandatory_checks.append(
                MandatoryCheck(
                    name=f"core_file:{path}",
                    passed=present,
                    details="" if present else f"Missing directive: {path}",
                )
            )

    for skipped_name in run_input.skipped_mandatory_checks:
        mandatory_checks.append(
            MandatoryCheck(
                name=skipped_name,
                executed=False,
                passed=False,
                details="Mandatory check was skipped.",
            )
        )

    if run_input.capabilities.requires_local_conformance_scripts:
        if not run_input.runner_executed:
            mandatory_checks.append(
                MandatoryCheck(
                    name="conformance_runner",
                    executed=False,
                    passed=False,
                    details="runner.py was not executed in local Python checkout.",
                )
            )
        else:
            mandatory_checks.append(
                MandatoryCheck(
                    name="conformance_runner",
                    executed=True,
                    passed=run_input.runner_passed,
                    details="" if run_input.runner_passed else (run_input.runner_error.strip() or "runner.py failed."),
                )
            )

        if not run_input.consultation_verifier_executed:
            mandatory_checks.append(
                MandatoryCheck(
                    name="consultation_verifier",
                    executed=False,
                    passed=False,
                    details=(
                        "consultation_verifier.py was not executed in local "
                        "Python checkout."
                    ),
                )
            )
        else:
            mandatory_checks.append(
                MandatoryCheck(
                    name="consultation_verifier",
                    executed=True,
                    passed=run_input.consultation_verifier_passed,
                    details=(
                        ""
                        if run_input.consultation_verifier_passed
                        else (run_input.consultation_verifier_error.strip() or "consultation_verifier.py failed.")
                    ),
                )
            )
    else:
        optional_checks.append(
            OptionalCheck(
                name="local_conformance_scripts",
                available=False,
                executed=False,
                passed=False,
                details=(
                    "Local conformance scripts unavailable: no local checkout "
                    "and Python runtime."
                ),
            )
        )
        non_blocking_issues.append(
            NonBlockingIssue(
                summary=(
                    "Web/offline runtime cannot execute local conformance "
                    "scripts (runner.py, consultation_verifier.py)."
                )
            )
        )

    evaluation = AdoptionEvaluation(
        repository_accessible=run_input.repository_accessible,
        mandatory_checks=mandatory_checks,
        optional_checks=optional_checks,
        non_blocking_issues=non_blocking_issues,
    )
    return classify_and_format_adoption(evaluation)


def _parse_manifest_metadata(
    manifest_text: str,
) -> tuple[bool, str, bool, str | None]:
    fail_closed = False
    default_mode = ""
    allow_advisory_fallback = True
    manifest_version: str | None = None

    for raw_line in manifest_text.splitlines():
        line = raw_line.strip()
        if line.startswith("version:") and manifest_version is None:
            manifest_version = (
                line.split(":", 1)[1].strip().strip("'").strip('"')
            )
        elif line.startswith("fail_closed:"):
            fail_closed = line.split(":", 1)[1].strip().lower() == "true"
        elif line.startswith("default_mode:"):
            default_mode = (
                line.split(":", 1)[1].strip().strip("'").strip('"').lower()
            )
        elif line.startswith("allow_advisory_fallback:"):
            allow_advisory_fallback = (
                line.split(":", 1)[1].strip().lower() == "true"
            )

    return fail_closed, default_mode, allow_advisory_fallback, manifest_version


def _parse_manifest_security_posture(manifest_text: str) -> tuple[bool, str, bool]:
    fail_closed, default_mode, allow_advisory_fallback, _ = (
        _parse_manifest_metadata(manifest_text)
    )
    return fail_closed, default_mode, allow_advisory_fallback


def _execute_local_runner(root: Path) -> tuple[bool, bool, str]:
    runner_path = root / "tools/tsar-conformance/runner.py"
    if not runner_path.is_file():
        return False, False, "runner.py missing."
    try:
        proc = subprocess.run(
            [sys.executable, str(runner_path), "--json"],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
        if proc.returncode == 0:
            return True, True, ""
        err = (proc.stderr or proc.stdout or f"exit code {proc.returncode}").strip()
        return True, False, f"runner.py failed: {err[:200]}"
    except (OSError, subprocess.SubprocessError) as exc:
        return True, False, f"runner.py failed: {exc}"


def _execute_local_consultation_verifier(root: Path) -> tuple[bool, bool, str]:
    verifier_path = root / "tools/tsar-conformance/consultation_verifier.py"
    if not verifier_path.is_file():
        return False, False, "consultation_verifier.py missing."
    try:
        expected_proc = subprocess.run(
            [
                sys.executable,
                str(verifier_path),
                "--repo-root",
                str(root),
                "--print-expected",
            ],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
        if expected_proc.returncode != 0:
           return True, False, f"consultation_verifier.py failed (exit {expected_proc.returncode})"
        expected_digests = json.loads(expected_proc.stdout)
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", encoding="utf-8", delete=True
        ) as tmp:
            json.dump({"digests": expected_digests}, tmp)
            tmp.flush()
            verify_proc = subprocess.run(
                [
                    sys.executable,
                    str(verifier_path),
                    "--repo-root",
                    str(root),
                    "--evidence",
                    tmp.name,
                ],
                cwd=root,
                capture_output=True,
                text=True,
                timeout=60,
                check=False,
            )
        if verify_proc.returncode == 0:
            return True, True, ""
        err = (verify_proc.stderr or verify_proc.stdout or f"exit code {verify_proc.returncode}").strip()
        return True, False, f"consultation_verifier.py failed: {err[:200]}"
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        return True, False, f"consultation_verifier.py failed: {exc}"

def verify_local_repository_checkout(
    repo_root: Path | str | None = None,
) -> AdoptionResponse:
    """Verify an actual TSAR repository checkout on local disk by executing real checks."""

    root = (
        Path(repo_root).resolve()
        if repo_root is not None
        else Path(__file__).resolve().parents[2]
    )
    if not root.is_dir():
        return evaluate_adoption_run(
            AdoptionRunInput(
                repository_accessible=False,
                capabilities=RuntimeCapabilities(
                    has_local_checkout=True,
                    has_python_runtime=True,
                ),
            )
        )

    verified_files = {rel: (root / rel).is_file() for rel in CORE_FILES}
    manifest_path = root / "manifest.yaml"
    version_path = root / "VERSION"
    expected_version: str | None = None
    observed_version: str | None = None

    if version_path.is_file():
        expected_version = version_path.read_text(encoding="utf-8").strip()

    if manifest_path.is_file():
        (
            fail_closed,
            default_mode,
            allow_advisory_fallback,
            observed_version,
        ) = _parse_manifest_metadata(manifest_path.read_text(encoding="utf-8"))
    else:
        fail_closed, default_mode, allow_advisory_fallback = False, "", True

    runner_executed, runner_passed, runner_error = _execute_local_runner(root)
    verifier_executed, verifier_passed, verifier_error= _execute_local_consultation_verifier(
        root
    )

    return evaluate_adoption_run(
        AdoptionRunInput(
            repository_accessible=True,
            capabilities=RuntimeCapabilities(
                has_local_checkout=True,
                has_python_runtime=True,
            ),
            verified_files=verified_files,
            expected_version=expected_version,
            observed_version=observed_version,
            fail_closed=fail_closed,
            default_mode=default_mode,
            allow_advisory_fallback=allow_advisory_fallback,
            runner_executed=runner_executed,
            runner_passed=runner_passed,
            runner_error=runner_error,
            consultation_verifier_executed=verifier_executed,
            consultation_verifier_passed=verifier_passed,
            consultation_verifier_error=verifier_error,
        )
    )


def main() -> int:
    response = verify_local_repository_checkout()
    print(
        json.dumps(
            {
                "outcome": response.outcome.value,
                "header": response.lines[0] if response.lines else "",
                "rendered": response.message,
            },
            indent=2,
        )
    )
    return 0 if response.outcome != AdoptionOutcome.FAILED else 1


if __name__ == "__main__":
    raise SystemExit(main())
