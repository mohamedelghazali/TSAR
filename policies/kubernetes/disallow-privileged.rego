package kubernetes.disallow_privileged

violation[{"msg": msg, "details": {"pod": input.metadata.name}}] {
  container := input.spec.containers[_]
  container.securityContext.privileged == true
  msg := sprintf("Pod %v runs a privileged container", [input.metadata.name])
}

violation[{"msg": msg, "details": {"pod": input.metadata.name}}] {
  container := input.spec.containers[_]
  container.securityContext.allowPrivilegeEscalation == true
  msg := sprintf("Pod %v allows privilege escalation", [input.metadata.name])
}

violation[{"msg": msg, "details": {"pod": input.metadata.name}}] {
  not input.spec.securityContext.runAsNonRoot
  msg := sprintf("Pod %v must set runAsNonRoot", [input.metadata.name])
}
