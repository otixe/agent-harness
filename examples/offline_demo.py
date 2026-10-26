"""Offline demo: the Planner -> Workers -> Validator loop with a scripted client.

No cloud account or API key needed. The scripted client stands in for a model:
it omits a required section on the first pass and includes it once the
validator's feedback is appended to the task. Run: python examples/offline_demo.py
"""

from typing import Any

from agent_harness import Harness, Planner, Task, Validator, Worker


class ScriptedClient:
    """Implements the LLMClient protocol: converse(messages, system_prompt) -> str."""

    def converse(self, messages: list[dict[str, Any]], system_prompt: str = "") -> str:
        prompt = messages[0]["content"][0]["text"]
        if "Previous feedback" in prompt:
            return "Summary of the change.\nRollback plan: revert the release tag."
        return "Summary of the change."


harness = Harness(
    planner=Planner(model="planner-model"),
    workers=[Worker(name="writer", model="worker-model", client=ScriptedClient())],
    validator=Validator(model="validator-model"),  # no client -> substring check of criteria
    escalation_model="escalation-model",
    max_iterations=3,
)

task = Task(
    description="Draft the release note for v1.2",
    success_criteria=["Summary", "Rollback plan"],
)
result = harness.run(task)

print(f"success={result.success} iterations={result.iterations_used} escalated={result.escalated}")
print(f"validator: {result.validation.feedback}")
print("--- output ---")
print(result.output)
