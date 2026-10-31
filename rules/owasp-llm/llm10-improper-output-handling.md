# LLM10: Improper Output Handling

## Risk
Model output is untrusted data. Passing it to downstream interpreters, browsers, databases, shells, file systems, or tools without validation and context-appropriate handling can cause injection, XSS, SSRF, command execution, or data disclosure.

## Controls
- Validate generated output against an explicit schema and allow-list.
- Apply context-aware encoding for HTML, attributes, JavaScript, CSS, URLs, SQL, and shell arguments.
- Sanitize permitted rich text with a maintained sanitizer; prefer text rendering by default.
- Never pass model output to eval, exec, Function constructors, or shell command strings.
- Use parameterized database operations and argument arrays.
- Validate and constrain URLs, redirects, DNS resolution, and private-network access.
- Resolve file paths against an approved base directory and reject traversal.
- Require human approval before executing generated code or irreversible tool actions.
- Log the output-to-sink path with sensitive values redacted.

## Sinks to Protect
| Sink | Required Control |
|---|---|
| HTML/DOM | Context encoding; allow-listed sanitization |
| SQL | Parameterized statements |
| Shell | Fixed executable and argument array; no shell interpolation |
| File system | Canonical path containment |
| URL fetch | Destination allow-list and SSRF defenses |
| Code execution | Isolated sandbox and explicit approval |

## Testing
- Test stored/reflected XSS payloads and attribute-breaking strings.
- Test shell metacharacters, SQL payloads, path traversal, and SSRF targets.
- Verify malformed structured output is rejected closed.
- Confirm generated code cannot execute without policy checks and approval.

## Forbidden
- Executing or interpreting untrusted model output directly.
- Rendering raw model output as HTML.
- Using model-generated paths, URLs, or commands without validation.
