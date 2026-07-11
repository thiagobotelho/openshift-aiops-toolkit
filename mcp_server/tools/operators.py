from .base import ToolSpec, name_schema, oc_named, oc_simple
from ..commands import run_oc
from ..validators import validate_k8s_name
TOOLS={
'operator_details': oc_named('operator_details','Detalhes de ClusterOperator.','clusteroperator'),
'operator_related_resources': ToolSpec('operator_related_resources','Recursos relacionados do operador.',lambda p: run_oc(['describe','clusteroperator',validate_k8s_name(p['name'],'operator')]).to_dict(),name_schema('operator')),
'operator_namespace_health': oc_simple('operator_namespace_health','Namespaces e recursos de operadores.',['get','pods','-A','-o','wide']),
'olm_health': oc_simple('olm_health','Saúde geral de OLM.',['get','clusterserviceversions,subscriptions,installplans,catalogsources','-A','-o','wide']),
'subscription_details': oc_named('subscription_details','Detalhes de Subscription.','subscription',namespaced=True),
'csv_details': oc_named('csv_details','Detalhes de ClusterServiceVersion.','clusterserviceversion',namespaced=True),
'installplan_details': oc_named('installplan_details','Detalhes de InstallPlan.','installplan',namespaced=True),
'catalogsource_health': oc_simple('catalogsource_health','CatalogSources.',['get','catalogsources','-A','-o','wide']),
}
