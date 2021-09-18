import core.config_parser as cfg_parser
from core.config_store import ConfigStore
from utils.constants.globals import LOG_LEVEL, LOG_FORMAT, ROOT_PROCESS_CONFIG_PATH
from utils.validators import launcher_config_validator
from utils.logger import Logger


class Controller:
    def __init__(self, launcher_config_path):
        self.config_store = ConfigStore(launcher_config_path)
        self._setup()

    def _setup(self):
        self.config = self.config_store.get_config()
        launcher_config_validator.validate(self.config)

    def setup_logging(self):
        log_level = self.config.get(LOG_LEVEL)
        log_format = self.config.get(LOG_FORMAT)
        logger = Logger(log_level=log_level, log_format=log_format)
        logger.setup()

    def setup_root(self):
        root_process_config_path = self.config.get(ROOT_PROCESS_CONFIG_PATH)
        self.root_process = cfg_parser.parse(root_process_config_path)

    def execute_root(self):
        self.root_process.compile()
        self.root_process.execute()
