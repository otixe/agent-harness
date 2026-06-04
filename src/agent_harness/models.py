"""Pydantic models: Task, TaskStep, TaskResult."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class Task(BaseModel):
    """A user-supplied task to orchestrate."""

    model_config = ConfigDict(frozen=True)

    description: str
    success_criteria: list[str] = Field(default_factory=list)
    red_lines: list[str] = Field(default_factory=list)
    max_iterations: int = 5


class TaskStep(BaseModel):
    """A single atomic step in the planner's decomposition."""

    model_config = ConfigDict(frozen=True)

    step_id: str
    description: str
    worker: str  # worker name to assign
    depends_on: list[str] = Field(default_factory=list)
    output: str | None = None
    status: Literal["pending", "in_progress", "completed", "failed"] = "pending"


class ValidationResult(BaseModel):
    """Output of the Validator role."""

    model_config = ConfigDict(frozen=True)

    passed: bool
    feedback: str
    failed_criteria: list[str] = Field(default_factory=list)


class TaskResult(BaseModel):
    """Final result of a Harness.run() call."""

    success: bool
    output: str
    iterations_used: int
    escalated: bool = False
    steps: list[TaskStep] = Field(default_factory=list)
    validation: ValidationResult | None = None
