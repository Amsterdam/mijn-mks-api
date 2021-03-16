from prometheus_client import Gauge

mks_connection_state = Gauge('mks_connection_state', 'State of connection to MKS')
