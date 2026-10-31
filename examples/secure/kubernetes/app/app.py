#!/usr/bin/env python3
"""Minimal HTTPS health application used by the TSAR Kubernetes example."""
import os
import ssl
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path not in ("/healthz", "/ready"):
            self.send_error(404)
            return
        body = b"ok\n"
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, _format, *_args):
        return


def main():
    cert_file = os.environ.get("TLS_CERT_FILE", "/etc/tls/tls.crt")
    key_file = os.environ.get("TLS_KEY_FILE", "/etc/tls/tls.key")
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    context.load_cert_chain(certfile=cert_file, keyfile=key_file)

    server = ThreadingHTTPServer(("0.0.0.0", 8443), HealthHandler)
    server.socket = context.wrap_socket(server.socket, server_side=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
