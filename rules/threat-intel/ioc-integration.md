# IOC Integration

## Indicator Types
- IP addresses, domains, URLs.
- File hashes (MD5 weak; prefer SHA-256).
- Email addresses, subjects.
- User agents, JA3/JA4 fingerprints.
- Registry keys, file paths.

## Ingestion Pipeline
1. Fetch from feeds (commercial + open source).
2. Validate format and freshness.
3. Score confidence and relevance.
4. Deduplicate.
5. Enrich with context.
6. Publish to detection systems.

## Detection Integration
- SIEM rules for network IOCs.
- EDR for file hashes and process IOCs.
- WAF for malicious IPs and URLs.
- DNS sinkhole for known-bad domains.

## Lifecycle
- IOCs expire (default 30 days) unless confirmed malicious.
- False positives tracked and suppressed.
- Source reputation maintained.

## Forbidden
- Blocking on low-confidence IOCs without review.
- Ingesting untrusted feeds without validation.
- Retaining IOCs beyond useful life.
