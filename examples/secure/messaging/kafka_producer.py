"""TSAR reference: secure Kafka producer with TLS, SASL, and AEAD payloads."""
import json
import os
from confluent_kafka import Producer
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes

MASTER_KEY = bytes.fromhex(os.environ["TSAR_MASTER_KEY_HEX"])

def derive(purpose: bytes) -> bytes:
    return HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b"tsar/kafka/" + purpose,
    ).derive(MASTER_KEY)

def encrypt_payload(payload: dict, topic: str) -> bytes:
    key = derive(topic.encode())
    nonce = os.urandom(12)
    aad = topic.encode()
    ct = AESGCM(key).encrypt(nonce, json.dumps(payload).encode(), aad)
    return b"\x01" + nonce + ct

conf = {
    "bootstrap.servers": os.environ["KAFKA_BROKERS"],
    "security.protocol": "SASL_SSL",
    "sasl.mechanism": "SCRAM-SHA-512",
    "sasl.username": os.environ["KAFKA_USERNAME"],
    "sasl.password": os.environ["KAFKA_PASSWORD"],
    "ssl.ca.location": "/etc/tls/ca.pem",
    "ssl.endpoint.identification.algorithm": "https",
    "acks": "all",
    "enable.idempotence": True,
    "compression.type": "zstd",
    "linger.ms": 5,
}

producer = Producer(conf)

def publish(topic: str, key: str, payload: dict) -> None:
    envelope = encrypt_payload(payload, topic)
    producer.produce(
        topic=topic,
        key=key.encode(),
        value=envelope,
        headers={
            "content-type": "application/x-tsar-aead",
            "schema-version": "1",
        },
    )
    producer.poll(0)

def flush() -> None:
    producer.flush(timeout=10)
