from .base import oc_simple
TOOLS={'authentication_health': oc_simple('authentication_health','Saúde de authentication operator.',['get','clusteroperator','authentication','-o','yaml'])}
