from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Callable
from ..commands import run_oc
from ..validators import validate_k8s_name, validate_namespace, validate_tail, validate_workload_kind
Handler = Callable[[dict[str, Any]], dict[str, Any]]
@dataclass
class ToolSpec:
    name: str
    description: str
    handler: Handler
    input_schema: dict[str, Any]
def no_args_schema() -> dict[str, Any]: return {"type":"object","properties":{},"additionalProperties":False}
def name_schema(kind: str='resource') -> dict[str, Any]: return {"type":"object","properties":{"name":{"type":"string","description":f"nome do {kind}"}},"required":["name"],"additionalProperties":False}
def ns_name_schema(kind: str='resource') -> dict[str, Any]: return {"type":"object","properties":{"namespace":{"type":"string"},"name":{"type":"string","description":f"nome do {kind}"}},"required":["namespace","name"],"additionalProperties":False}
def oc_simple(name: str, description: str, args: list[str]) -> ToolSpec: return ToolSpec(name, description, lambda params: run_oc(args).to_dict(), no_args_schema())
def oc_named(name: str, description: str, resource: str, namespaced: bool=False) -> ToolSpec:
    def handler(params: dict[str, Any]) -> dict[str, Any]:
        item = validate_k8s_name(params['name'], 'name')
        args = ['get', resource, item, '-o', 'yaml']
        if namespaced:
            args += ['-n', validate_namespace(params['namespace'])]
        return run_oc(args).to_dict()
    return ToolSpec(name, description, handler, ns_name_schema(resource) if namespaced else name_schema(resource))
def pod_log_schema() -> dict[str, Any]: return {"type":"object","properties":{"namespace":{"type":"string"},"name":{"type":"string"},"container":{"type":"string"},"tail":{"type":"integer","minimum":1,"maximum":2000}},"required":["namespace","name"],"additionalProperties":False}
def logs_tool(previous: bool=False) -> Handler:
    def handler(params: dict[str, Any]) -> dict[str, Any]:
        ns = validate_namespace(params['namespace']); pod = validate_k8s_name(params['name'], 'pod'); tail = validate_tail(params.get('tail', 300), maximum=2000)
        args = ['logs', pod, '-n', ns, '--tail', str(tail)]
        if previous: args.append('--previous')
        if params.get('container'): args += ['-c', validate_k8s_name(params['container'], 'container')]
        return run_oc(args).to_dict()
    return handler
def workload_schema() -> dict[str, Any]: return {"type":"object","properties":{"namespace":{"type":"string"},"kind":{"type":"string"},"name":{"type":"string"}},"required":["namespace","name"],"additionalProperties":False}
def workload_handler(params: dict[str, Any]) -> dict[str, Any]:
    ns = validate_namespace(params['namespace']); kind = validate_workload_kind(params.get('kind', 'deployment')); name = validate_k8s_name(params['name'], 'workload')
    return run_oc(['get', kind, name, '-n', ns, '-o', 'yaml']).to_dict()
