datacenter = "dc1"
data_dir   = "/opt/nomad/data"
bind_addr  = "0.0.0.0"

advertise {
  http = "10.0.1.10"
  rpc  = "10.0.1.10"
  serf = "10.0.1.10"
}

server {
  enabled          = true
  bootstrap_expect = 3
}

client {
  enabled = true

  reserved {
    cpu            = 500
    memory         = 512
    disk           = 1024
    reserved_ports = "22,8500-8503"
  }
}

tls {
  http = true
  rpc  = true

  ca_file   = "/etc/nomad.d/tls/ca.pem"
  cert_file = "/etc/nomad.d/tls/server.pem"
  key_file  = "/etc/nomad.d/tls/server-key.pem"

  verify_server_hostname = true
  verify_https_client    = true
}

acl {
  enabled    = true
  token_ttl  = "30s"
  policy_ttl = "60s"
}

telemetry {
  collection_interval        = "5s"
  prometheus_metrics         = true
  disable_hostname           = true
  publish_allocation_metrics = true
  publish_node_metrics       = true
}

vault {
  enabled          = true
  address          = "https://vault.internal.example.com:8200"
  ca_file          = "/etc/nomad.d/tls/ca.pem"
  create_from_role = "nomad-cluster"
}
