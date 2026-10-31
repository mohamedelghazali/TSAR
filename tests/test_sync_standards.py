"""Failure-mode and atomicity tests for upstream standards synchronization."""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "sync_standards", ROOT / "scripts" / "sync_standards.py"
)
sync = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(sync)


def test_fetch_failure_does_not_create_or_modify_cache(tmp_path, monkeypatch, capsys):
    cache = tmp_path / ".tsar-cache"
    cache.mkdir()
    marker = cache / "owasp-llm.sha256"
    marker.write_text("a" * 64, encoding="ascii")
    before = marker.read_text(encoding="ascii")

    monkeypatch.setattr(sync, "CACHE_DIR", cache)
    monkeypatch.setattr(sync, "UPSTREAM", {"one": "https://example.invalid/one",
                                           "two": "https://example.invalid/two"})
    calls = []

    def fake_fetch(url):
        calls.append(url)
        if url.endswith("/two"):
            raise OSError("simulated network failure")
        return b"valid source"

    monkeypatch.setattr(sync, "fetch", fake_fetch)
    assert sync.main() == 1
    assert marker.read_text(encoding="ascii") == before
    assert not list(tmp_path.glob(".tsar-cache.stage.*"))
    assert "cache was not changed" in capsys.readouterr().err


def test_all_unchanged_sources_do_not_rewrite_cache(tmp_path, monkeypatch):
    cache = tmp_path / ".tsar-cache"
    cache.mkdir()
    data = {"one": b"source one", "two": b"source two"}
    import hashlib
    for name, content in data.items():
        (cache / f"{name}.sha256").write_text(
            hashlib.sha256(content).hexdigest(), encoding="ascii"
        )

    monkeypatch.setattr(sync, "CACHE_DIR", cache)
    monkeypatch.setattr(sync, "UPSTREAM", {name: f"https://example.invalid/{name}"
                                           for name in data})
    monkeypatch.setattr(sync, "fetch", lambda url: data[url.rsplit("/", 1)[-1]])
    before = {p.name: p.stat().st_mtime_ns for p in cache.iterdir()}

    assert sync.main() == 0
    after = {p.name: p.stat().st_mtime_ns for p in cache.iterdir()}
    assert after == before


def test_changed_sources_are_committed_as_complete_cache(tmp_path, monkeypatch):
    cache = tmp_path / ".tsar-cache"
    cache.mkdir()
    (cache / "one.sha256").write_text("0" * 64, encoding="ascii")
    (cache / "operator-note.txt").write_text("preserve me", encoding="utf-8")

    monkeypatch.setattr(sync, "CACHE_DIR", cache)
    monkeypatch.setattr(sync, "UPSTREAM", {
        "one": "https://example.invalid/one",
        "two": "https://example.invalid/two",
    })
    monkeypatch.setattr(sync, "fetch", lambda url: url.rsplit("/", 1)[-1].encode())

    assert sync.main() == 0
    assert (cache / "one.sha256").read_text(encoding="ascii") == (
        __import__("hashlib").sha256(b"one").hexdigest()
    )
    assert (cache / "two.sha256").exists()
    assert (cache / "operator-note.txt").read_text(encoding="utf-8") == "preserve me"
    assert not list(tmp_path.glob(".tsar-cache.stage.*"))
    assert not list(tmp_path.glob(".tsar-cache.backup.*"))


def test_invalid_existing_digest_aborts_without_mutation(tmp_path, monkeypatch):
    cache = tmp_path / ".tsar-cache"
    cache.mkdir()
    marker = cache / "one.sha256"
    marker.write_text("not-a-sha", encoding="ascii")

    monkeypatch.setattr(sync, "CACHE_DIR", cache)
    monkeypatch.setattr(sync, "UPSTREAM", {"one": "https://example.invalid/one"})
    monkeypatch.setattr(sync, "fetch", lambda _url: b"new source")

    assert sync.main() == 1
    assert marker.read_text(encoding="ascii") == "not-a-sha"
