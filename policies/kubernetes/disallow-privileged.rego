# Revalidated by the dedicated OPA policy-check and complete release-gate workflows.
package kubernetes.disallow_privileged

import rego.v1

violation contains {"msg": msg, "details": {"pod": input.metadata.name}} if {
  container := input.spec.containers[_]
  container.securityContext.privileged == true
  msg := sprintf("Pod %v runs a privileged container", [input.metadata.name])
}

violation contains {"msg": msg, "details": {"pod": input.metadata.name}} if {
  container := input.spec.containers[_]
  container.securityContext.allowPrivilegeEscalation == true
  msg := sprintf("Pod %v allows privilege escalation", [input.metadata.name])
}

violation contains {"msg": msg, "details": {"pod": input.metadata.name}} if {
  not input.spec.securityContext.runAsNonRoot
  msg := sprintf("Pod %v must set runAsNonRoot", [input.metadata.name])
}
