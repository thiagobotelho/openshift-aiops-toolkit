from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .commands import run_oc


@dataclass
class Capability:
    name: str
    status: str
    reason: str

    def to_dict(self) -> dict[str, str]:
        return {"name": self.name, "status": self.status, "reason": self.reason}


def has_resource(api_resources_stdout: str, resource: str, api_version_contains: str | None = None) -> bool:
    wanted = resource.lower()
    version_fragment = api_version_contains.lower() if api_version_contains else None
    for line in api_resources_stdout.lower().splitlines():
        cols = line.split()
        if cols and cols[0] == wanted and (version_fragment is None or any(version_fragment in col for col in cols[1:])):
            return True
    return False


def discover_capabilities(*, timeout: int = 60, context: str | None = None, kubeconfig: str | None = None) -> dict[str, Any]:
    resources = run_oc(["api-resources"], timeout=timeout, context=context, kubeconfig=kubeconfig)
    versions = run_oc(["api-versions"], timeout=timeout, context=context, kubeconfig=kubeconfig)
    capabilities: list[Capability] = []
    if resources.exit_code != 0:
        capabilities.append(Capability("api-resources", "unavailable", resources.stderr.strip() or "não foi possível consultar recursos da API"))
    else:
        checks = [
            ("metrics-api", "pods", "metrics.k8s.io"),
            ("machineconfigpools", "machineconfigpools", None),
            ("ingresscontrollers", "ingresscontrollers", None),
            ("routes", "routes", None),
            ("prometheusrules", "prometheusrules", None),
            ("clusterserviceversions", "clusterserviceversions", None),
        ]
        for name, resource, api_version in checks:
            if has_resource(resources.stdout, resource, api_version):
                suffix = f" em {api_version}" if api_version else ""
                capabilities.append(Capability(name, "ok", f"recurso {resource}{suffix} disponível"))
            else:
                suffix = f" em {api_version}" if api_version else ""
                capabilities.append(Capability(name, "not_applicable", f"recurso {resource}{suffix} não anunciado pela API"))
    if versions.exit_code != 0:
        capabilities.append(Capability("api-versions", "unavailable", versions.stderr.strip() or "não foi possível consultar versões da API"))
    else:
        capabilities.append(Capability("api-versions", "ok", "versões da API consultadas"))
    return {
        "api_resources": resources.to_dict(),
        "api_versions": versions.to_dict(),
        "capabilities": [item.to_dict() for item in capabilities],
    }
