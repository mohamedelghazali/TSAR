from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
DB = ROOT / "rules" / "database"

def test_files_present():
    for name in ["postgresql.md", "mysql.md", "mongodb.md", "redis.md",
                 "multi-tenant.md", "replication.md"]:
        assert (DB / name).exists()

def test_postgres_forbids_trust():
    text = (DB / "postgresql.md").read_text()
    assert "trust" in text

def test_postgres_requires_rls():
    text = (DB / "postgresql.md").read_text()
    assert "Row-level security" in text or "RLS" in text

def test_multi_tenant_requires_rls():
    text = (DB / "multi-tenant.md").read_text()
    assert "Row-Level Security" in text
    assert "BYPASSRLS" in text
