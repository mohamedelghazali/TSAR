# STIX and TAXII

## STIX 2.1
- Use STIX 2.1 for indicator, malware, campaign, threat-actor sharing.
- Every object has: id (UUIDv4), type, created, modified, spec_version.
- Relationships modeled as SROs (relationship, sighting).
- Confidence scores 0-100.
- TLP marking (TLP:CLEAR, TLP:GREEN, TLP:AMBER, TLP:AMBER+STRICT, TLP:RED).

## TAXII 2.1
- HTTPS only; client authentication via mTLS or OAuth.
- Collections scoped per sharing community.
- Versioning: objects immutable; updates via new version.

## Ingestion
- Validate objects against STIX schema.
- Deduplicate by id + modified.
- Enrich with local context (asset criticality, exposure).
- Store with retention per TLP.

## Sharing
- Respect TLP markings; enforce in export.
- Attribution preserved.
- Sanitization for PII before sharing.

## Forbidden
- Sharing TLP:RED outside its designated recipients.
- Ingestion without schema validation.
- Storing indicators beyond their useful life without review.
