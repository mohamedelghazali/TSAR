job "tsar-app" {
  datacenters = ["dc1"]
  type        = "service"

  group "app" {
    count = 3

    network {
      port "https" {
        to = 8443
      }
    }

    task "app" {
      driver = "docker"

      config {
        image = "registry.example.com/tsar-app@sha256:0000000000000000000000000000000000000000000000000000000000000000"
        ports = ["https"]

        # Least-privilege
        readonly_rootfs = true
        user            = "10001:10001"

        # Limits
        memory = 512
        cpu    = 500
      }

      vault {
        policies = ["tsar-app"]
      }

      template {
        data = <<EOF
{{ with secret "secret/data/app" }}
DB_PASSWORD={{ .Data.data.password }}
JWT_SECRET={{ .Data.data.jwt_secret }}
{{ end }}
EOF
        destination = "secrets/env"
        env         = true
      }

      resources {
        cpu    = 500
        memory = 512
      }

      service {
        name = "tsar-app"
        port = "https"
        tags = ["https", "tsar"]

        check {
          type     = "http"
          path     = "/healthz"
          interval = "10s"
          timeout  = "2s"
        }
      }

      kill_timeout = "30s"

      restart {
        attempts = 3
        delay    = "15s"
        interval = "5m"
        mode     = "fail"
      }
    }
  }

  update {
    max_parallel      = 1
    health_check      = "checks"
    min_healthy_time  = "10s"
    healthy_deadline  = "5m"
    progress_deadline = "10m"
    auto_revert       = true
    canary            = 1
  }
}
