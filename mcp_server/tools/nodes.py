from .base import oc_simple, oc_named
TOOLS={
'list_nodes': oc_simple('list_nodes','Lista nodes.',['get','nodes','-o','wide']),
'unhealthy_nodes': oc_simple('unhealthy_nodes','Nodes para análise de condições.',['get','nodes','-o','json']),
'node_details': oc_named('node_details','Detalhes de node.','node'),
'node_resource_usage': oc_simple('node_resource_usage','Uso de recursos por node.',['adm','top','nodes']),
'node_pods': oc_simple('node_pods','Pods distribuídos por node.',['get','pods','-A','-o','wide']),
'machineconfigpool_health': oc_simple('machineconfigpool_health','Saúde dos MachineConfigPools.',['get','machineconfigpools','-o','wide']),
}
