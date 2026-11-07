"""Authenticated end-to-end live test for the deployed TSAR AWS WORM service."""
from __future__ import annotations
import base64
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
import urllib.error
import urllib.request
import boto3
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()

def call(url: str, token: str, *, method: str = "GET", body: dict | None = None):
    data = canonical(body) if body is not None else None
    request = urllib.request.Request(url, data=data, method=method, headers={
        "Authorization": f"Bearer {token}", "Content-Type": "application/json", "Cache-Control": "no-store"
    })
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.status, json.loads(response.read())
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read() or b"{}")

def main() -> None:
    endpoint, token = os.environ["TSAR_WORM_ENDPOINT"].rstrip("/"), os.environ["TSAR_WORM_TOKEN"]
    key_arn = os.environ["TSAR_WORM_KMS_KEY_ARN"]
    retention_days = int(os.environ["TSAR_WORM_RETENTION_DAYS"])
    if not endpoint.startswith("https://") or not token:
        raise SystemExit("A valid HTTPS endpoint and bearer token are required.")
    unauth = urllib.request.Request(endpoint + "/v1/runs/" + ("0" * 64) + "/latest")
    try:
        urllib.request.urlopen(unauth, timeout=20)
        raise SystemExit("Unauthenticated request unexpectedly succeeded.")
    except urllib.error.HTTPError as exc:
        if exc.code != 401:
            raise SystemExit(f"Expected HTTP 401 without credentials; received {exc.code}.")
    created_at = datetime.now(timezone.utc).isoformat(timespec="microseconds")
    commit_sha = os.environ.get("GITHUB_SHA", "0" * 40)
    evidence = b"TSAR GitHub Actions live WORM qualification evidence.\n"
    path = "evidence/github-actions-live-smoke-test.txt"
    gates = {"github_oidc_deployment": "PASS", "live_api_smoke_test": "PASS"}
    record = {"schema":"tsar/lifecycle-run/v1","created_at":created_at,
      "task":{"task":"GitHub Actions live AWS WORM qualification"},
      "provenance":{"upstream_commit_sha":commit_sha},"gates":gates,
      "evidence":[{"path":path,"sha256":sha256(evidence),"size_bytes":len(evidence)}]}
    snapshot = canonical(record)
    identity = {"repository":"mohamedelghazali/TSAR","created_at":created_at,
      "task":record["task"]["task"],"upstream_commit_sha":commit_sha}
    run_id, record_sha = sha256(canonical(identity)), sha256(snapshot)
    body = {"schema":"tsar/external-audit-anchor-request/v1","repository":"mohamedelghazali/TSAR",
      "run_id":run_id,"record_sha256":record_sha,"audit_snapshot_b64":base64.b64encode(snapshot).decode(),
      "evidence_files_b64":{path:base64.b64encode(evidence).decode()},"integrity_status":"PASS",
      "lifecycle_status":"COMPLETE","gate_states":gates,"upstream_commit_sha":commit_sha,
      "expected_previous_anchor_sha256":None,
      "idempotency_key":sha256((run_id+":"+record_sha).encode())}
    status, payload = call(endpoint+"/v1/anchors",token,method="POST",body=body)
    if status != 201 or not isinstance(payload.get("receipt"),dict):
        raise SystemExit(f"Append failed HTTP {status}: {payload.get('error','invalid response')}")
    receipt = payload["receipt"]
    expected = {"schema":"tsar/external-audit-anchor-receipt/v1","run_id":run_id,
      "sequence":1,"record_sha256":record_sha,"retention_mode":"WORM_COMPLIANCE"}
    if any(receipt.get(k)!=v for k,v in expected.items()):
        raise SystemExit("Receipt fields do not match submitted live evidence.")
    expiry = datetime.fromisoformat(receipt["retain_until"].replace("Z","+00:00"))
    if expiry < datetime.now(timezone.utc)+timedelta(days=retention_days-1):
        raise SystemExit("Receipt retention expiry is shorter than configured policy.")
    der = boto3.client("kms").get_public_key(KeyId=key_arn)["PublicKey"]
    public_key = serialization.load_der_public_key(der)
    if not isinstance(public_key,Ed25519PublicKey):
        raise SystemExit("Deployed KMS public key is not Ed25519.")
    unsigned = {k:v for k,v in receipt.items() if k!="signature"}
    try:
        public_key.verify(base64.b64decode(receipt["signature"],validate=True),canonical(unsigned))
    except Exception as exc:
        raise SystemExit("KMS receipt signature verification failed.") from exc
    status, latest = call(endpoint+f"/v1/runs/{run_id}/latest",token)
    if status!=200 or latest.get("receipt")!=receipt:
        raise SystemExit(f"Latest-anchor read failed or differed (HTTP {status}).")
    status, retry = call(endpoint+"/v1/anchors",token,method="POST",body=body)
    if status!=201 or retry.get("receipt")!=receipt:
        raise SystemExit("Idempotent retry did not return the original receipt.")
    print(json.dumps({"result":"PASS","unauthenticated_request":"401","append":"201",
      "receipt_signature":"Ed25519 verified against AWS KMS public key","retention_mode":receipt["retention_mode"],
      "latest_read":"PASS","idempotent_retry":"PASS","run_id":run_id,
      "anchor_id":receipt["anchor_id"],"retain_until":receipt["retain_until"]},indent=2))

if __name__ == "__main__":
    main()
