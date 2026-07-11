from .base import ToolSpec, ns_name_schema, oc_simple
from ..commands import run_oc
from ..validators import validate_k8s_name, validate_namespace
TOOLS={'ingress_health': oc_simple('ingress_health','Saúde de ingress e routers.',['get','ingresscontrollers','-A','-o','wide']), 'route_health': ToolSpec('route_health','Detalhes de Route.',lambda p: run_oc(['get','route',validate_k8s_name(p['name'],'route'),'-n',validate_namespace(p['namespace']),'-o','yaml']).to_dict(),ns_name_schema('route'))}
