import logging
from libs.processes import BaseProcess

LOG = logging.getLogger(__name__)


class PipelineProcess(BaseProcess):
    def _compile(self):
        ...

    def _execute(self):
        ...
