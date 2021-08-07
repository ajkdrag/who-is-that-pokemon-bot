import logging
from libs.processes import BaseProcess
from utils.functions import get_class_based_on_class_type
from utils.constants.config_contract import PREPROCESSING_TYPE_MAP

LOG = logging.getLogger(__name__)


class PreprocessingProcess(BaseProcess):
    _list_preprocessors = []

    def _add_preprocessor(self, new_preprocessor):
        self._list_preprocessors.append(new_preprocessor)

    def _compile(self):
        preprocessors_to_use = self.config.get("preprocessors")
        for preprocessing_type in preprocessors_to_use:
            preprocessor = get_class_based_on_class_type(
                preprocessing_type, PREPROCESSING_TYPE_MAP
            )(self.config.get("extraArgs"))
            self._add_preprocessor(preprocessor)

    def _execute(self):
        for preprocessor in self._list_preprocessors:
            preprocessor.preprocess()
