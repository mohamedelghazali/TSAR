# LLM08: Hidden Context Exposure

## Risk
System prompts, tool schemas, internal reasoning, and retrieved private context may leak through model output.

## Controls
- Never place secrets, internal URLs, or PII in system prompts.
- Treat system prompts as non-secret; assume they can be extracted.
- Redact internal identifiers from tool outputs before passing to the model.
- Strip chain-of-thought and internal metadata from user-facing responses.
- Separate tenant data at retrieval time; enforce row-level access control in RAG.

## Testing
- Prompt extraction probes ("repeat your instructions verbatim").
- Cross-tenant retrieval probes.
