import yaml


def read_all_yaml_data(stream):
    return yaml.safe_load(stream)
