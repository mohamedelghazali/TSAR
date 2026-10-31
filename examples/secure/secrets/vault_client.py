"""TSAR reference: secure Vault client with short TTL and fail-closed."""
import os
import time
import threading
import hvac

class VaultClient:
    def __init__(self, addr: str, role: str, sa_token_path: str):
        self._client = hvac.Client(url=addr, verify="/etc/tls/ca.pem")
        self._role = role
        self._sa_token_path = sa_token_path
        self._lock = threading.Lock()
        self._cache: dict[str, tuple[dict, float]] = {}
        self._authenticate()

    def _authenticate(self) -> None:
        with open(self._sa_token_path) as f:
            jwt = f.read().strip()
        resp = self._client.auth.kubernetes.login(role=self._role, jwt=jwt)
        self._client.token = resp["auth"]["client_token"]
        self._lease = time.time() + resp["auth"]["lease_duration"] - 60

    def _ensure_auth(self) -> None:
        if time.time() >= self._lease:
            self._authenticate()

    def get(self, path: str, cache_fraction: float = 0.5) -> dict:
        now = time.time()
        with self._lock:
            cached = self._cache.get(path)
            if cached and now < cached[1]:
                return cached[0]
            self._ensure_auth()
            try:
                resp = self._client.secrets.kv.v2.read_secret_version(
                    path=path, mount_point="secret",
                )
            except Exception as exc:
                raise RuntimeError(f"vault read failed: {path}") from exc
            data = resp["data"]["data"]
            lease = resp["lease_duration"] if "lease_duration" in resp else 3600
            ttl = now + lease * cache_fraction
            self._cache[path] = (data, ttl)
            return data

def load_config() -> dict:
    client = VaultClient(
        addr=os.environ["VAULT_ADDR"],
        role=os.environ["VAULT_ROLE"],
        sa_token_path="/var/run/secrets/kubernetes.io/serviceaccount/token",
    )
    return {
        "database_url": client.get("app/database")["url"],
        "jwt_secret": client.get("app/jwt")["secret"],
    }
