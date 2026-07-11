from .base import oc_simple
TOOLS={'monitoring_health': oc_simple('monitoring_health','Saúde do monitoring stack.',['get','clusteroperator','monitoring','-o','yaml'])}
