from .base import ToolSpec, oc_simple, workload_handler, workload_schema
TOOLS={
'workload_health': ToolSpec('workload_health','Saúde de workload suportado.',workload_handler,workload_schema()),
'deployment_health': oc_simple('deployment_health','Deployments.',['get','deployments','-A','-o','wide']),
'statefulset_health': oc_simple('statefulset_health','StatefulSets.',['get','statefulsets','-A','-o','wide']),
'daemonset_health': oc_simple('daemonset_health','DaemonSets.',['get','daemonsets','-A','-o','wide']),
'failed_jobs': oc_simple('failed_jobs','Jobs para análise de falha.',['get','jobs','-A','-o','wide']),
}
