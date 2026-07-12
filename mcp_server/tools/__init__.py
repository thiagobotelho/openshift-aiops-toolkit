from __future__ import annotations
from typing import Any
from .base import ToolSpec, extend_schema_with_common, validate_common_params
MODULES=['cluster','nodes','pods','workloads','namespaces','operators','storage','network','ingress','dns','authentication','monitoring','certificates','evidence','reports']
def get_tool_registry() -> dict[str, ToolSpec]:
    registry={}
    for module_name in MODULES:
        module=__import__(f'mcp_server.tools.{module_name}', fromlist=['TOOLS'])
        registry.update(module.TOOLS)
    from .base import oc_simple
    registry.setdefault('api_health', oc_simple('api_health','Saúde dos operadores de API.',['get','clusteroperators','kube-apiserver','openshift-apiserver','-o','yaml']))
    registry.setdefault('etcd_health', oc_simple('etcd_health','Saúde do operador etcd.',['get','clusteroperator','etcd','-o','yaml']))
    registry.setdefault('console_health', oc_simple('console_health','Saúde do console operator.',['get','clusteroperator','console','-o','yaml']))
    registry.setdefault('image_registry_health', oc_simple('image_registry_health','Saúde do image registry operator.',['get','clusteroperator','image-registry','-o','yaml']))
    registry.setdefault('service_health', oc_simple('service_health','Services.',['get','services','-A','-o','wide']))
    registry.setdefault('endpoints_health', oc_simple('endpoints_health','Endpoints e EndpointSlices.',['get','endpoints,endpointslices','-A','-o','wide']))
    return registry
def list_tools() -> list[dict[str, Any]]:
    return sorted([{'name': s.name, 'description': s.description, 'inputSchema': extend_schema_with_common(s.input_schema)} for s in get_tool_registry().values()], key=lambda x: x['name'])
def call_tool(name: str, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
    registry=get_tool_registry()
    if name not in registry:
        raise KeyError(f'ferramenta MCP desconhecida: {name}')
    params=arguments or {}
    validate_common_params(params)
    return registry[name].handler(params)
