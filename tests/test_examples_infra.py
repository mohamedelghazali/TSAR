"""Verify Kubernetes and Terraform examples are structurally valid."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
K8S = ROOT / "examples" / "secure" / "kubernetes"
TF = ROOT / "examples" / "secure" / "terraform"

def test_k8s_files_present():
    for name in ["namespace.yaml", "deployment.yaml", "serviceaccount.yaml",
                 "networkpolicy.yaml", "rbac.yaml", "secret.yaml",
                 "poddisruptionbudget.yaml"]:
        assert (K8S / name).exists(), f"missing {name}"

def test_k8s_deployment_hardened():
    text = (K8S / "deployment.yaml").read_text()
    assert "runAsNonRoot: true" in text
    assert "readOnlyRootFilesystem: true" in text
    assert "allowPrivilegeEscalation: false" in text
    assert "automountServiceAccountToken: false" in text
    assert "seccompProfile" in text

def test_k8s_networkpolicy_default_deny():
    text = (K8S / "networkpolicy.yaml").read_text()
    assert "name: default-deny" in text
    assert "podSelector: {}" in text

def test_tf_files_present():
    for name in ["main.tf", "variables.tf", "kms.tf", "s3.tf", "rds.tf",
                 "iam.tf", "security-groups.tf", "outputs.tf"]:
        assert (TF / name).exists(), f"missing {name}"

def test_tf_s3_hardened():
    text = (TF / "s3.tf").read_text()
    assert "block_public_acls" in text
    assert "sse_algorithm" in text
    assert "aws:kms" in text

def test_tf_rds_encrypted():
    text = (TF / "rds.tf").read_text()
    assert "storage_encrypted" in text
    assert "publicly_accessible" in text
    assert "false" in text


def test_tf_database_rules_reference_the_rds_security_group():
    text = (TF / "security-groups.tf").read_text()
    assert 'resource "aws_vpc_security_group_egress_rule" "app_to_rds"' in text
    assert 'resource "aws_vpc_security_group_ingress_rule" "rds_from_app"' in text
    assert "referenced_security_group_id = aws_security_group.rds.id" in text
    assert "referenced_security_group_id = aws_security_group.app.id" in text
    assert "cidr_blocks = var.private_subnet_cidrs" not in text


def test_k8s_tls_secret_is_managed_externally():
    text = (K8S / "secret.yaml").read_text()
    assert "name: tsar-app-tls" in text
    assert "type: kubernetes.io/tls" in text
    assert "key: tsar/app/tls_crt" in text
    assert "key: tsar/app/tls_key" in text
    assert "-----BEGIN" not in text


def test_k8s_deployment_marks_image_as_required_release_input():
    text = (K8S / "deployment.yaml").read_text()
    assert "image: registry.example.com/tsar-app@sha256:REPLACE_WITH_VERIFIED_64_HEX_DIGEST" in text


def test_infra_workflow_validates_external_secret_with_pinned_schema():
    text = (ROOT / ".github" / "workflows" / "infra-validation.yml").read_text()
    assert "3eb90d47aba8d61919d4419dd38301536e32a94b" in text
    assert "{{.Group}}/{{.ResourceKind}}_{{.ResourceAPIVersion}}.json" in text
    assert "-ignore-missing-schemas" not in text
