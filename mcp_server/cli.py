from __future__ import annotations

import argparse
import json
import time
from typing import Any, Sequence

from .capabilities import discover_capabilities
from .commands import detect_cluster_name, run_oc
from .formatters import render_response
from .schemas import ClusterIdentity, Evidence, Finding, Limitation, ToolResponse

READONLY_COMMANDS: dict[str, list[str]] = {
    "cluster": ["get", "clusterversion", "-o", "json"],
    "operators": ["get", "clusteroperators", "-o", "wide"],
    "nodes": ["get", "nodes", "-o", "wide"],
    "pods": ["get", "pods", "-A", "--field-selector=status.phase!=Running", "-o", "wide"],
    "storage": ["get", "pvc", "-A", "-o", "wide"],
    "network": ["get", "network.config.openshift.io", "cluster", "-o", "yaml"],
    "ingress": ["get", "ingresscontrollers", "-A", "-o", "wide"],
    "dns": ["get", "clusteroperator", "dns", "-o", "yaml"],
    "monitoring": ["get", "clusteroperator", "monitoring", "-o", "yaml"],
    "olm": ["get", "clusterserviceversions,subscriptions,installplans,catalogsources", "-A", "-o", "wide"],
    "certificates": ["get", "csr", "-o", "wide"],
    "capacity": ["get", "nodes", "-o", "json"],
    "events": ["get", "events", "-A", "--field-selector=type=Warning", "--sort-by=.lastTimestamp"],
}


def parse_json(text: str) -> Any | None:
    try:
        return json.loads(text)
    except Exception:
        return None


def first_line(text: str | None) -> str | None:
    if not text:
        return None
    return text.strip().splitlines()[0] if text.strip() else None


def openshift_version(version_stdout: str) -> str | None:
    for line in version_stdout.splitlines():
        if line.startswith("Server Version:"):
            return line.split(":", 1)[1].strip()
    return None


def build_identity(*, timeout: int, context: str | None, kubeconfig: str | None) -> tuple[ClusterIdentity, list[Evidence], list[Limitation]]:
    evidence: list[Evidence] = []
    limitations: list[Limitation] = []

    def collect(name: str, args: list[str]):
        result = run_oc(args, timeout=timeout, context=context, kubeconfig=kubeconfig)
        evidence.append(Evidence(name=name, command=result.command, exit_code=result.exit_code, summary=first_line(result.stdout), truncated=result.truncated))
        if result.exit_code != 0:
            limitations.append(Limitation("unavailable", name, first_line(result.stderr) or f"exit_code={result.exit_code}"))
        return result

    current = collect("current-context", ["config", "current-context"])
    user = collect("whoami", ["whoami"])
    server = collect("api-server", ["whoami", "--show-server"])
    version = collect("version", ["version"])
    infrastructure = collect("infrastructure", ["get", "infrastructure", "cluster", "-o", "json"])
    nodes = collect("nodes", ["get", "nodes", "-o", "json"])
    network = collect("network", ["get", "network.config.openshift.io", "cluster", "-o", "json"])

    infra_data = parse_json(infrastructure.stdout) or {}
    infra_status = infra_data.get("status") or {}
    nodes_data = parse_json(nodes.stdout) or {}
    network_data = parse_json(network.stdout) or {}

    name = infra_status.get("infrastructureName")
    if not name:
        name = detect_cluster_name(timeout=timeout, context=context, kubeconfig=kubeconfig)

    identity = ClusterIdentity(
        name=name,
        context=first_line(current.stdout),
        api_server=first_line(server.stdout),
        user=first_line(user.stdout),
        version=openshift_version(version.stdout),
        platform=infra_status.get("platform"),
        control_plane_topology=infra_status.get("controlPlaneTopology"),
        infrastructure_topology=infra_status.get("infrastructureTopology"),
        infrastructure_name=infra_status.get("infrastructureName"),
        nodes=len(nodes_data.get("items") or []) if isinstance(nodes_data, dict) else None,
        network=(network_data.get("status") or {}).get("networkType") if isinstance(network_data, dict) else None,
    )
    return identity, evidence, limitations


def response_for_command(command: str, args: argparse.Namespace) -> ToolResponse:
    started = time.monotonic()
    identity, evidence, limitations = build_identity(timeout=args.timeout, context=args.context, kubeconfig=args.kubeconfig)
    capabilities = discover_capabilities(timeout=args.timeout, context=args.context, kubeconfig=args.kubeconfig)
    for key in ["api_resources", "api_versions"]:
        result = capabilities.get(key) or {}
        evidence.append(Evidence(key.replace("_", "-"), result.get("command") or [], result.get("exit_code"), summary=first_line(result.get("stdout")), truncated=bool(result.get("truncated"))))
        if result.get("exit_code") not in {0, None}:
            limitations.append(Limitation("unavailable", key.replace("_", "-"), first_line(result.get("stderr")) or f"exit_code={result.get('exit_code')}"))
    response = ToolResponse(
        tool=command,
        execution_status="success" if not limitations else "partial",
        health_status="healthy" if not limitations else "unknown",
        summary="diagnóstico consultivo concluído",
        cluster=identity,
        evidence=evidence,
        limitations=limitations,
        data={"capabilities": capabilities.get("capabilities", [])},
    )
    if command == "health":
        operators = run_oc(["get", "clusteroperators", "-o", "json"], timeout=args.timeout, context=args.context, kubeconfig=args.kubeconfig)
        pods = run_oc(["get", "pods", "-A", "--field-selector=status.phase!=Running", "-o", "wide"], timeout=args.timeout, context=args.context, kubeconfig=args.kubeconfig)
        response.evidence.append(Evidence("clusteroperators", operators.command, operators.exit_code, summary=first_line(operators.stdout), truncated=operators.truncated))
        response.evidence.append(Evidence("pods-not-running", pods.command, pods.exit_code, summary=first_line(pods.stdout), truncated=pods.truncated))
        op_data = parse_json(operators.stdout) or {}
        degraded = []
        for item in op_data.get("items") or []:
            conditions = {condition.get("type"): condition.get("status") for condition in item.get("status", {}).get("conditions", [])}
            if conditions.get("Degraded") == "True":
                degraded.append(item.get("metadata", {}).get("name", "unknown"))
        if degraded:
            response.health_status = "warning"
            response.summary = f"{len(degraded)} ClusterOperator(s) degradado(s)"
            for name in degraded:
                response.findings.append(Finding("warning", "ClusterOperator degradado", f"ClusterOperator {name} está degradado.", resource=name, next_step=f"./openshift-aiops operator {name}"))
        elif operators.exit_code == 0:
            response.health_status = "healthy"
            response.summary = "ClusterOperators consultados sem degradação detectada"
        if pods.exit_code != 0:
            response.execution_status = "partial"
            response.limitations.append(Limitation("permission_denied" if pods.exit_code == 1 else "unavailable", "pods", first_line(pods.stderr) or "não foi possível consultar pods"))
        response.metadata.duration_ms = int((time.monotonic() - started) * 1000)
        return response

    if command in READONLY_COMMANDS:
        result = run_oc(READONLY_COMMANDS[command], timeout=args.timeout, context=args.context, kubeconfig=args.kubeconfig)
        response.evidence.append(Evidence(command, result.command, result.exit_code, summary=first_line(result.stdout), truncated=result.truncated))
        response.data = {"result": result.to_dict(), "capabilities": capabilities.get("capabilities", [])}
        if result.exit_code == 0:
            response.health_status = "unknown" if command != "cluster" else "healthy"
            response.summary = f"{command}: consulta concluída"
        else:
            response.execution_status = "partial"
            response.health_status = "unknown"
            response.summary = f"{command}: consulta indisponível"
            response.limitations.append(Limitation("permission_denied" if result.exit_code == 1 else "unavailable", command, first_line(result.stderr) or f"exit_code={result.exit_code}"))
        response.metadata.duration_ms = int((time.monotonic() - started) * 1000)
        return response

    if command in {"pod", "namespace", "operator", "node"}:
        response.summary = f"Use o script direcionado correspondente para detalhes de {command}."
        response.health_status = "unknown"
        response.metadata.duration_ms = int((time.monotonic() - started) * 1000)
        return response

    response.execution_status = "failed"
    response.health_status = "unknown"
    response.summary = f"comando não suportado: {command}"
    response.findings.append(Finding("critical", "Argumento inválido", response.summary))
    response.metadata.duration_ms = int((time.monotonic() - started) * 1000)
    return response


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="OpenShift AIOps Toolkit")
    parser.add_argument("command", nargs="?", default="health", choices=["health", "cluster", "operators", "nodes", "pods", "storage", "network", "ingress", "dns", "monitoring", "olm", "certificates", "capacity", "events", "collect", "pod", "namespace", "operator", "node"])
    parser.add_argument("target", nargs="*")
    parser.add_argument("-n", "--namespace")
    parser.add_argument("--context")
    parser.add_argument("--kubeconfig")
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--output", choices=["human", "json", "yaml", "markdown", "raw"], default="human")
    parser.add_argument("--no-color", action="store_true")
    parser.add_argument("--ascii", action="store_true")
    parser.add_argument("--quiet", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--version", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.version:
        print("openshift-aiops-toolkit 0.1.0")
        return 0
    if args.command == "collect":
        from .commands import main as commands_main

        forwarded = ["collect-cluster", "--timeout", str(args.timeout)]
        if args.context:
            forwarded += ["--context", args.context]
        if args.kubeconfig:
            forwarded += ["--kubeconfig", args.kubeconfig]
        return commands_main(forwarded)
    response = response_for_command(args.command, args)
    print(render_response(response, output=args.output, ascii_only=args.ascii, no_color=args.no_color, quiet=args.quiet, verbose=args.verbose, debug=args.debug))
    if response.execution_status == "failed":
        return 6
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
