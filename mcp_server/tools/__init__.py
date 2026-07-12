from __future__ import annotations
from datetime import datetime, timezone
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

def _result_exit_code(result: dict[str, Any]) -> int | None:
    if isinstance(result.get('exit_code'), int):
        return int(result['exit_code'])
    nested = result.get('result')
    if isinstance(nested, dict) and isinstance(nested.get('exit_code'), int):
        return int(nested['exit_code'])
    return None

def _result_summary(result: dict[str, Any]) -> str:
    stdout = result.get('stdout')
    if isinstance(stdout, str) and stdout.strip():
        return stdout.strip().splitlines()[0]
    message = result.get('message')
    if isinstance(message, str) and message.strip():
        return message.strip()
    return 'consulta MCP concluída'

def wrap_tool_response(name: str, result: dict[str, Any]) -> dict[str, Any]:
    if 'schema_version' in result and 'execution_status' in result:
        return result
    exit_code = _result_exit_code(result)
    execution_status = 'success' if exit_code in {None, 0} else 'partial'
    wrapped = {
        'schema_version': '1.0',
        'tool': name,
        'execution_status': execution_status,
        'health_status': 'unknown',
        'summary': _result_summary(result),
        'cluster': {},
        'findings': [],
        'evidence': [],
        'limitations': [] if execution_status == 'success' else [{'status': 'unavailable', 'component': name, 'reason': f'exit_code={exit_code}'}],
        'metadata': {
            'finished_at': datetime.now(timezone.utc).isoformat(),
            'toolkit_version': '0.1.0',
        },
        'result': result,
    }
    wrapped.update(result)
    return wrapped

def call_tool(name: str, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
    registry=get_tool_registry()
    if name not in registry:
        raise KeyError(f'ferramenta MCP desconhecida: {name}')
    params=arguments or {}
    validate_common_params(params)
    return wrap_tool_response(name, registry[name].handler(params))
