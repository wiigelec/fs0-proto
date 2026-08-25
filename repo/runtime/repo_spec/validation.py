"""Execution of mechanically runnable validations from an accepted Plan."""
from __future__ import annotations

from dataclasses import dataclass
import os
import subprocess

from .errors import ConformanceError
from .plan import LogicalPlan
from .repository import Repository


_EXECUTABLE_KINDS = {"unit", "schema"}
_VALIDATION_TIMEOUT_SECONDS = 120


@dataclass(frozen=True)
class ValidationResult:
    id: str
    kind: str
    command: str
    returncode: int
    stdout: str
    stderr: str

    @property
    def passed(self) -> bool:
        return self.returncode == 0

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "kind": self.kind,
            "command": self.command,
            "returncode": self.returncode,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "disposition": "PASS" if self.passed else "FAIL",
        }


def run_plan_validations(
    repository: Repository,
    plan: LogicalPlan,
) -> tuple[ValidationResult, ...]:
    required = {vid for fc in plan.file_changes for vid in fc.validation_ids}
    entries = plan.validation.get("validation")
    if not isinstance(entries, list):
        raise ConformanceError(
            "invalid-plan-validation",
            "Plan validation document requires validation array",
        )

    results = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue

        validation_id = entry.get("id")
        kind = entry.get("kind")
        if validation_id not in required or kind not in _EXECUTABLE_KINDS:
            continue

        command = entry.get("command")
        if not isinstance(command, str) or not command.strip():
            raise ConformanceError(
                "missing-validation-command",
                f"{validation_id} requires an executable command",
            )

        env = dict(os.environ)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env["FS0_PLAN_VALIDATION_CHILD"] = "1"

        try:
            proc = subprocess.run(
                command,
                cwd=repository.root,
                shell=True,
                executable="/bin/sh",
                text=True,
                capture_output=True,
                env=env,
                timeout=_VALIDATION_TIMEOUT_SECONDS,
            )
        except subprocess.TimeoutExpired as exc:
            raise ConformanceError(
                "plan-validation-timeout",
                f"{validation_id} exceeded {_VALIDATION_TIMEOUT_SECONDS}s",
            ) from exc

        result = ValidationResult(
            validation_id,
            kind,
            command,
            proc.returncode,
            proc.stdout,
            proc.stderr,
        )
        results.append(result)

        if not result.passed:
            raise ConformanceError(
                "plan-validation-failed",
                f"{validation_id} failed: {proc.stderr.strip() or proc.stdout.strip()}",
            )

    return tuple(results)
