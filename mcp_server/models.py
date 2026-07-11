from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

@dataclass
class CommandResult:
    command: list[str]
    exit_code: int
    stdout: str
    stderr: str
    duration_seconds: float
    timed_out: bool = False
    truncated: bool = False
    def to_dict(self) -> dict[str, Any]:
        return {"command": self.command, "exit_code": self.exit_code, "stdout": self.stdout, "stderr": self.stderr, "duration_seconds": round(self.duration_seconds, 3), "timed_out": self.timed_out, "truncated": self.truncated}

@dataclass
class EvidenceFile:
    path: str
    sha256: str
    size_bytes: int
    sanitized: bool = True

@dataclass
class EvidenceManifest:
    cluster: str
    environment: str
    context: str
    server: str = "unknown"
    user: str = "unknown"
    started_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    finished_at: str | None = None
    toolkit_version: str = "0.1.0"
    commands: list[dict[str, Any]] = field(default_factory=list)
    files: list[EvidenceFile] = field(default_factory=list)
    sanitization_status: str = "enabled"
    def finish(self) -> None:
        self.finished_at = datetime.now(timezone.utc).isoformat()
    def to_dict(self) -> dict[str, Any]:
        return {"cluster": self.cluster, "environment": self.environment, "context": self.context, "server": self.server, "user": self.user, "started_at": self.started_at, "finished_at": self.finished_at, "toolkit_version": self.toolkit_version, "commands": self.commands, "files": [f.__dict__ for f in self.files], "sanitization_status": self.sanitization_status}
