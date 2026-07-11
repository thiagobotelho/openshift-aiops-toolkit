from pathlib import Path
from .base import ToolSpec, name_schema, no_args_schema, ns_name_schema
from ..collectors import collect_cluster_evidence, collect_target_evidence, sanitize_evidence_tree

def _collect_cluster(p):
    path=collect_cluster_evidence(cluster=p.get('cluster','cluster'), environment=p.get('environment','development'), output_dir=Path(p.get('output_dir','evidencias')))
    return {'evidence_dir': str(path)}
def _collect_target(target):
    def h(p):
        path=collect_target_evidence(target=target, namespace=p.get('namespace'), name=p.get('name'), kind=p.get('kind'), output_dir=Path(p.get('output_dir','evidencias')))
        return {'evidence_dir': str(path)}
    return h
TOOLS={
'collect_cluster_evidence': ToolSpec('collect_cluster_evidence','Coleta evidências gerais do cluster.',_collect_cluster,{"type":"object","properties":{"cluster":{"type":"string"},"environment":{"type":"string"},"output_dir":{"type":"string"}},"additionalProperties":False}),
'collect_namespace_evidence': ToolSpec('collect_namespace_evidence','Coleta evidências de namespace.',_collect_target('namespace'),name_schema('namespace')),
'collect_pod_evidence': ToolSpec('collect_pod_evidence','Coleta evidências de Pod.',_collect_target('pod'),ns_name_schema('pod')),
'collect_workload_evidence': ToolSpec('collect_workload_evidence','Coleta evidências de workload.',_collect_target('workload'),{"type":"object","properties":{"namespace":{"type":"string"},"kind":{"type":"string"},"name":{"type":"string"}},"required":["namespace","name"],"additionalProperties":False}),
'collect_operator_evidence': ToolSpec('collect_operator_evidence','Coleta evidências de operador.',_collect_target('operator'),name_schema('operator')),
'collect_node_evidence': ToolSpec('collect_node_evidence','Coleta evidências de node.',_collect_target('node'),name_schema('node')),
'collect_storage_evidence': ToolSpec('collect_storage_evidence','Coleta evidências de storage.',_collect_target('storage'),no_args_schema()),
'collect_network_evidence': ToolSpec('collect_network_evidence','Coleta evidências de rede.',_collect_target('network'),no_args_schema()),
'generate_evidence_manifest': ToolSpec('generate_evidence_manifest','Manifesto é gerado durante a coleta.',lambda p: {'message':'manifest.json é gerado automaticamente','path':p.get('name','')},name_schema('path')),
'sanitize_evidence': ToolSpec('sanitize_evidence','Sanitiza evidências locais.',lambda p: {'files_sanitized': sanitize_evidence_tree(Path(p['name']))},name_schema('path')),
'package_evidence': ToolSpec('package_evidence','Empacota evidências sanitizadas.',lambda p: {'message':'use scripts/empacotar-evidencias.sh','path':p.get('name','')},name_schema('path')),
}
