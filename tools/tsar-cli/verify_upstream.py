#!/usr/bin/env python3
"""Fail-closed verification of the authoritative TSAR upstream snapshot.

The manifest and policy files are fetched from one immutable commit SHA.
This verifies repository state and availability; it does not prove that an
agent obeyed the policy or that the policy is cryptographically signed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

OWNER = "mohamedelghazali"
REPO = "TSAR"
API = f"https://api.github.com/repos/{OWNER}/{REPO}"
RAW = f"https://raw.githubusercontent.com/{OWNER}/{REPO}"
USER_AGENT = "TSAR-Upstream-Verifier/1.0"
REQUIRED_CORE = {
    "system/CORE_DIRECTIVE.md",
    "system/DO_NOT_GENERATE.md",
    "system/ENFORCEMENT_LEVELS.md",
    "system/LIFECYCLE.md",
}
VERSION_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:[-+][0-9A-Za-z.-]+)?$")


class VerificationError(RuntimeError):
    pass


def fetch_bytes(url: str, *, accept: str = "*/*", timeout: int = 20) -> bytes:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": accept},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            if response.status != 200:
                raise VerificationError(f"HTTP {response.status}: {url}")
            return response.read()
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise VerificationError(f"Unable to fetch {url}: {exc}") from exc


def fetch_json(url: str) -> dict[str, Any]:
    try:
        value = json.loads(fetch_bytes(url, accept="application/vnd.github+json"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise VerificationError(f"Invalid JSON from {url}: {exc}") from exc
    if not isinstance(value, dict):
        raise VerificationError(f"Unexpected JSON structure from {url}")
    return value


def load_yaml(raw: bytes, label: str) -> dict[str, Any]:
    try:
        import yaml
        value = yaml.safe_load(raw)
    except Exception as exc:
        raise VerificationError(f"Cannot parse {label}: {exc}") from exc
    if not isinstance(value, dict):
        raise VerificationError(f"{label} must contain a YAML mapping")
    return value


def validate_manifest(manifest: dict[str, Any]) -> tuple[str, dict[str, list[str]]]:
    version = manifest.get("version")
    if not isinstance(version, str) or not VERSION_RE.fullmatch(version):
        raise VerificationError("Manifest version is missing or is not valid semantic version text")
    repository = manifest.get("repository")
    if not isinstance(repository, str) or repository.rstrip("/") != f"https://github.com/{OWNER}/{REPO}":
        raise VerificationError("Manifest repository identity does not match the trusted TSAR repository")

    lifecycle = manifest.get("lifecycle")
    enforcement = manifest.get("enforcement")
    if not isinstance(lifecycle, dict) or not isinstance(enforcement, dict):
        raise VerificationError("Manifest lifecycle/enforcement configuration is missing")
    if lifecycle.get("fail_closed") is not True:
        raise VerificationError("Manifest does not enable fail_closed")
    if lifecycle.get("fetch_before_task") is not True:
        raise VerificationError("Manifest does not require fetch_before_task")
    if enforcement.get("default_mode") != "strict":
        raise VerificationError("Manifest default enforcement mode is not strict")
    if enforcement.get("allow_advisory_fallback") is not False:
        raise VerificationError("Advisory fallback is enabled; strict preflight refuses this configuration")
    check_url = lifecycle.get("check_url")
    if check_url != f"{RAW}/main/manifest.yaml":
        raise VerificationError("Manifest check_url is not the expected canonical upstream URL")

    active = manifest.get("active_files")
    if not isinstance(active, dict) or not active:
        raise VerificationError("Manifest active_files must be a non-empty mapping")
    groups: dict[str, list[str]] = {}
    all_paths: set[str] = set()
    for group, paths in active.items():
        if not isinstance(group, str) or not re.fullmatch(r"[a-z][a-z0-9_]*", group):
            raise VerificationError(f"Invalid active_files group name: {group!r}")
        if not isinstance(paths, list) or not paths:
            raise VerificationError(f"active_files.{group} must be a non-empty list")
        clean: list[str] = []
        for path in paths:
            if not isinstance(path, str) or not path or path.startswith("/") or "\\" in path:
                raise VerificationError(f"Unsafe active file path: {path!r}")
            parts = path.split("/")
            if any(part in ("", ".", "..") for part in parts):
                raise VerificationError(f"Unsafe active file path: {path!r}")
            if not path.endswith(".md"):
                raise VerificationError(f"Unexpected active policy file extension: {path}")
            if path in all_paths:
                raise VerificationError(f"Duplicate active policy path: {path}")
            all_paths.add(path)
            clean.append(path)
        groups[group] = clean

    core = set(groups.get("core", []))
    if core != REQUIRED_CORE:
        missing = sorted(REQUIRED_CORE - core)
        extra = sorted(core - REQUIRED_CORE)
        raise VerificationError(f"Core policy set mismatch; missing={missing}, extra={extra}")
    return version, groups


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify current TSAR upstream before security-sensitive work")
    parser.add_argument("--domain", action="append", required=True, help="Required applicable manifest domain; repeat as needed")
    parser.add_argument("--report", help="Write a JSON verification report to this path")
    parser.add_argument("--repo-root", default=None, help="Optional local TSAR checkout for version consistency checks")
    args = parser.parse_args()

    report: dict[str, Any] = {
        "verifier": "tsar-upstream-preflight",
        "status": "FAIL",
        "repository": f"{OWNER}/{REPO}",
        "commit_sha": None,
        "manifest_version": None,
        "manifest_sha256": None,
        "loaded_policy_sha256": {},
        "core_files_read": [],
        "selected_domains": [],
        "selected_policy_files_read": [],
        "active_file_count": 0,
        "checks": [],
        "errors": [],
        "limitations": [
            "Repository integrity and file availability are checked; release signatures are not verified.",
            "A PASS does not prove agent compliance or guarantee secure generated output.",
        ],
    }

    def passed(name: str, detail: str) -> None:
        report["checks"].append({"name": name, "status": "PASS", "detail": detail})

    try:
        commit = fetch_json(f"{API}/commits/main")
        sha = commit.get("sha")
        if not isinstance(sha, str) or not re.fullmatch(r"[0-9a-f]{40}", sha):
            raise VerificationError("GitHub did not return a valid 40-character main commit SHA")
        report["commit_sha"] = sha
        passed("resolve_upstream_commit", f"main resolved to immutable commit {sha}")

        tree_data = fetch_json(f"{API}/git/trees/{sha}?recursive=1")
        if tree_data.get("truncated") is True:
            raise VerificationError("Git tree response was truncated; completeness cannot be established")
        tree = tree_data.get("tree")
        if not isinstance(tree, list):
            raise VerificationError("GitHub tree response is missing its tree array")
        tree_paths = {item.get("path") for item in tree if isinstance(item, dict) and item.get("type") == "blob"}
        passed("load_complete_git_tree", f"Loaded {len(tree_paths)} blob paths at pinned commit")

        manifest_url = f"{RAW}/{sha}/manifest.yaml"
        manifest_raw = fetch_bytes(manifest_url)
        manifest = load_yaml(manifest_raw, "pinned manifest.yaml")
        version, groups = validate_manifest(manifest)
        report["manifest_version"] = version
        report["manifest_sha256"] = hashlib.sha256(manifest_raw).hexdigest()
        passed("validate_manifest", f"Manifest v{version}: strict, fail-closed, canonical repository")

        upstream_version = fetch_bytes(f"{RAW}/{sha}/VERSION").decode("utf-8").strip()
        pyproject = fetch_bytes(f"{RAW}/{sha}/tools/tsar-cli/pyproject.toml").decode("utf-8")
        package_match = re.search(r'(?m)^version\s*=\s*"([^"]+)"', pyproject)
        if not package_match:
            raise VerificationError("Pinned upstream pyproject.toml has no parseable project version")
        if upstream_version != version or package_match.group(1) != version:
            raise VerificationError(
                "Pinned upstream version mismatch: "
                f"manifest={version}, VERSION={upstream_version}, pyproject={package_match.group(1)}"
            )
        passed("upstream_version_consistency", f"manifest.yaml, VERSION, and CLI package all declare v{version}")

        declared_files = [path for paths in groups.values() for path in paths]
        report["active_file_count"] = len(declared_files)
        missing = sorted(set(declared_files) - tree_paths)
        if missing:
            raise VerificationError(f"{len(missing)} active policy file(s) missing from pinned tree: {missing[:20]}")
        passed("active_file_inventory", f"All {len(declared_files)} active policy paths exist at pinned commit")

        selected = ["core"]
        for domain in args.domain:
            if domain not in groups:
                raise VerificationError(f"Unknown manifest domain: {domain}")
            if domain not in selected:
                selected.append(domain)
        report["selected_domains"] = selected
        to_read = []
        for domain in selected:
            for path in groups[domain]:
                encoded = urllib.parse.quote(path, safe="/")
                data = fetch_bytes(f"{RAW}/{sha}/{encoded}")
                if not data.strip():
                    raise VerificationError(f"Policy file is empty: {path}")
                report["loaded_policy_sha256"][path] = hashlib.sha256(data).hexdigest()
                to_read.append(path)
                if domain == "core":
                    report["core_files_read"].append(path)
                else:
                    report["selected_policy_files_read"].append(path)
        passed("read_required_policy", f"Fetched {len(to_read)} policy files from the same pinned commit")

        if args.repo_root:
            root = Path(args.repo_root).expanduser().resolve()
            checks = {
                "VERSION": (root / "VERSION").read_text(encoding="utf-8").strip(),
                "tools/tsar-cli/pyproject.toml": None,
            }
            pyproject = (root / "tools/tsar-cli/pyproject.toml").read_text(encoding="utf-8")
            match = re.search(r'(?m)^version\s*=\s*"([^"]+)"', pyproject)
            if not match:
                raise VerificationError("Local pyproject.toml has no parseable project version")
            checks["tools/tsar-cli/pyproject.toml"] = match.group(1)
            mismatches = {path: value for path, value in checks.items() if value != version}
            if mismatches:
                raise VerificationError(f"Local version metadata differs from upstream manifest v{version}: {mismatches}")
            passed("local_version_consistency", f"VERSION and CLI package metadata match v{version}")

        report["status"] = "PASS"
        print(f"TSAR PREFLIGHT: PASS")
        print(f"Repository: {OWNER}/{REPO}")
        print(f"Pinned commit: {sha}")
        print(f"Manifest version: {version}")
        print(f"Policy files read: {len(to_read)} ({len(report['core_files_read'])} core)")
        print(f"Active policy paths verified: {len(declared_files)}")
        print(f"Domains loaded: {', '.join(selected)}")
    except Exception as exc:
        report["errors"].append(str(exc))
        print(f"TSAR PREFLIGHT: FAIL — {exc}", file=sys.stderr)
        print("Security-sensitive implementation must stop until the failure is resolved.", file=sys.stderr)

    if args.report:
        output = Path(args.report).expanduser()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"Report: {output}")
    return 0 if report["status"] == "PASS" else 2


if __name__ == "__main__":
    sys.exit(main())
