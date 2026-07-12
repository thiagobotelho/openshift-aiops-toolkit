from __future__ import annotations

import json
import os
import shutil
import sys
from typing import Any

from .sanitizers import sanitize_text
from .schemas import ToolResponse

STATUS_LABELS = {
    "ok": "OK",
    "warning": "ALERTA",
    "critical": "CRÍTICO",
    "informational": "INFORMATIVO",
    "not_applicable": "NÃO APLICÁVEL",
    "permission_denied": "SEM PERMISSÃO",
    "unavailable": "INDISPONÍVEL",
    "not_checked": "NÃO VERIFICADO",
}
ASCII_STATUS_LABELS = {
    "ok": "[OK]",
    "warning": "[ALERTA]",
    "critical": "[CRITICO]",
    "informational": "[INFO]",
    "not_applicable": "[N/A]",
    "permission_denied": "[SEM PERMISSAO]",
    "unavailable": "[INDISPONIVEL]",
    "not_checked": "[NAO VERIFICADO]",
}
UNICODE_STATUS_LABELS = {
    "ok": "✓ OK",
    "warning": "! ALERTA",
    "critical": "✗ CRÍTICO",
    "informational": "i INFORMATIVO",
    "not_applicable": "- NÃO APLICÁVEL",
    "permission_denied": "! SEM PERMISSÃO",
    "unavailable": "! INDISPONÍVEL",
    "not_checked": "? NÃO VERIFICADO",
}
COLORS = {
    "ok": "\033[32m",
    "warning": "\033[33m",
    "critical": "\033[31m",
    "informational": "\033[36m",
    "not_applicable": "\033[90m",
    "permission_denied": "\033[35m",
    "unavailable": "\033[31m",
    "not_checked": "\033[90m",
}
RESET = "\033[0m"


def supports_color(no_color: bool = False) -> bool:
    return bool(not no_color and not os.environ.get("NO_COLOR") and sys.stdout.isatty())


def supports_unicode(ascii_only: bool = False) -> bool:
    if ascii_only:
        return False
    encoding = (sys.stdout.encoding or "").lower()
    return "utf" in encoding


def terminal_width(default: int = 100) -> int:
    return shutil.get_terminal_size((default, 24)).columns


def truncate_text(value: str | None, width: int = 120) -> str:
    text = sanitize_text(value or "")
    if len(text) <= width:
        return text
    return text[: max(0, width - 15)] + " ...[truncado]"


def status_label(status: str, *, ascii_only: bool = False, color: bool = False) -> str:
    labels = ASCII_STATUS_LABELS if ascii_only else UNICODE_STATUS_LABELS
    label = labels.get(status, STATUS_LABELS.get(status, status.upper()))
    if color and status in COLORS:
        return COLORS[status] + label + RESET
    return label


def section(title: str, *, ascii_only: bool = False) -> str:
    line = "-" if ascii_only else "─"
    return f"\n{title}\n{line * min(60, max(10, len(title)))}"


def key_values(rows: list[tuple[str, Any]]) -> str:
    width = max((len(label) for label, _ in rows), default=0)
    rendered = []
    for label, value in rows:
        rendered.append(f"  {label + ':':<{width + 1}} {value if value not in {None, ''} else 'não informado'}")
    return "\n".join(rendered)


def table(headers: list[str], rows: list[list[Any]], *, max_width: int | None = None) -> str:
    max_width = max_width or terminal_width()
    data = [[str(item) for item in row] for row in rows]
    widths = [len(header) for header in headers]
    for row in data:
        for index, item in enumerate(row):
            widths[index] = max(widths[index], min(len(item), 40))
    total = sum(widths) + 3 * (len(widths) - 1)
    if total > max_width and rows:
        rendered = []
        for row in data:
            rendered.append("\n".join(f"- {headers[i]}: {truncate_text(row[i], 80)}" for i in range(len(headers))))
            rendered.append("")
        return "\n".join(rendered).strip()
    fmt = "   ".join(f"{{:<{width}}}" for width in widths)
    lines = [fmt.format(*headers)]
    lines.append("   ".join("-" * width for width in widths))
    for row in data:
        lines.append(fmt.format(*(truncate_text(row[i], widths[i]) for i in range(len(headers)))))
    return "\n".join(lines)


def render_human(response: ToolResponse, *, ascii_only: bool = False, no_color: bool = False, quiet: bool = False, verbose: bool = False, debug: bool = False) -> str:
    color = supports_color(no_color)
    if quiet:
        return f"{status_label(response.health_status if response.health_status != 'healthy' else 'ok', ascii_only=ascii_only, color=color)} {response.summary}".strip()
    c = response.cluster
    lines = [
        "OpenShift AIOps Toolkit",
        ("-" if ascii_only else "─") * 60,
        section("Cluster", ascii_only=ascii_only),
        key_values(
            [
                ("Nome", c.name),
                ("API", c.api_server),
                ("Contexto", c.context),
                ("Usuário", c.user),
                ("Versão", c.version),
                ("Plataforma", c.platform),
                ("Control Plane", c.control_plane_topology),
                ("Infraestrutura", c.infrastructure_topology),
                ("Nodes", c.nodes),
                ("Rede", c.network),
            ]
        ),
        section("Resumo", ascii_only=ascii_only),
        f"  Execução: {response.execution_status}",
        f"  Saúde:    {response.health_status}",
        f"  Resultado: {response.summary or 'sem resumo'}",
    ]
    if response.findings:
        lines.append(section("Achados prioritários", ascii_only=ascii_only))
        for finding in response.findings:
            lines.append(f"{status_label(finding.severity, ascii_only=ascii_only, color=color)} {finding.title}")
            if finding.message:
                lines.append(f"  {truncate_text(finding.message, 160)}")
            if finding.evidence:
                lines.append(f"  Evidência: {truncate_text(finding.evidence, 160)}")
            if finding.next_step:
                lines.append(f"  Próxima validação: {finding.next_step}")
    if response.limitations:
        lines.append(section("Limitações", ascii_only=ascii_only))
        for limitation in response.limitations:
            lines.append(f"- {limitation.component}: {status_label(limitation.status, ascii_only=ascii_only)} — {limitation.reason}")
    if verbose or debug:
        lines.append(section("Evidências", ascii_only=ascii_only))
        if response.evidence:
            lines.append(table(["NOME", "EXIT", "RESUMO"], [[e.name, e.exit_code, e.summary or ""] for e in response.evidence]))
        else:
            lines.append("  nenhuma evidência registrada")
    if debug:
        lines.append(section("Debug", ascii_only=ascii_only))
        lines.append(json.dumps(response.to_dict().get("metadata", {}), ensure_ascii=False, indent=2))
    return "\n".join(lines)


def render_markdown(response: ToolResponse) -> str:
    payload = response.to_dict()
    lines = [
        f"# {response.tool}",
        "",
        f"- Execution status: `{response.execution_status}`",
        f"- Health status: `{response.health_status}`",
        f"- Summary: {response.summary}",
        "",
        "## Cluster",
        "",
    ]
    for key, value in payload.get("cluster", {}).items():
        lines.append(f"- {key}: {value if value not in {None, ''} else 'não informado'}")
    if response.findings:
        lines += ["", "## Findings", ""]
        for finding in payload["findings"]:
            lines.append(f"- **{finding['severity']}** — {finding['title']}: {finding['message']}")
    return "\n".join(lines) + "\n"


def render_yaml(payload: dict[str, Any]) -> str:
    try:
        import yaml  # type: ignore[import-not-found]
    except Exception as exc:
        raise RuntimeError("Formato YAML requer PyYAML instalado no ambiente Python") from exc
    return yaml.safe_dump(payload, allow_unicode=True, sort_keys=False)


def render_response(response: ToolResponse, *, output: str = "human", ascii_only: bool = False, no_color: bool = False, quiet: bool = False, verbose: bool = False, debug: bool = False) -> str:
    payload = response.to_dict()
    if output == "human":
        return render_human(response, ascii_only=ascii_only, no_color=no_color, quiet=quiet, verbose=verbose, debug=debug)
    if output == "json":
        return json.dumps(payload, ensure_ascii=False, indent=2)
    if output == "yaml":
        return render_yaml(payload)
    if output == "markdown":
        return render_markdown(response)
    if output == "raw":
        return sanitize_text(str(response.data if response.data is not None else payload))
    raise ValueError(f"formato de saída não suportado: {output}")
