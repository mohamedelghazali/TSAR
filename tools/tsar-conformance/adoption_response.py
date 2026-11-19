"""Deterministic 3-state TSAR adoption outcome classification and response formatting."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Sequence

SUCCESS_MESSAGE = "✅ Adoption successful. Let's start working on your project."
FAILED_HEADER = "❌ Adoption failed."
WARNING_HEADER = "⚠️ Adoption successful, but some issues require attention."

_FORBIDDEN_OVERCLAIM_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(
        r"consultation\s+guarantees\s+(?:policy\s+)?(?:conformance|compliance|security)",
        re.IGNORECASE,
    ),
    re.compile(
        r"consultation\s+proves\s+security\s+effectiveness",
        re.IGNORECASE,
    ),
    re.compile(
        r"(?:reading|fetching)\s+(?:the\s+)?(?:files|rules|manifest|directives)\s+guarantees\s+(?:policy\s+)?(?:conformance|compliance|security)",
        re.IGNORECASE,
    ),
)

_UNAVAILABLE_STATE_A_MARKERS: tuple[str, ...] = (
    "unsupported",
    "unavailable",
    "unexecuted",
    "not available",
)


class AdoptionOutcome(str, Enum):
    """Deterministic outcome states for TSAR adoption."""

    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    SUCCESS_WITH_WARNINGS = "SUCCESS_WITH_WARNINGS"


@dataclass(frozen=True)
class MandatoryCheck:
    """Result of a mandatory TSAR adoption check."""

    name: str
    passed: bool = True
    executed: bool = True
    details: str = ""


@dataclass(frozen=True)
class OptionalCheck:
    """Result of an optional TSAR adoption check."""

    name: str
    executed: bool = True
    available: bool = True
    passed: bool = True
    details: str = ""


@dataclass(frozen=True)
class NonBlockingIssue:
    """Non-blocking warning or issue observed during TSAR adoption."""

    summary: str
    impact: str = ""


@dataclass(frozen=True)
class AdoptionEvaluation:
    """Aggregated inputs used to classify a TSAR adoption run."""

    repository_accessible: bool = True
    missing_mandatory_files: Sequence[str] = field(default_factory=tuple)
    mandatory_checks: Sequence[MandatoryCheck] = field(default_factory=tuple)
    optional_checks: Sequence[OptionalCheck] = field(default_factory=tuple)
    non_blocking_issues: Sequence[NonBlockingIssue] = field(default_factory=tuple)
    repository_error: str = ""


@dataclass(frozen=True)
class AdoptionResponse:
    """Classified outcome and formatted final response."""

    outcome: AdoptionOutcome
    message: str
    lines: tuple[str, ...]


@dataclass(frozen=True)
class ResponseValidationResult:
    """Validation result for raw agent adoption response text."""

    valid: bool
    detected_outcome: AdoptionOutcome | None
    violations: tuple[str, ...]


def _format_detail(details: str) -> str:
    cleaned = details.strip()
    return f" ({cleaned})" if cleaned else ""


def classify_and_format_adoption(evaluation: AdoptionEvaluation) -> AdoptionResponse:
    """Classify TSAR adoption outcome and format the deterministic response."""
    failure_lines: list[str] = []

    if not evaluation.repository_accessible:
        reason = evaluation.repository_error.strip() or "TSAR repository could not be accessed."
        failure_lines.append(f"- Repository inaccessible: {reason}")

    for missing_file in evaluation.missing_mandatory_files:
        failure_lines.append(f"- Missing mandatory file: {missing_file}")

    if not evaluation.mandatory_checks:
        failure_lines.append("- Mandatory checks missing: no mandatory checks were executed.")

    for check in evaluation.mandatory_checks:
        if not check.executed:
            failure_lines.append(f"- Mandatory check not executed: {check.name}{_format_detail(check.details)}")
        elif not check.passed:
            failure_lines.append(f"- Mandatory check failed: {check.name}{_format_detail(check.details)}")

    if failure_lines:
        lines = (FAILED_HEADER, *failure_lines)
        return AdoptionResponse(outcome=AdoptionOutcome.FAILED, message="\n".join(lines), lines=lines)

    warning_lines: list[str] = []

    for issue in evaluation.non_blocking_issues:
        impact = issue.impact.strip() or "non-blocking"
        warning_lines.append(f"- Non-blocking issue: {issue.summary} (Impact: {impact})")

    for opt in evaluation.optional_checks:
        if not opt.available:
            warning_lines.append(f"- Optional check unavailable: {opt.name}{_format_detail(opt.details)}")
        elif not opt.executed:
            warning_lines.append(f"- Optional check not executed: {opt.name}{_format_detail(opt.details)}")
        elif not opt.passed:
            warning_lines.append(f"- Optional check failed: {opt.name}{_format_detail(opt.details)}")

    if warning_lines:
        completed_lines = [f"- Completed mandatory check: {check.name}" for check in evaluation.mandatory_checks]
        lines = (WARNING_HEADER, *warning_lines, *completed_lines)
        return AdoptionResponse(outcome=AdoptionOutcome.SUCCESS_WITH_WARNINGS, message="\n".join(lines), lines=lines)

    return AdoptionResponse(outcome=AdoptionOutcome.SUCCESS, message=SUCCESS_MESSAGE, lines=(SUCCESS_MESSAGE,))


def validate_adoption_response_text(response_text: str) -> ResponseValidationResult:
    """Validate raw agent adoption output against canonical 3-state and integrity rules."""
    stripped = response_text.strip()
    if not stripped:
        return ResponseValidationResult(
            valid=False,
            detected_outcome=None,
            violations=("Empty adoption response.",),
        )

    lines = stripped.splitlines()
    first_line = lines[0].strip()
    violations: list[str] = []
    detected_outcome: AdoptionOutcome | None = None

    if first_line == SUCCESS_MESSAGE:
        detected_outcome = AdoptionOutcome.SUCCESS
        if len(lines) > 1:
            violations.append(
                "State A (SUCCESS) must be strictly one line with no additional commentary or capability tables."
            )
    elif first_line == FAILED_HEADER:
        detected_outcome = AdoptionOutcome.FAILED
        if not any(line.strip() for line in lines[1:]):
            violations.append(
                "State B (FAILED) must include failure details after the canonical header."
            )
    elif first_line == WARNING_HEADER:
        detected_outcome = AdoptionOutcome.SUCCESS_WITH_WARNINGS
        if not any(line.strip() for line in lines[1:]):
            violations.append(
                "State C (SUCCESS_WITH_WARNINGS) must include non-blocking issue details after the canonical header."
            )
    else:
        violations.append(
            "Line 1 must be an exact canonical header (State A ✅, State B ❌, or State C ⚠️); custom headers or preambles are not permitted."
        )

    if first_line.startswith("✅"):
        lowered = stripped.lower()
        found_markers = [m for m in _UNAVAILABLE_STATE_A_MARKERS if m in lowered]
        if found_markers:
            violations.append(
                "State A (✅) false positive: response declares unsupported/unavailable/unexecuted capabilities "
                f"({', '.join(found_markers)}) and must use State C (⚠️) or State B (❌) instead."
            )

    for pattern in _FORBIDDEN_OVERCLAIM_PATTERNS:
        if pattern.search(stripped):
            violations.append(
                "Verification integrity violation: source consultation does not guarantee policy conformance or prove security effectiveness."
            )
            break

    return ResponseValidationResult(
        valid=not violations,
        detected_outcome=detected_outcome,
        violations=tuple(violations),
    )
