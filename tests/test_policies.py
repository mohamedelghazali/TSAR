"""Verify OPA policies compile and detect violations."""
import shutil
import subprocess
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parent.parent
POLICIES = ROOT / "policies"

OPA = shutil.which("opa")

pytestmark = pytest.mark.skipif(OPA is None, reason="opa not installed")

def test_policies_compile():
    r = subprocess.run([OPA, "check", str(POLICIES)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr

def test_disallow_privileged(tmp_path):
    pod = tmp_path / "pod.json"
    pod.write_text('''{
      "metadata": {"name": "bad"},
      "spec": {"containers": [{"name": "c", "securityContext": {"privileged": true}}]}
    }''')
    r = subprocess.run(
        [OPA, "eval", "--format=json",
         "--data", str(POLICIES / "kubernetes"),
         "--input", str(pod),
         "data.kubernetes.disallow_privileged.violation"],
        capture_output=True, text=True,
    )
    assert r.returncode == 0
    assert '"bad"' in r.stdout or "privileged" in r.stdout
