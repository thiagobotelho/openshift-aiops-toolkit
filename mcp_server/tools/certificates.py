from .base import oc_simple
TOOLS={'certificate_health': oc_simple('certificate_health','CSRs e certificados observáveis.',['get','csr','-o','wide']), 'pending_csrs': oc_simple('pending_csrs','CSRs pendentes.',['get','csr','-o','wide'])}
