from pathlib import Path
from .base import ToolSpec, no_args_schema
from ..reports import compare_evidence_dirs, generate_base_report
TOOLS={
'generate_base_report': ToolSpec('generate_base_report','Gera relatório base em Markdown.',lambda p: {'report': generate_base_report(Path(p['name']) if p.get('name') else None)}, {"type":"object","properties":{"name":{"type":"string"}},"additionalProperties":False}),
'generate_incident_timeline': ToolSpec('generate_incident_timeline','Gera estrutura de timeline de incidente.',lambda p: {'timeline':'detecção → coleta → triagem → validação → plano → aprovação → execução externa → validação pós-mudança'},no_args_schema()),
'compare_evidence_collections': ToolSpec('compare_evidence_collections','Compara duas coletas.',lambda p: {'report': compare_evidence_dirs(Path(p['old']), Path(p['new']))},{"type":"object","properties":{"old":{"type":"string"},"new":{"type":"string"}},"required":["old","new"],"additionalProperties":False}),
'compare_cluster_health': ToolSpec('compare_cluster_health','Compara saúde de clusters.',lambda p: {'report': compare_evidence_dirs(Path(p['old']), Path(p['new']))},{"type":"object","properties":{"old":{"type":"string"},"new":{"type":"string"}},"required":["old","new"],"additionalProperties":False}),
}
