from .base import oc_simple
TOOLS={'dns_health': oc_simple('dns_health','Saúde de DNS operator e DNS config.',['get','dns.operator.openshift.io','default','-o','yaml'])}
