# Revalidated by the dedicated OPA policy-check and complete release-gate workflows.
package kubernetes.disallow_privileged

violation contains msg if {
  input.spec.containers[_].securityContext.privileged == true
  msg := sprintf("container %q is privileged", [input.metadata.name])
}
