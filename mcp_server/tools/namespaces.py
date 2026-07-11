from .base import ToolSpec, name_schema
from ..commands import run_oc
from ..validators import validate_namespace
TOOLS={
'namespace_health': ToolSpec('namespace_health','Resumo de namespace.',lambda p: run_oc(['get','all','-n',validate_namespace(p['name']),'-o','wide']).to_dict(),name_schema('namespace')),
'namespace_events': ToolSpec('namespace_events','Eventos de namespace.',lambda p: run_oc(['get','events','-n',validate_namespace(p['name']),'--sort-by=.lastTimestamp']).to_dict(),name_schema('namespace')),
'namespace_resource_usage': ToolSpec('namespace_resource_usage','Uso de recursos no namespace.',lambda p: run_oc(['adm','top','pods','-n',validate_namespace(p['name'])]).to_dict(),name_schema('namespace')),
'namespace_quotas': ToolSpec('namespace_quotas','Quotas e LimitRanges.',lambda p: run_oc(['get','resourcequotas,limitranges','-n',validate_namespace(p['name']),'-o','wide']).to_dict(),name_schema('namespace')),
}
