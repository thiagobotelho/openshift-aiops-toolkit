from .base import oc_simple
TOOLS={'network_health': oc_simple('network_health','Configuração e operador de rede.',['get','network.config.openshift.io','cluster','-o','yaml']), 'network_policies': oc_simple('network_policies','NetworkPolicies.',['get','networkpolicies','-A','-o','wide'])}
