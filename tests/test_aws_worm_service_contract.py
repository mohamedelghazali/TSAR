from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SERVICE = ROOT / "aws-worm-service"


def test_lambda_service_uses_compliance_lock_and_ed25519_kms_signing():
    source = (SERVICE / "lambda" / "handler.py").read_text(encoding="utf-8")
    assert '"COMPLIANCE"' in source
    assert '"ED25519_SHA_512"' in source
    assert 'MessageType="RAW"' in source
    assert "get_object_retention" in source
    assert "transact_write_items" in source
    assert "hmac.compare_digest" in source
    assert "audit_snapshot_b64" in source
    assert "digest(audit_bytes) != record_sha" in source
    assert "stable_identity" in source
    assert "evidence_files_b64" in source
    assert "evidence archive bytes do not match audit evidence metadata" in source
    assert "s3:PutObjectRetention" in (SERVICE / "terraform" / "main.tf").read_text(encoding="utf-8")


def test_terraform_enables_object_lock_versioning_and_deletion_protection():
    source = (SERVICE / "terraform" / "main.tf").read_text(encoding="utf-8")
    assert "object_lock_enabled = true" in source
    assert 'status = "Enabled"' in source
    assert 'mode = "COMPLIANCE"' in source
    assert "deletion_protection_enabled = true" in source
    assert "aws_kms_key" in source
    assert "aws_apigatewayv2_stage" in source
    assert "throttling_rate_limit" in source


def test_service_does_not_claim_aws_resources_are_deployed():
    docs = (SERVICE / "README.md").read_text(encoding="utf-8")
    assert "No AWS resources have been deployed" in docs
    assert "retained orphan objects" in docs.lower()


def test_github_aws_deployment_uses_oidc_and_explicit_irreversible_retention_ack():
    workflow = (ROOT / ".github" / "workflows" / "aws-worm-deploy.yml").read_text(encoding="utf-8")
    assert "id-token: write" in workflow
    assert "aws-actions/configure-aws-credentials@" in workflow
    assert "use_lockfile=true" in workflow
    assert "YES_I_UNDERSTAND_COMPLIANCE_RETENTION_IS_IRREVERSIBLE" in workflow
    assert "aws secretsmanager get-secret-value" in workflow
    assert "live_smoke_test.py" in workflow
    assert "terraform destroy" not in workflow


def test_live_aws_smoke_test_script_compiles():
    import ast
    source = (SERVICE / "tools" / "live_smoke_test.py").read_text(encoding="utf-8")
    ast.parse(source)
