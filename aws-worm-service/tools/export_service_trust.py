"""Export the AWS KMS Ed25519 public key into TSAR's external trust-file format."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import stat

import boto3
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--key-id", required=True, help="AWS KMS asymmetric Ed25519 key ARN or ID")
    parser.add_argument("--service-id", required=True)
    parser.add_argument("--region", required=True)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    response = boto3.client("kms", region_name=args.region).get_public_key(KeyId=args.key_id)
    if response.get("KeySpec") != "ECC_NIST_EDWARDS25519" or response.get("KeyUsage") != "SIGN_VERIFY":
        raise SystemExit("KMS key must be ECC_NIST_EDWARDS25519 with SIGN_VERIFY usage")
    public_key = serialization.load_der_public_key(response["PublicKey"])
    if not isinstance(public_key, Ed25519PublicKey):
        raise SystemExit("KMS returned a non-Ed25519 public key")
    raw_key = public_key.public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    document = {
        "schema": "tsar/audit-anchor-trust/v1",
        "service_id": args.service_id,
        "public_key": base64.b64encode(raw_key).decode("ascii"),
    }
    destination = args.output.expanduser()
    repository_root = Path(__file__).resolve().parents[2]
    if destination.resolve(strict=False).is_relative_to(repository_root):
        raise SystemExit("trust file must be written outside the TSAR repository")
    if not destination.parent.is_dir():
        raise SystemExit("output parent directory must already exist and be protected")
    if os.name == "posix" and destination.parent.stat().st_mode & (stat.S_IWGRP | stat.S_IWOTH):
        raise SystemExit("output parent directory must not be group- or world-writable")
    destination = destination.parent.resolve(strict=True) / destination.name
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(str(destination), flags, 0o600)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(document, stream, sort_keys=True, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
    except Exception:
        try:
            destination.unlink()
        except OSError:
            pass
        raise
    if os.name == "posix":
        os.chmod(destination, stat.S_IRUSR | stat.S_IWUSR)
    print("Created TSAR service trust file: " + str(destination))
    print("Public-key SHA-256 fingerprint: " + hashlib.sha256(raw_key).hexdigest())
    print("Verify this fingerprint through an independent administrative channel.")


if __name__ == "__main__":
    main()
