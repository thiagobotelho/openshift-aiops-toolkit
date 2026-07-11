from .base import oc_simple
TOOLS={'alerts': oc_simple('alerts','Regras e objetos de alerting observáveis.',['get','prometheusrules','-A','-o','wide'])}
