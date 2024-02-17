import falcon
import falcon.asgi
import json
from system_monitoring_probe import SysMonitoringProbe


class MetricsResource:
    def __init__(self, probe):
        self.probe = probe

    async def on_get(self, req, resp):
        try:
            report = self.probe.currentReport
            resp.media = report
        except Exception as e:
            raise falcon.HTTPBadRequest(description=str(e))


probe_conf = json.load(open("./probe_conf.json"))
system_monitoring_probe = SysMonitoringProbe(probe_conf)
app = falcon.asgi.App()

# Resources are represented by long-lived class instances

# things will handle all requests to the '/things' URL path
metrics_resource = MetricsResource(system_monitoring_probe)
app.add_route("/metrics", metrics_resource)
