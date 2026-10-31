# SAML 2.0 Security

## Assertions
- Validate signature on the assertion AND on the response.
- Reject assertions without a signature unless the entire response is signed.
- Reject `none` algorithm; require `rsa-sha256` or `ecdsa-sha256` minimum.
- Verify `Issuer` matches the expected IdP entity ID exactly.
- Verify `Audience` matches the SP entity ID exactly.
- `NotBefore`/`NotOnOrAfter` within clock skew (<= 3 minutes).
- `InResponseTo` matches an outstanding authentication request.
- `Destination` matches the ACS URL.

## XML Signature Wrapping
- Use a hardening parser that rejects duplicate IDs and disables DTD.
- Bind signature verification to the assertion by ID, not by position.
- Reject XML with processing instructions or comments inside signed elements.

## Replay Protection
- Track `AssertionID` for the assertion lifetime; reject reuse.
- Store consumed assertion IDs for `NotOnOrAfter` duration.
- Require `SubjectConfirmation` with `bearer` method.

## Single Logout
- Validate `LogoutRequest` signature.
- Reject unsolicited logout without a corresponding session.
- Propagate logout to all SPs.

## Session
- SP session lifetime <= SAML session lifetime.
- Re-authenticate on privilege change.
- No session fixation: regenerate session ID on login.

## Forbidden
- `WantAssertionsSigned=false` with unsigned assertions.
- Unvalidated `RelayState` used as redirect target.
- Disabling `InResponseTo` validation.
- SHA-1 signatures.
