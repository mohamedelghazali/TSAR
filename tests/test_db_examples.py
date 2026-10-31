"""Verify secure database examples have required hardening."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "examples" / "secure" / "database"

def test_postgres_example_uses_tls():
    text = (DB / "postgres.py").read_text()
    assert "TLSv1_3" in text
    assert "ssl.create_default_context" in text

def test_postgres_example_sets_tenant():
    text = (DB / "postgres.py").read_text()
    assert "app.current_tenant" in text

def test_migrations_enable_rls():
    text = (DB / "migrations.sql").read_text()
    assert "ENABLE ROW LEVEL SECURITY" in text
    assert "CREATE POLICY" in text
