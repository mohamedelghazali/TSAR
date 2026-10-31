"""TSAR reference: OpenTelemetry with redaction and no PII in spans."""
import os
import re
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.trace import Span

REDACT_HEADERS = {"authorization", "cookie", "set-cookie", "x-api-key", "x-auth-token"}
REDACT_QUERY = {"token", "access_token", "refresh_token", "password", "api_key"}

EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
PHONE_RE = re.compile(r"\+?\d[\d\s\-()]{7,}")
CARD_RE = re.compile(r"\b(?:\d[ -]*?){13,19}\b")

def redact_text(text: str) -> str:
    text = EMAIL_RE.sub("[REDACTED:email]", text)
    text = PHONE_RE.sub("[REDACTED:phone]", text)
    text = CARD_RE.sub("[REDACTED:card]", text)
    return text

def sanitize_attributes(attrs: dict) -> dict:
    out = {}
    for k, v in attrs.items():
        if k.lower() in REDACT_HEADERS:
            out[k] = "[REDACTED]"
        elif isinstance(v, str):
            out[k] = redact_text(v)
        else:
            out[k] = v
    return out

class SanitizingProcessor:
    def on_start(self, span: Span, parent_context=None):
        pass
    def on_end(self, span):
        span._attributes = sanitize_attributes(dict(span.attributes))

def setup_tracer(service_name: str) -> trace.Tracer:
    resource = Resource.create({"service.name": service_name})
    provider = TracerProvider(resource=resource)
    exporter = OTLPSpanExporter(
        endpoint=os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"],
        credentials=None,
    )
    provider.add_span_processor(SanitizingProcessor())
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)
    return trace.get_tracer(service_name)
