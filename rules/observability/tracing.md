# Distributed Tracing Security

## Data in Spans
- Never capture request/response bodies by default.
- Redact headers: `Authorization`, `Cookie`, `Set-Cookie`, `X-Api-Key`.
- Redact query parameters containing tokens.
- Do not include PII in span attributes.

## Sampling
- Tail-based sampling for high-cardinality services.
- Sensitive transactions always sampled but with redaction.
- Sampling decisions logged.

## Storage
- Trace storage encrypted at rest.
- Access controlled; production traces not readable by all engineers.
- Retention per classification.

## Propagation
- W3C Trace Context; validate incoming trace IDs.
- Reject malformed trace IDs.
- Prevent trace ID injection via user input.

## Forbidden
- Capturing full request bodies in spans.
- Unredacted auth headers in traces.
- Public trace viewers without auth.
