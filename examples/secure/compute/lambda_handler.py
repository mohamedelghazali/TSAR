"""TSAR reference: secure AWS Lambda handler."""
import json
import os
import hmac
import hashlib
import boto3
from botocore.exceptions import ClientError

secrets = boto3.client("secretsmanager")
dynamodb = boto3.resource("dynamodb")

JWT_SECRET_CACHE: dict[str, bytes] = {}

def get_jwt_secret() -> bytes:
    if "jwt" not in JWT_SECRET_CACHE:
        resp = secrets.get_secret_value(SecretId=os.environ["JWT_SECRET_ARN"])
        JWT_SECRET_CACHE["jwt"] = resp["SecretString"].encode()
    return JWT_SECRET_CACHE["jwt"]

ALLOWED_ACTIONS = frozenset({"read", "list"})

def verify_signature(body: bytes, signature_hex: str) -> bool:
    expected = hmac.new(get_jwt_secret(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature_hex)

def validate_input(event: dict) -> dict:
    if not isinstance(event.get("body"), str) or len(event["body"]) > 10_000:
        raise ValueError("invalid body")
    payload = json.loads(event["body"])
    if not isinstance(payload, dict):
        raise ValueError("body must be object")
    action = payload.get("action")
    if action not in ALLOWED_ACTIONS:
        raise ValueError("invalid action")
    return payload

def handler(event, context):
    try:
        sig = event.get("headers", {}).get("x-tsar-signature", "")
        body = event.get("body", "").encode()
        if not verify_signature(body, sig):
            return {"statusCode": 401, "body": json.dumps({"error": "unauthorized"})}
        payload = validate_input(event)
        table = dynamodb.Table(os.environ["TABLE_NAME"])
        item = table.get_item(Key={"id": payload.get("id")}).get("Item")
        if not item:
            return {"statusCode": 404, "body": json.dumps({"error": "not_found"})}
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json", "Cache-Control": "no-store"},
            "body": json.dumps(item),
        }
    except ValueError:
        return {"statusCode": 400, "body": json.dumps({"error": "bad_request"})}
    except ClientError:
        return {"statusCode": 500, "body": json.dumps({"error": "internal"})}
