"""TSAR reference implementation: Python secure patterns.

Dependencies: argon2-cffi, cryptography, pyjwt
"""
import os
import hmac
import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
import jwt

ARGON2 = PasswordHasher(time_cost=3, memory_cost=65536, parallelism=4, hash_len=32, salt_len=16)

def hash_password(password: str) -> str:
    if len(password) < 12:
        raise ValueError("password must be at least 12 characters")
    return ARGON2.hash(password)

def verify_password(password: str, stored_hash: str) -> bool:
    try:
        return ARGON2.verify(stored_hash, password)
    except VerifyMismatchError:
        return False

def constant_time_compare(a: bytes, b: bytes) -> bool:
    return hmac.compare_digest(a, b)

def generate_token(nbytes: int = 32) -> str:
    return secrets.token_urlsafe(nbytes)

class AEADBox:
    """AES-256-GCM envelope with per-message random nonce and AAD binding."""

    def __init__(self, master_key: bytes):
        if len(master_key) != 32:
            raise ValueError("master key must be 32 bytes")
        self._key = master_key

    def _derive(self, purpose: bytes) -> bytes:
        return HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=b"tsar/aead/" + purpose,
        ).derive(self._key)

    def encrypt(self, plaintext: bytes, aad: bytes) -> bytes:
        key = self._derive(b"data")
        nonce = os.urandom(12)
        ct = AESGCM(key).encrypt(nonce, plaintext, aad)
        return b"\x01" + nonce + ct

    def decrypt(self, envelope: bytes, aad: bytes) -> bytes:
        if not envelope or envelope[0] != 1:
            raise ValueError("unsupported envelope version")
        nonce, ct = envelope[1:13], envelope[13:]
        key = self._derive(b"data")
        return AESGCM(key).decrypt(nonce, ct, aad)

JWT_SECRET = os.environ["TSAR_JWT_SECRET"].encode()
JWT_ALG = "HS256"

def issue_token(user_id: str, ttl_minutes: int = 15) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=ttl_minutes)).timestamp()),
        "jti": secrets.token_urlsafe(16),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)

def verify_token(token: str) -> dict:
    return jwt.decode(
        token,
        JWT_SECRET,
        algorithms=[JWT_ALG],
        options={"require": ["exp", "iat", "sub"]},
    )

ALLOWED_ACTIONS = frozenset({"read", "list", "search"})

def authorize(action: str, user: dict, resource_owner_id: str) -> bool:
    if action not in ALLOWED_ACTIONS:
        return False
    if user["sub"] != resource_owner_id and "admin" not in user.get("roles", []):
        return False
    return True

def audit_log(event: str, user_id: str, outcome: str) -> None:
    record = {
        "event": event,
        "user_id": hashlib.sha256(user_id.encode()).hexdigest()[:16],
        "outcome": outcome,
        "ts": datetime.now(timezone.utc).isoformat(),
    }
    print(record)
