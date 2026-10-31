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


def test_tf_security_group_rules_are_separate_and_restricted():
    text = (TF / "security-groups.tf").read_text()
    assert "aws_vpc_security_group_egress_rule" in text
    assert "aws_vpc_security_group_ingress_rule" in text
    assert "referenced_security_group_id" in text
    assert "cidr_blocks" not in text


def test_k8s_deployment_uses_buildable_local_image_and_configmap():
    text = (K8S / "deployment.yaml").read_text()
    assert "tsar-example-app:local" in text
    assert "0000000000000000000000000000000000000000000000000000000000000000" not in text
    assert "configMapRef" in text
    assert "tsar-app-tls" in text


def test_k8s_local_app_source_and_configmap_exist():
    assert (K8S / "app" / "Dockerfile").is_file()
    assert (K8S / "app" / "app.py").is_file()
    assert (K8S / "configmap.yaml").is_file()
