import importlib
import requests
import shutil
import os


def get_class_based_on_class_type(class_type, class_mapping):
    class_path = class_mapping[class_type]
    module_path, _, class_name = class_path.rpartition(".")
    return getattr(importlib.import_module(module_path), class_name)


def download_file(url, out_path):
    with requests.get(url, stream=True) as stream:
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "wb") as fp:
            stream.raw.decode_content = True
            shutil.copyfileobj(stream.raw, fp)


def join(*args):
    return os.path.join(*args)


def scrape_dir(dir):
    for filename in os.listdir(dir):
        yield filename
