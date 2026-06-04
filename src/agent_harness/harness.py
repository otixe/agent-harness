"""Harness: orchestrates Planner → Workers → Validator with escalation logic."""

from __future__ import annotations

from .models import Task, TaskResult, TaskStep, ValidationResult
from .roles import Planner, Validator, Worker


class Harness:
    """Multi-agent task orchestrator."""

    def __init__(
        self,
        planner: Planner,
        workers: list[Worker],
        validator: Validator,
        escalation_model: str | None = None,
        max_iterations: int = 5,
    ) -> None:
        self.planner = planner
        self.workers = {w.name: w for w in workers}
        self.validator = validator
        self.escalation_model = escalation_model
        self.max_iterations = max_iterations

    def run(self, task: Task) -> TaskResult:
        """Run the full Planner → Workers → Validator loop."""
        iteration = 0
        steps: list[TaskStep] = []
        accumulated_output = ""
        last_validation: ValidationResult | None = None

        while iteration < min(task.max_iterations, self.max_iterations):
            iteration += 1
            steps = self.planner.plan(task, available_workers=list(self.workers))
            accumulated_output = self._execute_steps(steps)

            last_validation = self.validator.validate(task, accumulated_output)
            if last_validation.passed:
                return TaskResult(
                    success=True,
                    output=accumulated_output,
                    iterations_used=iteration,
                    steps=steps,
                    validation=last_validation,
                )

            # Validation failed — feed feedback back into next iteration
            task = task.model_copy(
                update={
                    "description": task.description
                    + f"\n\n[Previous feedback: {last_validation.feedback}]"
                }
            )

        # Out of iterations — escalate if escalation_model is configured
        escalated = self.escalation_model is not None
        return TaskResult(
            success=False,
            output=accumulated_output,
            iterations_used=iteration,
            escalated=escalated,
            steps=steps,
            validation=last_validation,
        )

    def _execute_steps(self, steps: list[TaskStep]) -> str:
        """Run each step in dependency order, return combined output."""
        outputs: dict[str, str] = {}
        for step in steps:
            worker = self.workers.get(step.worker)
            if worker is None:
                outputs[step.step_id] = f"[ERROR] Unknown worker: {step.worker}"
                continue
            context = {dep: outputs.get(dep, "") for dep in step.depends_on}
            outputs[step.step_id] = worker.execute(step, context)
        return "\n\n".join(f"## {sid}\n{out}" for sid, out in outputs.items())
