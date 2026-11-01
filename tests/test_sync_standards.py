"""Fail-closed tests for upstream standards synchronization."""
import hashlib
import importlib.util
import io
import urllib.error
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "sync_standards.py"


def load_sync_module():
    spec = importlib.util.spec_from_file_location("tsar_sync_standards_test", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_nist_source_uses_authoritative_nist_domain():
    module = load_sync_module()
    assert module.UPSTREAM["nist-ai-rmf"] == (
        "https://www.nist.gov/itl/ai-risk-management-framework"
    )


def test_fetch_retries_transient_http_errors_and_sends_user_agent(monkeypatch):
    module = load_sync_module()
    calls = []

    def fake_urlopen(request, timeout):
        calls.append((request, timeout))
        assert request.get_header("User-agent").startswith("TSAR-Standards-Sync/")
        assert timeout == 30
        if len(calls) == 1:
            raise urllib.error.HTTPError(
                request.full_url, 503, "Service Unavailable", hdrs=None, fp=None
            )
        return io.BytesIO(b"official standards")

    monkeypatch.setattr(module.urllib.request, "urlopen", fake_urlopen)
    monkeypatch.setattr(module.time, "sleep", lambda _seconds: None)

    assert module.fetch("https://example.test/standards") == b"official standards"
    assert len(calls) == 2


def test_fetch_does_not_retry_permanent_not_found(monkeypatch):
    module = load_sync_module()
    calls = []

    def fake_urlopen(request, timeout):
        calls.append(request)
        raise urllib.error.HTTPError(
            request.full_url, 404, "Not Found", hdrs=None, fp=None
        )

    monkeypatch.setattr(module.urllib.request, "urlopen", fake_urlopen)
    monkeypatch.setattr(
        module.time, "sleep",
        lambda _seconds: (_ for _ in ()).throw(AssertionError("must not retry 404")),
    )

    try:
        module.fetch("https://example.test/missing")
    except urllib.error.HTTPError as exc:
        assert exc.code == 404
    else:
        raise AssertionError("HTTP 404 must be raised")
    assert len(calls) == 1


def test_fetch_failure_does_not_modify_existing_cache(tmp_path, monkeypatch):
    module = load_sync_module()
    cache = tmp_path / ".tsar-cache"
    cache.mkdir()
    marker = cache / "old.sha256"
    marker.write_text("previous marker", encoding="ascii")
    note = cache / "operator-note.txt"
    note.write_text("keep", encoding="utf-8")
    monkeypatch.setattr(module, "CACHE_DIR", cache)
    monkeypatch.setattr(module, "UPSTREAM", {"first": "url-1", "second": "url-2"})

    def fake_fetch(url):
        if url == "url-2":
            raise OSError("simulated upstream outage")
        return b"new upstream content"

    monkeypatch.setattr(module, "fetch", fake_fetch)
    assert module.main() == 1
    assert marker.read_text(encoding="ascii") == "previous marker"
    assert note.read_text(encoding="utf-8") == "keep"


def test_changed_sources_are_reported_after_atomic_cache_update(tmp_path, monkeypatch):
    module = load_sync_module()
    cache = tmp_path / ".tsar-cache"
    output = tmp_path / "github-output.txt"
    monkeypatch.setattr(module, "CACHE_DIR", cache)
    monkeypatch.setattr(module, "UPSTREAM", {"owasp": "url-1", "nist": "url-2"})
    monkeypatch.setattr(module, "fetch", lambda _url: b"new standards")
    monkeypatch.setenv("GITHUB_OUTPUT", str(output))

    assert module.main() == 0
    expected = hashlib.sha256(b"new standards").hexdigest()
    assert (cache / "owasp.sha256").read_text(encoding="ascii").strip() == expected
    assert (cache / "nist.sha256").is_file()
    values = output.read_text(encoding="utf-8")
    assert "changed=true" in values
    assert "changed_sources=owasp,nist" in values


def test_unchanged_sources_report_false_without_replacing_cache(tmp_path, monkeypatch):
    module = load_sync_module()
    cache = tmp_path / ".tsar-cache"
    cache.mkdir()
    digest = hashlib.sha256(b"same").hexdigest()
    for name in ("owasp", "nist"):
        (cache / f"{name}.sha256").write_text(digest + "\n", encoding="ascii")
    output = tmp_path / "github-output.txt"
    monkeypatch.setattr(module, "CACHE_DIR", cache)
    monkeypatch.setattr(module, "UPSTREAM", {"owasp": "url-1", "nist": "url-2"})
    monkeypatch.setattr(module, "fetch", lambda _url: b"same")
    monkeypatch.setattr(
        module, "commit_cache_atomically",
        lambda _digests: (_ for _ in ()).throw(AssertionError("cache must not be replaced")),
    )
    monkeypatch.setenv("GITHUB_OUTPUT", str(output))

    assert module.main() == 0
    assert "changed=false" in output.read_text(encoding="utf-8")


def test_standards_cache_is_not_gitignored():
    gitignore = SCRIPT.parents[1] / ".gitignore"
    lines = [line.strip() for line in gitignore.read_text(encoding="utf-8").splitlines()]
    assert ".tsar-cache/" not in lines


def test_cache_promotion_failure_restores_previous_cache(tmp_path, monkeypatch):
    module = load_sync_module()
    cache = tmp_path / ".tsar-cache"
    cache.mkdir()
    marker = cache / "one.sha256"
    marker.write_text("previous digest", encoding="ascii")
    operator_note = cache / "operator-note.txt"
    operator_note.write_text("preserve", encoding="utf-8")
    monkeypatch.setattr(module, "CACHE_DIR", cache)
    monkeypatch.setattr(module, "UPSTREAM", {"one": "url-1"})
    monkeypatch.setattr(module, "fetch", lambda _url: b"new source")

    real_replace = module.os.replace

    def fail_promotion(source, destination):
        source_path = Path(source)
        destination_path = Path(destination)
        if source_path.name.startswith(".tsar-cache.stage.") and destination_path == cache:
            raise OSError("simulated cache promotion failure")
        return real_replace(source, destination)

    monkeypatch.setattr(module.os, "replace", fail_promotion)
    assert module.main() == 1
    assert marker.read_text(encoding="ascii") == "previous digest"
    assert operator_note.read_text(encoding="utf-8") == "preserve"
    assert not list(tmp_path.glob(".tsar-cache.stage.*"))
    assert not list(tmp_path.glob(".tsar-cache.backup.*"))
