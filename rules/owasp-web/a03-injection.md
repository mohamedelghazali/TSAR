# A03: Injection

## Scope
SQL, NoSQL, LDAP, XPath, OS command, template, header, log injection.

## Controls
- Parameterized queries exclusively; no string concatenation into query.
- ORM query builders with bound parameters.
- OS commands via argument arrays, never shell strings.
- Template engines with auto-escaping enabled; no raw rendering of user input.
- Allow-list validation on every user-controlled field before it reaches any sink.
- Context-aware output encoding (HTML, JS, URL, CSS, attribute).

## Forbidden
- \`eval\`, \`exec\`, \`Function()\`, \`setTimeout("...")\`.
- \`innerHTML =\` with unsanitized input.
- \`dangerouslySetInnerHTML\` without sanitizer (DOMPurify or equivalent).

## Testing
- SAST in CI via skills/secure-review.
- Fuzz inputs on every endpoint accepting structured data.
