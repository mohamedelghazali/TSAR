"""TSAR reference: idempotent Kafka consumer with dedupe and DLQ."""
import json
import os
from confluent_kafka import Consumer, KafkaError, Producer
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
import redis

MASTER_KEY = bytes.fromhex(os.environ["TSAR_MASTER_KEY_HEX"])
redis_client = redis.Redis(host=os.environ["REDIS_HOST"], port=6379, ssl=True)

def derive(purpose: bytes) -> bytes:
    return HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b"tsar/kafka/" + purpose,
    ).derive(MASTER_KEY)

def decrypt_payload(envelope: bytes, topic: str) -> dict:
    if not envelope or envelope[0] != 1:
        raise ValueError("bad envelope")
    nonce, ct = envelope[1:13], envelope[13:]
    key = derive(topic.encode())
    return json.loads(AESGCM(key).decrypt(nonce, ct, topic.encode()))

consumer = Consumer({
    "bootstrap.servers": os.environ["KAFKA_BROKERS"],
    "security.protocol": "SASL_SSL",
    "sasl.mechanism": "SCRAM-SHA-512",
    "sasl.username": os.environ["KAFKA_USERNAME"],
    "sasl.password": os.environ["KAFKA_PASSWORD"],
    "ssl.ca.location": "/etc/tls/ca.pem",
    "group.id": os.environ["KAFKA_GROUP"],
    "auto.offset.reset": "earliest",
    "enable.auto.commit": False,
})

dlq = Producer({**consumer._conf, "client.id": "tsar-dlq"})

MAX_ATTEMPTS = 5
DEDUPE_TTL_SECONDS = 86400

def dedupe_key(topic: str, msg_key: bytes) -> str:
    return f"tsar:kafka:dedupe:{topic}:{msg_key.hex()}"

def process(topic: str, key: bytes, payload: dict) -> None:
    # Application logic; must be idempotent per rules/messaging/idempotency.md.
    pass

def handle(msg) -> None:
    topic = msg.topic()
    key = msg.key() or b""
    dk = dedupe_key(topic, key)

    if redis_client.exists(dk):
        consumer.commit(message=msg, asynchronous=False)
        return

    try:
        payload = decrypt_payload(msg.value(), topic)
        process(topic, key, payload)
        redis_client.setex(dk, DEDUPE_TTL_SECONDS, b"1")
        consumer.commit(message=msg, asynchronous=False)
    except Exception as exc:
        attempts = int(redis_client.get(f"{dk}:attempts") or b"0") + 1
        redis_client.setex(f"{dk}:attempts", DEDUPE_TTL_SECONDS, str(attempts))
        if attempts >= MAX_ATTEMPTS:
            dlq.produce(
                topic=f"{topic}.dlq",
                key=key,
                value=msg.value(),
                headers={"reason": str(type(exc).__name__)},
            )
            dlq.flush(timeout=5)
            consumer.commit(message=msg, asynchronous=False)
        else:
            raise

def run() -> None:
    consumer.subscribe([os.environ["KAFKA_TOPIC"]])
    try:
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                raise RuntimeError(msg.error())
            handle(msg)
    finally:
        consumer.close()

if __name__ == "__main__":
    run()
