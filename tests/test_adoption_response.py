"""Tests for deterministic 3-state TSAR adoption response classification."""

import importlib.util
import sys
import unittest
from pathlib import Path

MODULE = (
    Path(__file__).resolve().parents[1]
    / "tools"
    / "tsar-conformance"
    / "adoption_response.py"
)
SPEC = importlib.util.spec_from_file_location("tsar_adoption_response", MODULE)
assert SPEC is not None and SPEC.loader is not None
adoption_response = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = adoption_response
SPEC.loader.exec_module(adoption_response)

AdoptionEvaluation = adoption_response.AdoptionEvaluation
AdoptionOutcome = adoption_response.AdoptionOutcome
MandatoryCheck = adoption_response.MandatoryCheck
NonBlockingIssue = adoption_response.NonBlockingIssue
OptionalCheck = adoption_response.OptionalCheck
classify_and_format_adoption = adoption_response.classify_and_format_adoption
validate_adoption_response_text = adoption_response.validate_adoption_response_text


class TestAdoptionResponse(unittest.TestCase):
    """Validate all 3 adoption outcome states and edge cases."""

    def test_01_complete_adoption_all_mandatory_passed_no_warnings(self) -> None:
        evaluation = AdoptionEvaluation(
            repository_accessible=True,
            missing_mandatory_files=[],
            mandatory_checks=[
                MandatoryCheck(name="governance-files", passed=True, executed=True),
                MandatoryCheck(name="policy-validation", passed=True, executed=True),
            ],
            optional_checks=[
                OptionalCheck(name="telemetry-hook", executed=True, available=True, passed=True),
            ],
            non_blocking_issues=[],
        )
        result = classify_and_format_adoption(evaluation)
        self.assertEqual(result.outcome, AdoptionOutcome.SUCCESS)
        self.assertEqual(
            result.message,
            "✅ Adoption successful. Let's start working on your project.",
        )

    def test_02_successful_mandatory_with_non_blocking_warnings(self) -> None:
        evaluation = AdoptionEvaluation(
            repository_accessible=True,
            missing_mandatory_files=[],
            mandatory_checks=[
                MandatoryCheck(name="governance-files", passed=True, executed=True),
            ],
            non_blocking_issues=[
                NonBlockingIssue(
                    summary="Optional pre-commit hook not installed",
                    impact="Local commits will not auto-run TSAR lint",
                ),
            ],
        )
        result = classify_and_format_adoption(evaluation)
        self.assertEqual(result.outcome, AdoptionOutcome.SUCCESS_WITH_WARNINGS)
        self.assertTrue(
            result.message.startswith("⚠️ Adoption successful, but some issues require attention.")
        )
        self.assertIn("Optional pre-commit hook not installed", result.message)
        self.assertIn("Local commits will not auto-run TSAR lint", result.message)
        self.assertIn("governance-files", result.message)

    def test_03_inaccessible_tsar_repository(self) -> None:
        evaluation = AdoptionEvaluation(
            repository_accessible=False,
            repository_error="HTTP 403 Forbidden",
            mandatory_checks=[
                MandatoryCheck(name="governance-files", passed=True, executed=True),
            ],
        )
        result = classify_and_format_adoption(evaluation)
        self.assertEqual(result.outcome, AdoptionOutcome.FAILED)
        self.assertTrue(result.message.startswith("❌ Adoption failed."))
        self.assertIn("HTTP 403 Forbidden", result.message)

    def test_04_missing_mandatory_governance_file(self) -> None:
        evaluation = AdoptionEvaluation(
            repository_accessible=True,
            missing_mandatory_files=["AGENTS.md", "policies/tsar.yaml"],
            mandatory_checks=[
                MandatoryCheck(name="governance-files", passed=True, executed=True),
            ],
        )
        result = classify_and_format_adoption(evaluation)
        self.assertEqual(result.outcome, AdoptionOutcome.FAILED)
        self.assertTrue(result.message.startswith("❌ Adoption failed."))
        self.assertIn("AGENTS.md", result.message)
        self.assertIn("policies/tsar.yaml", result.message)

    def test_05_failed_mandatory_validation(self) -> None:
        evaluation = AdoptionEvaluation(
            repository_accessible=True,
            missing_mandatory_files=[],
            mandatory_checks=[
                MandatoryCheck(
                    name="schema-validation",
                    passed=False,
                    executed=True,
                    details="fail_closed missing",
                ),
            ],
        )
        result = classify_and_format_adoption(evaluation)
        self.assertEqual(result.outcome, AdoptionOutcome.FAILED)
        self.assertTrue(result.message.startswith("❌ Adoption failed."))
        self.assertIn("schema-validation", result.message)
        self.assertIn("fail_closed missing", result.message)

    def test_06_mandatory_verification_not_executed(self) -> None:
        evaluation = AdoptionEvaluation(
            repository_accessible=True,
            missing_mandatory_files=[],
            mandatory_checks=[
                MandatoryCheck(
                    name="conformance-suite",
                    passed=False,
                    executed=False,
                    details="runner skipped",
                ),
            ],
        )
        result = classify_and_format_adoption(evaluation)
        self.assertEqual(result.outcome, AdoptionOutcome.FAILED)
        self.assertTrue(result.message.startswith("❌ Adoption failed."))
        self.assertIn("conformance-suite", result.message)

    def test_07_optional_verification_unavailable_after_successful_mandatory(self) -> None:
        evaluation = AdoptionEvaluation(
            repository_accessible=True,
            missing_mandatory_files=[],
            mandatory_checks=[
                MandatoryCheck(name="governance-files", passed=True, executed=True),
            ],
            optional_checks=[
                OptionalCheck(
                    name="sbom-attestation",
                    executed=False,
                    available=False,
                    details="cosign not installed",
                ),
            ],
        )
        result = classify_and_format_adoption(evaluation)
        self.assertEqual(result.outcome, AdoptionOutcome.SUCCESS_WITH_WARNINGS)
        self.assertTrue(
            result.message.startswith("⚠️ Adoption successful, but some issues require attention.")
        )
        self.assertIn("sbom-attestation", result.message)
        self.assertIn("governance-files", result.message)

    def test_08_no_additional_text_after_exact_success_message(self) -> None:
        evaluation = AdoptionEvaluation(
            repository_accessible=True,
            missing_mandatory_files=[],
            mandatory_checks=[
                MandatoryCheck(name="governance-files", passed=True, executed=True),
            ],
        )
        result = classify_and_format_adoption(evaluation)
        self.assertEqual(result.outcome, AdoptionOutcome.SUCCESS)
        self.assertEqual(len(result.message.splitlines()), 1)
        self.assertEqual(len(result.lines), 1)
        self.assertFalse(result.message.endswith("\n"))

    def test_09_mandatory_failure_mixed_with_non_blocking_warning(self) -> None:
        evaluation = AdoptionEvaluation(
            repository_accessible=True,
            missing_mandatory_files=[],
            mandatory_checks=[
                MandatoryCheck(name="governance-files", passed=True, executed=True),
                MandatoryCheck(name="policy-check", passed=False, executed=True),
            ],
            non_blocking_issues=[
                NonBlockingIssue(
                    summary="Optional badge missing",
                    impact="README badge will not render",
                ),
            ],
        )
        result = classify_and_format_adoption(evaluation)
        self.assertEqual(result.outcome, AdoptionOutcome.FAILED)
        self.assertTrue(result.message.startswith("❌ Adoption failed."))
        self.assertNotIn("⚠️", result.message)

    def test_10_empty_mandatory_checks_no_false_positive_success(self) -> None:
        evaluation = AdoptionEvaluation(
            repository_accessible=True,
            missing_mandatory_files=[],
            mandatory_checks=[],
            optional_checks=[],
            non_blocking_issues=[],
        )
        result = classify_and_format_adoption(evaluation)
        self.assertEqual(result.outcome, AdoptionOutcome.FAILED)
        self.assertTrue(result.message.startswith("❌ Adoption failed."))

    def test_11_validate_canonical_state_a_exact_single_line_passes(self) -> None:
        result = validate_adoption_response_text(
            "✅ Adoption successful. Let's start working on your project."
        )
        self.assertTrue(result.valid)
        self.assertEqual(result.detected_outcome, AdoptionOutcome.SUCCESS)
        self.assertEqual(result.violations, ())

    def test_12_validate_dola_false_positive_state_a_rejected(self) -> None:
        text = (
            "✅ TSAR v1.2.0 — Adoption Successful ✅\n"
            "- Hook installation: unsupported\n"
            "- Cross-session persistence: unavailable"
        )
        result = validate_adoption_response_text(text)
        self.assertFalse(result.valid)
        self.assertIsNone(result.detected_outcome)
        self.assertTrue(any("canonical header" in v for v in result.violations))
        self.assertTrue(any("false positive" in v for v in result.violations))

    def test_13_validate_state_a_with_extra_commentary_rejected(self) -> None:
        text = (
            "✅ Adoption successful. Let's start working on your project.\n"
            "All 4 directives loaded."
        )
        result = validate_adoption_response_text(text)
        self.assertFalse(result.valid)
        self.assertEqual(result.detected_outcome, AdoptionOutcome.SUCCESS)
        self.assertTrue(any("strictly one line" in v for v in result.violations))

    def test_14_validate_qwen_consultation_guarantees_conformance_overclaim_rejected(self) -> None:
        text = (
            "✅ Adoption successful. Let's start working on your project.\n"
            "Note: direct file consultation guarantees policy conformance."
        )
        result = validate_adoption_response_text(text)
        self.assertFalse(result.valid)
        self.assertTrue(any("Verification integrity violation" in v for v in result.violations))

    def test_15_validate_canonical_state_b_fail_closed_refusal_passes(self) -> None:
        text = (
            "❌ Adoption failed.\n"
            "- Repository inaccessible: network retrieval blocked."
        )
        result = validate_adoption_response_text(text)
        self.assertTrue(result.valid)
        self.assertEqual(result.detected_outcome, AdoptionOutcome.FAILED)
        self.assertEqual(result.violations, ())

    def test_16_validate_canonical_state_c_warning_response_passes(self) -> None:
        text = (
            "⚠️ Adoption successful, but some issues require attention.\n"
            "- Optional check unavailable: telemetry-hook"
        )
        result = validate_adoption_response_text(text)
        self.assertTrue(result.valid)
        self.assertEqual(result.detected_outcome, AdoptionOutcome.SUCCESS_WITH_WARNINGS)
        self.assertEqual(result.violations, ())

    def test_17_validate_preamble_before_header_rejected(self) -> None:
        text = (
            "Here is the adoption result:\n"
            "✅ Adoption successful. Let's start working on your project."
        )
        result = validate_adoption_response_text(text)
        self.assertFalse(result.valid)
        self.assertIsNone(result.detected_outcome)
        self.assertTrue(any("canonical header" in v for v in result.violations))

    def test_18_validate_bare_state_b_or_state_c_without_details_rejected(self) -> None:
        for header, expected_outcome in (
            ("❌ Adoption failed.", AdoptionOutcome.FAILED),
            (
                "⚠️ Adoption successful, but some issues require attention.",
                AdoptionOutcome.SUCCESS_WITH_WARNINGS,
            ),
        ):
            result = validate_adoption_response_text(header)
            self.assertFalse(result.valid)
            self.assertEqual(result.detected_outcome, expected_outcome)
            self.assertTrue(result.violations)


if __name__ == "__main__":
    unittest.main()
