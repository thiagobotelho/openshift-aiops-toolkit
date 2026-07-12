from __future__ import annotations
from typing import Any
from . import config
from .commands import run_oc
from .validators import validate_cluster, validate_context

def list_configured_clusters() -> list[dict[str, Any]]: return config.configured_clusters()
def current_context(timeout: int = 30) -> dict[str, Any]: return run_oc(['config','current-context'], timeout=timeout).to_dict()
def select_cluster_context(cluster_name: str) -> dict[str, Any]:
    cluster_name=validate_cluster(cluster_name); cluster=config.find_cluster(cluster_name)
    if not cluster: return {'found': False, 'cluster': cluster_name, 'message': 'cluster não encontrado no inventário'}
    return {'found': True, 'cluster': cluster, 'message': 'use os valores retornados como parâmetros explícitos; o toolkit não troca contexto silenciosamente'}
def validate_cluster_context(cluster_name: str, current: str | None = None, timeout: int = 30) -> dict[str, Any]:
    selected=select_cluster_context(cluster_name)
    if not selected.get('found'): return selected
    expected=validate_context(selected['cluster'].get('context','')); current_value=current or run_oc(['config','current-context'], timeout=timeout).stdout.strip()
    return {'cluster': cluster_name, 'expected_context': expected, 'current_context': current_value, 'matches': expected == current_value}
