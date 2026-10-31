# LLM07: Insecure Output Handling

## Risk
Model outputs may contain code, markup, or commands that are executed or
rendered without validation, leading to XSS, SSRF, command injection, or
data exfiltration.

## Controls
- Treat all model output as untrusted input.
- Validate output schema before use (JSON schema, regex, allow-list).
- Encode output context-aware before rendering (HTML, JS, URL, CSS, attribute).
- Never pass model output to `eval`, `exec`, `Function()`, or shell.
- Never render model output as HTML without sanitization (DOMPurify).
- Pass generated code through `skills/secure-review` before execution.
- Block markdown image tags pointing to non-allow-listed domains (exfiltration).
- Strip URLs from outputs unless explicitly required.

## Sinks to Protect
| Sink | Control |
|---|---|
| innerHTML | Sanitize with DOMPurify or use textContent |
| SQL query | Parameterize; never concatenate |
| Shell command | Argument array; no shell string |
| File path | Resolve and validate against base dir |
| URL fetch | Allow-list; block private IPs |
| eval/exec | Forbidden entirely |

## Testing
- Injection probes: ask model to generate payloads; verify they are escaped.
- Exfiltration probes: verify image tags and links are blocked.
- Code execution probes: verify generated code is reviewed before run.

## Forbidden
- Rendering model output as HTML without sanitization.
- Executing model-generated code without review.
- Passing model output to any sink without encoding.
