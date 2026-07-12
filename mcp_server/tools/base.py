from __future__ import annotations
import os
from dataclasses import dataclass
from typing import Any, Callable
from ..commands import run_oc
from ..validators import (
    ValidationError,
    ensure_no_dangerous,
    validate_cluster,
    validate_environment,
    validate_k8s_name,
    validate_namespace,
    validate_tail,
    validate_timeout,
    validate_workload_kind,
)
Handler = Callable[[dict[str, Any]], dict[str, Any]]
@dataclass
class ToolSpec:
    name: str
    description: str
    handler: Handler
    input_schema: dict[str, Any]
COMMON_PROPERTIES={
    "environment":{"type":"string","enum":["current","development","homologation","production","laboratory"],"description":"ambiente lógico da consulta; use current para o contexto ativo do oc"},
    "cluster":{"type":"string","description":"nome lógico do cluster usado para confirmação e auditoria"},
    "timeout":{"type":"integer","minimum":1,"maximum":900,"description":"timeout da consulta em segundos"},
    "confirm_production":{"type":"string","description":"confirmação explícita exigida quando environment=production"},
}
def schema_with_common(properties: dict[str, Any] | None=None, required: list[str] | None=None) -> dict[str, Any]:
    merged={**COMMON_PROPERTIES, **(properties or {})}
    schema={"type":"object","properties":merged,"additionalProperties":False}
    if required: schema["required"]=required
    return schema
def extend_schema_with_common(schema: dict[str, Any]) -> dict[str, Any]:
    if schema.get("type") != "object":
        return schema
    merged={**COMMON_PROPERTIES, **dict(schema.get("properties") or {})}
    updated=dict(schema)
    updated["properties"]=merged
    updated["additionalProperties"]=False
    return updated
def validate_common_params(params: dict[str, Any]) -> dict[str, Any]:
    environment=validate_environment(str(params.get("environment") or os.environ.get("OPENSHIFT_AIOPS_ENVIRONMENT","current")))
    timeout=validate_timeout(params.get("timeout",60))
    cluster=params.get("cluster") or os.environ.get("OPENSHIFT_AIOPS_CLUSTER")
    cluster_name=validate_cluster(str(cluster)) if cluster else None
    confirm=params.get("confirm_production") or os.environ.get("OPENSHIFT_AIOPS_PRODUCTION_CONFIRM")
    if confirm is not None:
        ensure_no_dangerous(str(confirm), "confirm_production")
    if environment == "production":
        expected=cluster_name or "production"
        if confirm != expected:
            raise ValidationError("ambiente production exige confirm_production igual ao nome lógico do cluster")
    return {"environment":environment, "cluster":cluster_name, "timeout":timeout}
def common_timeout(params: dict[str, Any]) -> int: return int(validate_common_params(params)["timeout"])
def no_args_schema() -> dict[str, Any]: return schema_with_common()
def name_schema(kind: str='resource') -> dict[str, Any]: return schema_with_common({"name":{"type":"string","description":f"nome do {kind}"}}, ["name"])
def ns_name_schema(kind: str='resource') -> dict[str, Any]: return schema_with_common({"namespace":{"type":"string"},"name":{"type":"string","description":f"nome do {kind}"}}, ["namespace","name"])
def oc_simple(name: str, description: str, args: list[str]) -> ToolSpec: return ToolSpec(name, description, lambda params: run_oc(args, timeout=common_timeout(params)).to_dict(), no_args_schema())
def oc_named(name: str, description: str, resource: str, namespaced: bool=False) -> ToolSpec:
    def handler(params: dict[str, Any]) -> dict[str, Any]:
        item = validate_k8s_name(params['name'], 'name')
        args = ['get', resource, item, '-o', 'yaml']
        if namespaced:
            args += ['-n', validate_namespace(params['namespace'])]
        return run_oc(args, timeout=common_timeout(params)).to_dict()
    return ToolSpec(name, description, handler, ns_name_schema(resource) if namespaced else name_schema(resource))
def pod_log_schema() -> dict[str, Any]: return schema_with_common({"namespace":{"type":"string"},"name":{"type":"string"},"container":{"type":"string"},"tail":{"type":"integer","minimum":1,"maximum":2000}}, ["namespace","name"])
def logs_tool(previous: bool=False) -> Handler:
    def handler(params: dict[str, Any]) -> dict[str, Any]:
        ns = validate_namespace(params['namespace']); pod = validate_k8s_name(params['name'], 'pod'); tail = validate_tail(params.get('tail', 300), maximum=2000)
        args = ['logs', pod, '-n', ns, '--tail', str(tail)]
        if previous: args.append('--previous')
        if params.get('container'): args += ['-c', validate_k8s_name(params['container'], 'container')]
        return run_oc(args, timeout=common_timeout(params)).to_dict()
    return handler
def workload_schema() -> dict[str, Any]: return schema_with_common({"namespace":{"type":"string"},"kind":{"type":"string"},"name":{"type":"string"}}, ["namespace","name"])
def workload_handler(params: dict[str, Any]) -> dict[str, Any]:
    ns = validate_namespace(params['namespace']); kind = validate_workload_kind(params.get('kind', 'deployment')); name = validate_k8s_name(params['name'], 'workload')
    return run_oc(['get', kind, name, '-n', ns, '-o', 'yaml'], timeout=common_timeout(params)).to_dict()
