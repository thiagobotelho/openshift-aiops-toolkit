from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal

SCHEMA_VERSION = "1.0"
TOOLKIT_VERSION = "0.1.0"

ComponentStatus = Literal[
    "ok",
    "warning",
    "critical",
    "informational",
    "not_applicable",
    "permission_denied",
    "unavailable",
    "not_checked",
]
ExecutionStatus = Literal["success", "partial", "failed", "cancelled"]
HealthStatus = Literal["healthy", "warning", "critical", "unknown"]


@dataclass
class ClusterIdentity:
    name: str | None = None
    context: str | None = None
    api_server: str | None = None
    user: str | None = None
    version: str | None = None
    platform: str | None = None
    control_plane_topology: str | None = None
    infrastructure_topology: str | None = None
    infrastructure_name: str | None = None
    nodes: int | None = None
    network: str | None = None


@dataclass
class Finding:
    severity: ComponentStatus
    title: str
    message: str
    resource: str | None = None
    namespace: str | None = None
    evidence: str | None = None
    next_step: str | None = None


@dataclass
class Evidence:
    name: str
    command: list[str] = field(default_factory=list)
    exit_code: int | None = None
    path: str | None = None
    summary: str | None = None
    truncated: bool = False


@dataclass
class Limitation:
    status: ComponentStatus
    component: str
    reason: str


@dataclass
class ExecutionMetadata:
    started_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    finished_at: str | None = None
    duration_ms: int = 0
    toolkit_version: str = TOOLKIT_VERSION


@dataclass
class ToolResponse:
    tool: str
    execution_status: ExecutionStatus = "success"
    health_status: HealthStatus = "unknown"
    summary: str = ""
    cluster: ClusterIdentity = field(default_factory=ClusterIdentity)
    findings: list[Finding] = field(default_factory=list)
    evidence: list[Evidence] = field(default_factory=list)
    limitations: list[Limitation] = field(default_factory=list)
    metadata: ExecutionMetadata = field(default_factory=ExecutionMetadata)
    data: Any | None = None
    schema_version: str = SCHEMA_VERSION

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def response_from_error(tool: str, message: str, *, execution_status: ExecutionStatus = "failed") -> ToolResponse:
    return ToolResponse(
        tool=tool,
        execution_status=execution_status,
        health_status="unknown",
        summary=message,
        findings=[Finding("critical", "Falha na execução", message)],
    )
