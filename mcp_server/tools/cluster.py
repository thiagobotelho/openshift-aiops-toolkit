from __future__ import annotations
from typing import Any
from .. import cluster as cluster_mod, context as context_mod
from ..commands import run_oc
from .base import ToolSpec, common_timeout, name_schema, no_args_schema, oc_simple

def _list(_: dict[str, Any]) -> dict[str, Any]: return {'clusters': context_mod.list_configured_clusters()}
def _current(p: dict[str, Any]) -> dict[str, Any]: return context_mod.current_context(timeout=common_timeout(p))
def _select(p: dict[str, Any]) -> dict[str, Any]: return context_mod.select_cluster_context(p['name'])
def _validate(p: dict[str, Any]) -> dict[str, Any]: return context_mod.validate_cluster_context(p['name'], timeout=common_timeout(p))
def _identity(p: dict[str, Any]) -> dict[str, Any]: return cluster_mod.identity(timeout=common_timeout(p))
def _permissions(p: dict[str, Any]) -> dict[str, Any]: return run_oc(['auth','can-i','--list'], timeout=common_timeout(p)).to_dict()
TOOLS={
'list_configured_clusters': ToolSpec('list_configured_clusters','Lista clusters do inventário local.',_list,no_args_schema()),
'current_context': ToolSpec('current_context','Retorna o contexto OpenShift atual.',_current,no_args_schema()),
'select_cluster_context': ToolSpec('select_cluster_context','Retorna metadados de cluster sem trocar contexto.',_select,name_schema('cluster')),
'validate_cluster_context': ToolSpec('validate_cluster_context','Valida se contexto atual corresponde ao cluster.',_validate,name_schema('cluster')),
'cluster_identity': ToolSpec('cluster_identity','Coleta identidade básica do cluster.',_identity,no_args_schema()),
'check_permissions': ToolSpec('check_permissions','Verifica permissões somente leitura.',_permissions,no_args_schema()),
'cluster_version': oc_simple('cluster_version','Retorna ClusterVersion.',['get','clusterversion','-o','json']),
'cluster_infrastructure': oc_simple('cluster_infrastructure','Retorna Infrastructure cluster.',['get','infrastructure','cluster','-o','json']),
'cluster_health': oc_simple('cluster_health','Resumo de ClusterOperators.',['get','clusteroperators','-o','wide']),
'cluster_operators': oc_simple('cluster_operators','Lista ClusterOperators.',['get','clusteroperators','-o','json']),
'degraded_operators': oc_simple('degraded_operators','Operadores degradados.',['get','clusteroperators','-o','json']),
'progressing_operators': oc_simple('progressing_operators','Operadores em progresso.',['get','clusteroperators','-o','json']),
'recent_warning_events': oc_simple('recent_warning_events','Eventos Warning recentes.',['get','events','-A','--field-selector=type=Warning','--sort-by=.lastTimestamp']),
'resource_usage': oc_simple('resource_usage','Uso de recursos por nodes.',['adm','top','nodes']),
'cluster_capacity': oc_simple('cluster_capacity','Capacidade de nodes.',['get','nodes','-o','json']),
'upgrade_status': oc_simple('upgrade_status','Status de upgrade.',['get','clusterversion','version','-o','yaml']),
}
