"""Role abstractions: Planner, Worker, Validator.

Each role wraps a Bedrock model invocation with a role-specific system prompt.
Roles are pluggable — bring your own LLM client (or use the default Bedrock one).
"""

from __future__ import annotations

from typing import Any, Protocol

from .models import Task, TaskStep, ValidationResult


class LLMClient(Protocol):
    """Minimal LLM interface roles depend on."""

    def converse(
        self,
        messages: list[dict[str, Any]],
        system_prompt: str = "",
    ) -> str: ...


_PLANNER_PROMPT = """\
You are a Planner. Decompose the user's task into 2-8 atomic steps.

Each step must:
- Be independently executable
- Specify which Worker should run it (use the worker names provided)
- Declare dependencies on other steps by their step_id

Output format: JSON array of steps.

Respect red lines: if a task implies violating a red line, refuse with an
explanation rather than producing a plan.
"""

_VALIDATOR_PROMPT = """\
You are a Validator. You receive:
- The original task with success criteria
- The output produced by Workers

Check whether each success criterion is satisfied.
Output: {"passed": bool, "feedback": str, "failed_criteria": [list]}.

Be strict: if a criterion is partially met, mark as failed and explain.
"""


class Planner:
    """Decomposes a Task into TaskSteps."""

    def __init__(
        self,
        model: str,
        client: LLMClient | None = None,
        system_prompt: str = _PLANNER_PROMPT,
    ) -> None:
        self.model = model
        self.client = client
        self.system_prompt = system_prompt

    def plan(self, task: Task, available_workers: list[str]) -> list[TaskStep]:
        """Return a list of TaskSteps."""
        if self.client is None:
            # Default fallback for tests / dry-runs: produce a trivial plan
            return [
                TaskStep(
                    step_id="step-1",
                    description=task.description,
                    worker=available_workers[0] if available_workers else "default",
                )
            ]
        # Real planner would parse JSON from LLM response — kept minimal here
        # to keep the harness testable without live Bedrock.
        prompt = (
            f"Task: {task.description}\n"
            f"Success criteria: {task.success_criteria}\n"
            f"Red lines: {task.red_lines}\n"
            f"Available workers: {available_workers}\n"
        )
        # The framework deliberately does NOT lock you into a specific JSON schema
        # — bring your own parser if your client returns structured output.
        _response = self.client.converse(
            messages=[{"role": "user", "content": [{"text": prompt}]}],
            system_prompt=self.system_prompt,
        )
        # Skeleton: returning trivial plan; production users should parse `_response`
        return [
            TaskStep(
                step_id="step-1",
                description=task.description,
                worker=available_workers[0] if available_workers else "default",
            )
        ]


class Worker:
    """Executes a single step."""

    def __init__(
        self,
        name: str,
        model: str,
        client: LLMClient | None = None,
        system_prompt: str = "You are a focused executor. Complete the assigned step.",
    ) -> None:
        self.name = name
        self.model = model
        self.client = client
        self.system_prompt = system_prompt

    def execute(self, step: TaskStep, context: dict[str, Any]) -> str:
        """Return the step's output."""
        if self.client is None:
            return f"[{self.name}] executed: {step.description}"
        message = f"Step: {step.description}\nContext: {context}\n"
        return self.client.converse(
            messages=[{"role": "user", "content": [{"text": message}]}],
            system_prompt=self.system_prompt,
        )


class Validator:
    """Checks Worker outputs against success criteria."""

    def __init__(
        self,
        model: str,
        client: LLMClient | None = None,
        system_prompt: str = _VALIDATOR_PROMPT,
    ) -> None:
        self.model = model
        self.client = client
        self.system_prompt = system_prompt

    def validate(self, task: Task, output: str) -> ValidationResult:
        """Return whether the output satisfies the task's success criteria."""
        if self.client is None:
            # Default fallback: assume success if every criterion appears in output
            failed = [c for c in task.success_criteria if c.lower() not in output.lower()]
            return ValidationResult(
                passed=len(failed) == 0,
                feedback="auto-validation (no LLM client provided)",
                failed_criteria=failed,
            )
        prompt = (
            f"Task: {task.description}\n"
            f"Success criteria: {task.success_criteria}\n"
            f"Worker output: {output}"
        )
        _response = self.client.converse(
            messages=[{"role": "user", "content": [{"text": prompt}]}],
            system_prompt=self.system_prompt,
        )
        # Skeleton: production code should parse JSON from `_response`
        return ValidationResult(passed=True, feedback="validated", failed_criteria=[])
