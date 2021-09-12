import logging
from libs.processes import BaseProcess
from utils.functions import get_class_based_on_class_type
from utils.constants.config_contract import SERVICE_TYPE_MAP


LOG = logging.getLogger(__name__)


class InferencingProcess(BaseProcess):
    _list_services = []

    def _add_service(self, new_service):
        self._list_services.append(new_service)

    def _compile(self):
        services_to_use = self.config.get("services")
        for service_type in services_to_use:
            service = get_class_based_on_class_type(service_type, SERVICE_TYPE_MAP)(
                self.config.get("extraArgs")
            )
            self._add_service(service)

    def _execute(self):
        for service in self._list_services:
            service.setup()
            service.start()
