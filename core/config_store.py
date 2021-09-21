from utils.general.file_io import read_all_yaml_data


class ConfigStore:
    def __init__(self, config_path):
        self.config_path = config_path

    def get_config(self):
        with open(self.config_path) as stream:
            return read_all_yaml_data(stream)
