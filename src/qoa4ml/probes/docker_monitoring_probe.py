import json
import time

import docker

from qoa4ml.reports.resources_report_model import DockerReport

from ..config.configs import ClientInfo, DockerProbeConfig
from ..connector.base_connector import BaseConnector
from ..utils.docker_util import get_docker_stats
from ..utils.logger import qoa_logger
from .probe import Probe


class DockerMonitoringProbe(Probe):
    def __init__(
        self,
        config: DockerProbeConfig,
        connector: BaseConnector,
        client_info: ClientInfo,
    ) -> None:
        super().__init__(config, connector, client_info)
        self.config = config
        if self.config.require_register:
            self.obs_service_url = self.config.obs_service_url
        self.docker_client = docker.from_env()

    def create_report(self):
        try:
            reports = get_docker_stats(self.docker_client, self.config.container_list)
            docker_report = DockerReport(
                metadata=self.client_info,
                timestamp=time.time(),
                container_reports=reports,
            )
            reports_dict = docker_report.model_dump()
            # NOTE: if the reports dict is empty, the loop will run very fast, so here add 2 seconds as if there is container to report
            if not reports_dict:
                time.sleep(2)
            return json.dumps(reports_dict)
        except RuntimeError:
            qoa_logger.exception(
                "Maybe running in the background result in this exception!"
            )
        return json.dumps({"error": "RuntimeError"})
