import logging
from libs.backend.file_io import read_all_yaml_data
from utils.validators.process_config_validator import validate
from utils.functions import get_class_based_on_class_type
from utils.constants.config_contract import PROC_TYPE_MAP

LOG = logging.getLogger(__name__)


def parse(config_path):
    with open(config_path) as stream:
        config = read_all_yaml_data(stream)

    validate(config)

    proc_name = config.get("name")
    proc_type = config.get("proc_type")
    proc_is_active = config.get("is_active")
    proc_is_sequential = config.get("is_sequential")
    proc_config = config.get("config")
    proc_subprocesses = config.get("subprocesses")

    process = get_class_based_on_class_type(proc_type, PROC_TYPE_MAP)(
        proc_name, proc_type, proc_is_active, proc_is_sequential, proc_config
    )

    if proc_subprocesses:
        for proc_subprocess in proc_subprocesses:
            subprocess = parse(proc_subprocess.get("config_path"))
            process.add_subprocess(subprocess)

    return process
