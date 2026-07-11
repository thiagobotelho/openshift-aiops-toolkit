from .base import ToolSpec, logs_tool, ns_name_schema, oc_named, oc_simple, pod_log_schema
from ..commands import run_oc
from ..validators import validate_k8s_name, validate_namespace

def _pod_events(p):
    ns=validate_namespace(p['namespace']); name=validate_k8s_name(p['name'],'pod')
    return run_oc(['get','events','-n',ns,'--field-selector',f'involvedObject.name={name}','--sort-by=.lastTimestamp']).to_dict()
TOOLS={
'unhealthy_pods': oc_simple('unhealthy_pods','Pods não Running.',['get','pods','-A','--field-selector=status.phase!=Running','-o','wide']),
'restarting_pods': oc_simple('restarting_pods','Pods para análise de reinícios.',['get','pods','-A','-o','json']),
'pending_pods': oc_simple('pending_pods','Pods Pending.',['get','pods','-A','--field-selector=status.phase=Pending','-o','wide']),
'pod_details': oc_named('pod_details','Detalhes do Pod.','pod',namespaced=True),
'pod_logs': ToolSpec('pod_logs','Logs atuais limitados de Pod.',logs_tool(False),pod_log_schema()),
'pod_previous_logs': ToolSpec('pod_previous_logs','Logs anteriores limitados de Pod.',logs_tool(True),pod_log_schema()),
'pod_events': ToolSpec('pod_events','Eventos de Pod.',_pod_events,ns_name_schema('pod')),
}
