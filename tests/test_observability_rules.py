from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OBS = ROOT / "rules" / "observability"

def test_files_present():
    for name in ["metrics.md", "tracing.md", "logging.md", "alerting.md"]:
        assert (OBS / name).exists()

def test_metrics_forbids_pii_labels():
    text = (OBS / "metrics.md").read_text()
    assert "PII" in text
    assert "labels" in text
