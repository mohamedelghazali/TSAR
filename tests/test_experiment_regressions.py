"""Regression and 10-model adversarial validation tests for TSAR adoption."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
VERIFY_ADOPTION_PATH = (
    REPO_ROOT / "tools" / "tsar-conformance" / "verify_adoption.py"
)

_SPEC = importlib.util.spec_from_file_location(
    "tsar_verify_adoption", VERIFY_ADOPTION_PATH
)
assert _SPEC is not None and _SPEC.loader is not None
verify_adoption = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = verify_adoption
_SPEC.loader.exec_module(verify_adoption)

AdoptionOutcome = verify_adoption.AdoptionOutcome
AdoptionRunInput = verify_adoption.AdoptionRunInput
RuntimeCapabilities = verify_adoption.RuntimeCapabilities
evaluate_adoption_run = verify_adoption.evaluate_adoption_run
verify_local_repository_checkout = verify_adoption.verify_local_repository_checkout

ALL_CORE_FILES = {path: True for path in verify_adoption.CORE_FILES}


class ExperimentRegressionTests(unittest.TestCase):
    """Regression tests covering the 11 original experiments and 10-model adversarial matrix."""

    def test_01_workstation_full_adoption_success(self) -> None:
        result = evaluate_adoption_run(
            AdoptionRunInput(
                repository_accessible=True,
                capabilities=RuntimeCapabilities(
                    has_local_checkout=True,
                    has_python_runtime=True,
                ),
                verified_files=dict(ALL_CORE_FILES),
                runner_executed=True,
                runner_passed=True,
                consultation_verifier_executed=True,
                consultation_verifier_passed=True,
            )
        )
        self.assertEqual(result.outcome, AdoptionOutcome.SUCCESS)
        self.assertEqual(
            result.message,
            "✅ Adoption successful. Let's start working on your project.",
        )

    def test_02_web_only_false_positive_prevention(self) -> None:
        result = evaluate_adoption_run(
            AdoptionRunInput(
                repository_accessible=True,
                capabilities=RuntimeCapabilities(
                    has_local_checkout=False,
                    has_python_runtime=False,
                ),
                verified_files=dict(ALL_CORE_FILES),
            )
        )
        self.assertNotEqual(result.outcome, AdoptionOutcome.SUCCESS)
        self.assertEqual(result.outcome, AdoptionOutcome.SUCCESS_WITH_WARNINGS)
        self.assertEqual(
            result.message.splitlines()[0],
            "⚠️ Adoption successful, but some issues require attention.",
        )
        self.assertIn("Optional check unavailable: local_conformance_scripts", result.message)
        self.assertNotIn("Optional check failed:", result.message)

    def test_03_web_only_false_negative_prevention(self) -> None:
        result = evaluate_adoption_run(
            AdoptionRunInput(
                repository_accessible=True,
                capabilities=RuntimeCapabilities(
                    has_local_checkout=False,
                    has_python_runtime=False,
                ),
                verified_files=dict(ALL_CORE_FILES),
                runner_executed=False,
                consultation_verifier_executed=False,
            )
        )
        self.assertNotEqual(result.outcome, AdoptionOutcome.FAILED)
        self.assertEqual(result.outcome, AdoptionOutcome.SUCCESS_WITH_WARNINGS)
        self.assertEqual(
            result.message.splitlines()[0],
            "⚠️ Adoption successful, but some issues require attention.",
        )

    def test_04_missing_system_directives_fail_closed(self) -> None:
        for directive in verify_adoption.SYSTEM_DIRECTIVES:
            incomplete_files = dict(ALL_CORE_FILES)
            incomplete_files[directive] = False
            result = evaluate_adoption_run(
                AdoptionRunInput(
                    repository_accessible=True,
                    capabilities=RuntimeCapabilities(
                        has_local_checkout=False,
                        has_python_runtime=False,
                    ),
                    verified_files=incomplete_files,
                    llms_full_fallback_used=False,
                )
            )
            self.assertEqual(result.outcome, AdoptionOutcome.FAILED, msg=directive)
            self.assertEqual(result.message.splitlines()[0], "❌ Adoption failed.")

    def test_05_llms_full_fallback_recovery(self) -> None:
        without_system_dir = {
            path: (not path.startswith("system/"))
            for path in verify_adoption.CORE_FILES
        }
        result = evaluate_adoption_run(
            AdoptionRunInput(
                repository_accessible=True,
                capabilities=RuntimeCapabilities(
                    has_local_checkout=False,
                    has_python_runtime=False,
                    directory_crawling_blocked=True,
                    raw_host_blocked=True,
                    github_api_available=True,
                ),
                verified_files=without_system_dir,
                llms_full_fallback_used=True,
                llms_full_complete=True,
                llms_full_verified_directives=True,
            )
        )
        self.assertEqual(result.outcome, AdoptionOutcome.SUCCESS_WITH_WARNINGS)
        self.assertEqual(
            result.message.splitlines()[0],
            "⚠️ Adoption successful, but some issues require attention.",
        )

    def test_06_inaccessible_repository_fail_closed(self) -> None:
        result = evaluate_adoption_run(
            AdoptionRunInput(
                repository_accessible=False,
                capabilities=RuntimeCapabilities(
                    has_local_checkout=False,
                    has_python_runtime=False,
                ),
                verified_files={},
            )
        )
        self.assertEqual(result.outcome, AdoptionOutcome.FAILED)
        self.assertEqual(result.message.splitlines()[0], "❌ Adoption failed.")

    def test_07_local_skipped_runner_fail_closed(self) -> None:
        result = evaluate_adoption_run(
            AdoptionRunInput(
                repository_accessible=True,
                capabilities=RuntimeCapabilities(
                    has_local_checkout=True,
                    has_python_runtime=True,
                ),
                verified_files=dict(ALL_CORE_FILES),
                runner_executed=False,
                consultation_verifier_executed=True,
                consultation_verifier_passed=True,
            )
        )
        self.assertEqual(result.outcome, AdoptionOutcome.FAILED)
        self.assertEqual(result.message.splitlines()[0], "❌ Adoption failed.")
        self.assertIn("Mandatory check not executed: conformance_runner", result.message)

    def test_08_weakened_security_posture_rejected(self) -> None:
        for kwargs in (
            {"fail_closed": False},
            {"default_mode": "advisory"},
            {"allow_advisory_fallback": True},
        ):
            result = evaluate_adoption_run(
                AdoptionRunInput(
                    repository_accessible=True,
                    capabilities=RuntimeCapabilities(
                        has_local_checkout=True,
                        has_python_runtime=True,
                    ),
                    verified_files=dict(ALL_CORE_FILES),
                    runner_executed=True,
                    runner_passed=True,
                    consultation_verifier_executed=True,
                    consultation_verifier_passed=True,
                    **kwargs,
                )
            )
            self.assertEqual(result.outcome, AdoptionOutcome.FAILED)
            self.assertEqual(result.message.splitlines()[0], "❌ Adoption failed.")

    def test_09_real_local_disk_checkout_verification(self) -> None:
        result = verify_local_repository_checkout(REPO_ROOT)
        self.assertEqual(result.outcome, AdoptionOutcome.SUCCESS, msg=result.message)
        self.assertEqual(
            result.message,
            "✅ Adoption successful. Let's start working on your project.",
        )

    def test_10_adversarial_readme_only_fails_closed(self) -> None:
        result = evaluate_adoption_run(
            AdoptionRunInput(
                repository_accessible=True,
                readme_only=True,
                verified_files={"README.md": True},
            )
        )
        self.assertEqual(result.outcome, AdoptionOutcome.FAILED)
        self.assertEqual(result.message.splitlines()[0], "❌ Adoption failed.")
        self.assertIn("anti_loophole_real_content", result.message)

    def test_11_adversarial_directory_listing_only_fails_closed(self) -> None:
        result = evaluate_adoption_run(
            AdoptionRunInput(
                repository_accessible=True,
                directory_listing_only=True,
                verified_files={},
            )
        )
        self.assertEqual(result.outcome, AdoptionOutcome.FAILED)
        self.assertEqual(result.message.splitlines()[0], "❌ Adoption failed.")
        self.assertIn("directory listing", result.message)

    def test_12_adversarial_gemini_hydrogen_landing_page_and_stale_tree_fails_closed(self) -> None:
        """Reproduces TEST 10 (Gemini Hydrogen): PERMISSION_DENIED on raw/API/blob, landing page only, stale 171 files."""
        result = evaluate_adoption_run(
            AdoptionRunInput(
                repository_accessible=True,
                landing_page_only=True,
                verified_files={},
                stale_or_cached_content=True,
                expected_active_file_count=175,
                observed_active_file_count=171,
            )
        )
        self.assertEqual(result.outcome, AdoptionOutcome.FAILED)
        self.assertEqual(result.message.splitlines()[0], "❌ Adoption failed.")
        self.assertIn("anti_loophole_real_content", result.message)
        self.assertIn("content_freshness", result.message)

    def test_13_adversarial_manifest_inaccessible_fails_closed(self) -> None:
        without_manifest = dict(ALL_CORE_FILES)
        without_manifest["manifest.yaml"] = False
        result = evaluate_adoption_run(
            AdoptionRunInput(
                repository_accessible=True,
                verified_files=without_manifest,
                llms_full_fallback_used=False,
            )
        )
        self.assertEqual(result.outcome, AdoptionOutcome.FAILED)
        self.assertEqual(result.message.splitlines()[0], "❌ Adoption failed.")
        self.assertIn("Missing core file: manifest.yaml", result.message)

    def test_14_adversarial_incomplete_llms_full_fails_closed(self) -> None:
        without_system_dir = {
            path: (not path.startswith("system/"))
            for path in verify_adoption.CORE_FILES
        }
        result = evaluate_adoption_run(
            AdoptionRunInput(
                repository_accessible=True,
                verified_files=without_system_dir,
                llms_full_fallback_used=True,
                llms_full_complete=False,
                llms_full_verified_directives=True,
            )
        )
        self.assertEqual(result.outcome, AdoptionOutcome.FAILED)
        self.assertEqual(result.message.splitlines()[0], "❌ Adoption failed.")
        self.assertIn("llms_full_bundle", result.message)

    def test_15_adversarial_cached_stale_claude_manifest_fails_closed(self) -> None:
        """Reproduces TEST 3 (Claude AI): cached manifest 2026-11-07 and blocked unseen URLs."""
        result = evaluate_adoption_run(
            AdoptionRunInput(
                repository_accessible=True,
                verified_files={
                    "manifest.yaml": True,
                    "AGENTS.md": True,
                    "VERSION": False,
                },
                expected_last_updated="2026-11-18",
                observed_last_updated="2026-11-07",
            )
        )
        self.assertEqual(result.outcome, AdoptionOutcome.FAILED)
        self.assertEqual(result.message.splitlines()[0], "❌ Adoption failed.")
        self.assertIn("content_freshness", result.message)

    def test_16_adversarial_stale_version_drift_fails_closed(self) -> None:
        """Cached/stale release tag cannot falsely establish current adoption."""
        result = evaluate_adoption_run(
            AdoptionRunInput(
                repository_accessible=True,
                verified_files=dict(ALL_CORE_FILES),
                expected_version="1.2.1",
                observed_version="1.2.0",
            )
        )
        self.assertEqual(result.outcome, AdoptionOutcome.FAILED)
        self.assertEqual(result.message.splitlines()[0], "❌ Adoption failed.")
        self.assertIn("version mismatch", result.message)

    def test_17_adversarial_local_failing_script_actually_fails_closed(self) -> None:
        """Verifies verify_local_repository_checkout actually executes scripts rather than trusting .is_file()."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "VERSION").write_text("1.2.1\n", encoding="utf-8")
            (root / "manifest.yaml").write_text(
                'version: "1.2.1"\nfail_closed: true\ndefault_mode: "strict"\nallow_advisory_fallback: false\n',
                encoding="utf-8",
            )
            (root / "AGENTS.md").write_text("# AGENTS\n", encoding="utf-8")
            (root / "system").mkdir()
            for rel in verify_adoption.SYSTEM_DIRECTIVES:
                (root / rel).write_text("# directive\n", encoding="utf-8")
            conformance_dir = root / "tools" / "tsar-conformance"
            conformance_dir.mkdir(parents=True)
            (conformance_dir / "runner.py").write_text("import sys; sys.exit(1)\n", encoding="utf-8")
            (conformance_dir / "consultation_verifier.py").write_text("import sys; sys.exit(1)\n", encoding="utf-8")

            result = verify_local_repository_checkout(root)
            self.assertEqual(result.outcome, AdoptionOutcome.FAILED)
            self.assertEqual(result.message.splitlines()[0], "❌ Adoption failed.")
            self.assertIn("runner.py failed", result.message)
            self.assertIn("consultation_verifier.py failed", result.message)

    def test_18_adversarial_ten_model_simulation_matrix(self) -> None:
        """Controlled 10-model fixture matrix matching all 10 evaluated models and line-1 header ordering."""
        scenarios: list[tuple[str, AdoptionRunInput, AdoptionOutcome, str]] = [
            (
                "TEST 1 DeepSeek (web-only verified)",
                AdoptionRunInput(
                    repository_accessible=True,
                    verified_files=dict(ALL_CORE_FILES),
                ),
                AdoptionOutcome.SUCCESS_WITH_WARNINGS,
                "⚠️ Adoption successful, but some issues require attention.",
            ),
            (
                "TEST 2 ChatGPT (web-only verified)",
                AdoptionRunInput(
                    repository_accessible=True,
                    verified_files=dict(ALL_CORE_FILES),
                ),
                AdoptionOutcome.SUCCESS_WITH_WARNINGS,
                "⚠️ Adoption successful, but some issues require attention.",
            ),
            (
                "TEST 3 Claude AI (blocked unseen URLs + stale 2026-11-07)",
                AdoptionRunInput(
                    repository_accessible=True,
                    verified_files={"manifest.yaml": True, "AGENTS.md": True},
                    expected_last_updated="2026-11-18",
                    observed_last_updated="2026-11-07",
                ),
                AdoptionOutcome.FAILED,
                "❌ Adoption failed.",
            ),
            (
                "TEST 4 Copilot (search only, repo files unreadable)",
                AdoptionRunInput(
                    repository_accessible=False,
                    verified_files={},
                ),
                AdoptionOutcome.FAILED,
                "❌ Adoption failed.",
            ),
            (
                "TEST 5 Qwen AI (web verified, local upstream blocked)",
                AdoptionRunInput(
                    repository_accessible=True,
                    verified_files=dict(ALL_CORE_FILES),
                    non_blocking_issues=["verify_upstream.py blocked by network policy"],
                ),
                AdoptionOutcome.SUCCESS_WITH_WARNINGS,
                "⚠️ Adoption successful, but some issues require attention.",
            ),
            (
                "TEST 6 Dola (verified complete llms-full.txt context bundle)",
                AdoptionRunInput(
                    repository_accessible=True,
                    verified_files={"VERSION": True, "AGENTS.md": True},
                    llms_full_fallback_used=True,
                    llms_full_complete=True,
                    llms_full_verified_manifest=True,
                    llms_full_verified_directives=True,
                ),
                AdoptionOutcome.SUCCESS_WITH_WARNINGS,
                "⚠️ Adoption successful, but some issues require attention.",
            ),
            (
                "TEST 7 Perplexity (direct fetches failed)",
                AdoptionRunInput(
                    repository_accessible=False,
                    verified_files={},
                ),
                AdoptionOutcome.FAILED,
                "❌ Adoption failed.",
            ),
            (
                "TEST 8 Kimi.ai (Python present, no local TSAR checkout)",
                AdoptionRunInput(
                    repository_accessible=True,
                    capabilities=RuntimeCapabilities(
                        has_local_checkout=False,
                        has_python_runtime=True,
                    ),
                    verified_files=dict(ALL_CORE_FILES),
                ),
                AdoptionOutcome.SUCCESS_WITH_WARNINGS,
                "⚠️ Adoption successful, but some issues require attention.",
            ),
            (
                "TEST 9 Gemini Neon (full web verification + memory)",
                AdoptionRunInput(
                    repository_accessible=True,
                    verified_files=dict(ALL_CORE_FILES),
                ),
                AdoptionOutcome.SUCCESS_WITH_WARNINGS,
                "⚠️ Adoption successful, but some issues require attention.",
            ),
            (
                "TEST 10 Gemini Hydrogen (landing page only + PERMISSION_DENIED)",
                AdoptionRunInput(
                    repository_accessible=True,
                    landing_page_only=True,
                    verified_files={},
                    expected_active_file_count=175,
                    observed_active_file_count=171,
                ),
                AdoptionOutcome.FAILED,
                "❌ Adoption failed.",
            ),
        ]

        for label, run_input, expected_outcome, expected_header in scenarios:
            with self.subTest(model=label):
                result = evaluate_adoption_run(run_input)
                self.assertEqual(result.outcome, expected_outcome)
                self.assertEqual(result.message.splitlines()[0], expected_header)

    def test_19_readme_adoption_prompt_contains_explicit_direct_urls(self) -> None:
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn(
            "Direct canonical URLs (for URL-allowlisted runtimes that only fetch explicit URLs):",
            readme,
        )
        raw_base = "https://raw." + "github" + "user" + "content" + ".com/mohamedelghazali/TSAR/main/"
        for rel in (
            "llms-full.txt",
            "VERSION",
            "manifest.yaml",
            "AGENTS.md",
            "system/CORE_DIRECTIVE.md",
            "system/DO_NOT_GENERATE.md",
            "system/ENFORCEMENT_LEVELS.md",
            "system/LIFECYCLE.md",
            "docs/universal-agent-onboarding.md",
            "docs/release-qualification.md",
        ):
            self.assertIn(raw_base + rel, readme)
        api_url = "https://api." + "github" + ".com/repos/mohamedelghazali/TSAR/contents/llms-full.txt"
        self.assertIn(api_url, readme)

    def test_20_release_qualification_has_no_stale_v120_contradictions(self) -> None:
            doc = (REPO_ROOT / "docs" / "release-qualification.md").read_text(
                encoding="utf-8"
            )
            self.assertIn("TSAR-Main-Protection", doc)
            for check_name in (
                "Full verification (OPA, LSP, Terraform, pytest)",
                "TSAR Self-Test",
                "Claude Code Windows Hook Compatibility",
                "Infrastructure Validation",
                "TSAR Validate Rules",
                "TSAR Orchestrator",
            ):
                self.assertIn(check_name, doc)
            self.assertIn("v1.1.1", doc)
            self.assertIn("v1.2.0", doc)
            self.assertIn("v1.2.1", doc)
            self.assertNotIn("NOT yet release-qualified", doc)

    def test_21_web_only_claude_without_version_or_agents_returns_state_c(self) -> None:
        files = {"manifest.yaml": True, "system/CORE_DIRECTIVE.md": True, "system/DO_NOT_GENERATE.md": True, "system/ENFORCEMENT_LEVELS.md": True, "system/LIFECYCLE.md": True}
        res = evaluate_adoption_run(AdoptionRunInput(repository_accessible=True, capabilities=RuntimeCapabilities(has_local_checkout=False, has_python_runtime=False), verified_files=files))
        self.assertEqual(res.outcome, AdoptionOutcome.SUCCESS_WITH_WARNINGS)
        self.assertIn("supplementary_file:VERSION", res.message)
        self.assertIn("supplementary_file:AGENTS.md", res.message)

    def test_22_local_checkout_missing_version_or_agents_still_fails_closed(self) -> None:
        for missing_file in ("VERSION", "AGENTS.md"):
            files = dict(ALL_CORE_FILES)
            files[missing_file] = False
            res = evaluate_adoption_run(AdoptionRunInput(repository_accessible=True, capabilities=RuntimeCapabilities(has_local_checkout=True, has_python_runtime=True), verified_files=files, runner_executed=True, runner_passed=True, consultation_verifier_executed=True, consultation_verifier_passed=True))
            self.assertEqual(res.outcome, AdoptionOutcome.FAILED, msg=missing_file)
            self.assertIn(f"Missing core file: {missing_file}", res.message)

    def test_23_latest_four_model_run_integration(self) -> None:
        base_ok = {"VERSION": True, "manifest.yaml": True, "system/CORE_DIRECTIVE.md": True, "system/DO_NOT_GENERATE.md": True, "system/ENFORCEMENT_LEVELS.md": True, "system/LIFECYCLE.md": True}
        claude_ok = {"manifest.yaml": True, "system/CORE_DIRECTIVE.md": True, "system/DO_NOT_GENERATE.md": True, "system/ENFORCEMENT_LEVELS.md": True, "system/LIFECYCLE.md": True}
        for name, inp, expected in (("DeepSeek", AdoptionRunInput(verified_files=base_ok), AdoptionOutcome.SUCCESS_WITH_WARNINGS), ("ChatGPT", AdoptionRunInput(capabilities=RuntimeCapabilities(has_local_checkout=False, has_python_runtime=True), verified_files=base_ok), AdoptionOutcome.SUCCESS_WITH_WARNINGS), ("Claude", AdoptionRunInput(verified_files=claude_ok), AdoptionOutcome.SUCCESS_WITH_WARNINGS), ("Copilot", AdoptionRunInput(capabilities=RuntimeCapabilities(has_local_checkout=False, has_python_runtime=True), verified_files={}), AdoptionOutcome.FAILED)):
            res = evaluate_adoption_run(inp)
            self.assertEqual(res.outcome, expected, msg=name)


if __name__ == "__main__":
    unittest.main()
