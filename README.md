# agent-harness

<div align="center">

🎭 **Multi-agent orchestration framework**

*Planner + Workers + Validators · Escalation rules · Bedrock-native*

[![CI](https://github.com/otixe/agent-harness/actions/workflows/ci.yml/badge.svg)](https://github.com/otixe/agent-harness/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

---

## What this is

A small framework for **multi-agent task execution** with explicit roles,
escalation rules, and validation gates. Designed around lessons learned from
running real production agent systems where:

- A single mega-agent does everything badly
- Pure parallel agents lose track of cross-cutting concerns
- "Just call Claude in a loop" eventually catches fire on long tasks

The pattern: **one Planner, many Workers, one Validator**, with hard rules
about when to escalate and when to deliver.

---

## Architecture

```
                ┌─────────────────┐
                │    User task    │
                └────────┬────────┘
                         ▼
                ┌─────────────────┐
                │    Planner      │  decomposes task into atomic steps
                │ (Sonnet/Opus)   │  produces a TaskGraph
                └────────┬────────┘
                         ▼
            ┌────────────┴────────────┐
            ▼                         ▼
  ┌──────────────────┐      ┌──────────────────┐
  │    Worker A      │      │    Worker B      │   parallel execution
  │  (Sonnet/Haiku)  │      │  (Sonnet/Haiku)  │   bounded by graph
  └────────┬─────────┘      └────────┬─────────┘
           │                         │
           └────────────┬────────────┘
                        ▼
               ┌─────────────────┐
               │   Validator     │   checks results vs success criteria
               │ (different LLM) │   issues escalation if needed
               └────────┬────────┘
                        ▼
        ┌───────────────┴───────────────┐
        │                               │
        ▼                               ▼
   ┌─────────┐                  ┌──────────────┐
   │ Deliver │                  │  Escalate    │
   │         │                  │  to Anvil    │
   │         │                  │  (Opus 4)    │
   └─────────┘                  └──────────────┘
```

Each box is a **role**, not a single agent. Roles can be backed by different
Bedrock models, different system prompts, different tool sets — but they
share a common message bus and task state.

---

## Why this design

### Hard-learned rules from production

1. **Different models for different roles**
   - Planner: Sonnet (fast, good reasoning)
   - Workers: Haiku (cheap, parallelizable)
   - Validator: a *different* model than the workers (avoids self-confirmation)
   - Anvil (escalation): Opus (only when complexity demands it)

2. **One Planner per task, not per turn**
   - Replanning mid-flight = loops and budget overruns
   - Force replan only on validator-triggered escalation

3. **Validator is non-negotiable**
   - "It looked good" → ship to prod → 3am pages
   - Validator runs on a separate context with the success criteria as input

4. **Multi-doc deliverables go in main, not delegated**
   - A subagent stuck after 40 minutes producing 1/3 docs is a known anti-pattern
   - Long single-deliverable tasks belong in the orchestrator's main thread

5. **Red lines are explicit, not implied**
   - Workers cannot touch secrets paths, infra config, CI files unless task-spec'd

---

## Quickstart

```python
from agent_harness import Harness, Task, Worker, Planner, Validator

harness = Harness(
    planner=Planner(model="us.anthropic.claude-sonnet-4-5"),
    workers=[
        Worker(name="research", model="us.anthropic.claude-haiku-4-5"),
        Worker(name="implement", model="us.anthropic.claude-sonnet-4-5"),
    ],
    validator=Validator(model="us.anthropic.claude-haiku-4-5"),
    escalation_model="us.anthropic.claude-opus-4-5",
    max_iterations=5,
)

task = Task(
    description="Audit our 3 firewalls for indirect exposure vectors and produce a report",
    success_criteria=[
        "Report covers all 3 firewalls",
        "Each finding includes severity, policy ID, recommendation",
        "Output is HTML and JSON",
    ],
    red_lines=[
        "Do not modify any firewall configuration",
        "Do not access secrets/ paths",
    ],
)

result = harness.run(task)
print(result.report_path)
print(result.iterations_used)
print(result.escalated)
```

---

## What this is NOT

- ❌ A general-purpose agent framework (use LangGraph or similar)
- ❌ A long-running background daemon (use a real workflow engine)
- ❌ A way to skip thinking about your problem decomposition

It's deliberately small and opinionated. ~800 LOC, no LangChain.

---

## Examples

- [`examples/firewall-audit.md`](examples/firewall-audit.md) — multi-firewall audit
- [`examples/code-review.md`](examples/code-review.md) — automated PR review with escalation

---

## License

MIT — see [LICENSE](LICENSE).

Built by [@otixe](https://github.com/otixe) — DevOps & Agentic Systems Engineer · 🇨🇱
