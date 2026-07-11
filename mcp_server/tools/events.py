from .base import oc_simple
TOOLS={'recent_warning_events': oc_simple('recent_warning_events','Eventos Warning recentes.',['get','events','-A','--field-selector=type=Warning','--sort-by=.lastTimestamp'])}
