# Security

## Reporting a vulnerability

Please use [Report a vulnerability](https://github.com/otixe/agent-harness/security/advisories/new) (GitHub Security Advisories).
Do not post tokens, credentials, private configuration or personal data in public issues.
If private reporting is not enabled, request that the maintainer enables it without disclosing vulnerability details.

## What this framework does NOT touch

- ❌ AWS credentials (delegated entirely to your `LLMClient` impl)
- ❌ User data persistence (state lives in the Task / TaskResult objects)
- ❌ External services (no network calls outside what your client makes)

## Threat model for orchestrators using this

When you build a real harness on top:

1. **Worker outputs are untrusted** — even if the worker is "your" model, treat
   the output as adversarial input to the next stage. Validate before passing
   to tools or external systems.

2. **Red lines must be enforced at the tool layer**, not just in the prompt.
   "Don't touch secrets" in a system prompt is **not** a security control.

3. **Validator should run on a different model context** — using the same
   model + prompt that produced the output for validation is self-confirmation.

4. **Escalation must be bounded** — set max_iterations aggressively. Runaway
   harnesses are easy to trigger and expensive to recover from.

5. **Audit log every Worker invocation** — you'll need it for incident analysis.

## What you should NEVER commit

- LLM API keys, AWS credentials
- Production system prompts that leak business logic
- Test fixtures with real customer data
- Memory snapshots from production runs

If you cannot use GitHub Security Advisories, email **otixecv@gmail.com** with the subject `SECURITY: agent-harness`. Please do not open a public issue for vulnerabilities.
