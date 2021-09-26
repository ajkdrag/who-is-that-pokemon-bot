import logging
from libs.processes import BaseProcess
from utils.functions import get_class_based_on_class_type
from utils.constants.config_contract import TRAINING_TYPE_MAP


LOG = logging.getLogger(__name__)


class TrainingProcess(BaseProcess):
    _list_scripts = []

    def _add_script(self, training_script):
        self._list_scripts.append(training_script)

    def _compile(self):
        scripts_to_use = self.config.get("scripts")
        for script_type in scripts_to_use:
            script = get_class_based_on_class_type(script_type, TRAINING_TYPE_MAP)(
                self.config.get("extraArgs")
            )
            self._add_script(script)

    def _execute(self):
        for script in self._list_scripts:
            script.setup()
            script.run()
