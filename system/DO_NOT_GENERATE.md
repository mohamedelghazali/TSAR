# DO NOT GENERATE — Hard Stops

The following patterns MUST cause the agent to refuse generation.

## Secrets
- Strings matching `AKIA[0-9A-Z]{16}`, `sk-[A-Za-z0-9]{20,}`, `ghp_[A-Za-z0-9]{36}`, `-----BEGIN .* PRIVATE KEY-----`.
- Database URLs containing `://user:password@`.
- JWT secrets, HMAC keys, or encryption keys as literals.

## Cryptography
- `AES/ECB/*`, `DES`, `3DES`, `RC4`, `MD5`, `SHA1` for security purposes.
- `Math.random()`, `rand()`, `java.util.Random` for security tokens.
- `==` or `.equals()` for comparing secrets or tokens.
- Custom cipher, custom hash, custom KDF.

## Injection
- `eval(`, `exec(`, `new Function(`, `setTimeout("...")`, `setInterval("...")`.
- String concatenation into `query(`, `execute(`, `raw(`, `execSync(`, `system(`.
- `innerHTML =` with unsanitized input; `dangerouslySetInnerHTML` without sanitizer.

## Network
- `verify=False`, `rejectUnauthorized: false`, `InsecureSkipVerify: true`.
- `Access-Control-Allow-Origin: *` on authenticated endpoints.
- WebSocket without origin validation.

## AI / Agents
- Concatenating user input into the system prompt string.
- Passing tool output as instructions to the model.
- Granting `*` permissions to an agent tool.
- Storing conversation history without redaction of secrets and PII.
