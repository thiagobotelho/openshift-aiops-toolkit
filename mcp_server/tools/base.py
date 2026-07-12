from __future__ import annotations
import os
from dataclasses import dataclass
from typing import Any, Callable
from ..commands import run_oc
from ..validators import (
    ensure_no_dangerous,
    validate_cluster,
    validate_context,
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
    "context":{"type":"string","description":"contexto kubeconfig opcional para esta consulta; não altera o contexto persistente"},
    "kubeconfig":{"type":"string","description":"kubeconfig opcional para esta consulta; não é impresso nem persistido"},
    "timeout":{"type":"integer","minimum":1,"maximum":900,"description":"timeout da consulta em segundos"},
    "output":{"type":"string","enum":["human","json","yaml","markdown","raw"],"description":"formato lógico preferido para a resposta"},
    "verbose":{"type":"boolean","description":"inclui detalhes adicionais quando a ferramenta suportar"},
    "environment":{"type":"string","enum":["current","development","homologation","production","laboratory"],"description":"metadado opcional para inventário/auditoria; o toolkit usa o contexto atual do oc"},
    "cluster":{"type":"string","description":"alias opcional para inventário; o toolkit identifica o cluster pelo contexto/API atual"},
    "confirm_production":{"type":"string","description":"metadado opcional de compatibilidade; ferramentas consultivas não exigem confirmação de produção"},
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
    context=params.get("context") or os.environ.get("OPENSHIFT_AIOPS_CONTEXT")
    kubeconfig=params.get("kubeconfig") or os.environ.get("OPENSHIFT_AIOPS_KUBECONFIG")
    if context:
        context=validate_context(str(context))
    if kubeconfig is not None:
        ensure_no_dangerous(str(kubeconfig), "kubeconfig")
    return {"environment":environment, "cluster":cluster_name, "timeout":timeout, "context":context, "kubeconfig":kubeconfig}
def common_timeout(params: dict[str, Any]) -> int: return int(validate_common_params(params)["timeout"])
def common_oc_kwargs(params: dict[str, Any]) -> dict[str, Any]:
    common=validate_common_params(params)
    return {"timeout": int(common["timeout"]), "context": common.get("context"), "kubeconfig": common.get("kubeconfig")}
def no_args_schema() -> dict[str, Any]: return schema_with_common()
def name_schema(kind: str='resource') -> dict[str, Any]: return schema_with_common({"name":{"type":"string","description":f"nome do {kind}"}}, ["name"])
def ns_name_schema(kind: str='resource') -> dict[str, Any]: return schema_with_common({"namespace":{"type":"string"},"name":{"type":"string","description":f"nome do {kind}"}}, ["namespace","name"])
def oc_simple(name: str, description: str, args: list[str]) -> ToolSpec: return ToolSpec(name, description, lambda params: run_oc(args, **common_oc_kwargs(params)).to_dict(), no_args_schema())
def oc_named(name: str, description: str, resource: str, namespaced: bool=False) -> ToolSpec:
    def handler(params: dict[str, Any]) -> dict[str, Any]:
        item = validate_k8s_name(params['name'], 'name')
        args = ['get', resource, item, '-o', 'yaml']
        if namespaced:
            args += ['-n', validate_namespace(params['namespace'])]
        return run_oc(args, **common_oc_kwargs(params)).to_dict()
    return ToolSpec(name, description, handler, ns_name_schema(resource) if namespaced else name_schema(resource))
def pod_log_schema() -> dict[str, Any]: return schema_with_common({"namespace":{"type":"string"},"name":{"type":"string"},"container":{"type":"string"},"tail":{"type":"integer","minimum":1,"maximum":2000}}, ["namespace","name"])
def logs_tool(previous: bool=False) -> Handler:
    def handler(params: dict[str, Any]) -> dict[str, Any]:
        ns = validate_namespace(params['namespace']); pod = validate_k8s_name(params['name'], 'pod'); tail = validate_tail(params.get('tail', 300), maximum=2000)
        args = ['logs', pod, '-n', ns, '--tail', str(tail)]
        if previous: args.append('--previous')
        if params.get('container'): args += ['-c', validate_k8s_name(params['container'], 'container')]
        return run_oc(args, **common_oc_kwargs(params)).to_dict()
    return handler
def workload_schema() -> dict[str, Any]: return schema_with_common({"namespace":{"type":"string"},"kind":{"type":"string"},"name":{"type":"string"}}, ["namespace","name"])
def workload_handler(params: dict[str, Any]) -> dict[str, Any]:
    ns = validate_namespace(params['namespace']); kind = validate_workload_kind(params.get('kind', 'deployment')); name = validate_k8s_name(params['name'], 'workload')
    return run_oc(['get', kind, name, '-n', ns, '-o', 'yaml'], **common_oc_kwargs(params)).to_dict()
