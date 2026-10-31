from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
MSG = ROOT / "rules" / "messaging"

def test_files_present():
    for name in ["kafka.md", "rabbitmq.md", "nats.md", "pubsub.md",
                 "idempotency.md", "poison-message.md"]:
        assert (MSG / name).exists()

def test_kafka_requires_tls():
    text = (MSG / "kafka.md").read_text()
    assert "TLS 1.3" in text
    assert "PLAINTEXT" in text

def test_idempotency_requires_dedupe():
    text = (MSG / "idempotency.md").read_text()
    assert "message_id" in text
    assert "dedupe" in text.lower() or "deduplication" in text.lower()
