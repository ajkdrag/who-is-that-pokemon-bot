import docker
import logging
from pathlib import Path

LOG = logging.getLogger(__name__)


class Server:
    def __init__(self, config):
        self.config = config

    def setup(self):
        self.model_nm = self.config.get("model_name")
        self.model_dir = Path("models").absolute()
        self.url = f"http://localhost:8501/v1/models/{self.model_nm}:predict"
        self.client = docker.from_env()

    def start(self):
        LOG.info("Starting container...")
        container = self.client.containers.run(
            self.config.get("serving_image"),
            environment={"MODEL_NAME": self.model_nm},
            ports={"8501/tcp": 8501},
            volumes={self.model_dir: {"bind": "/models", "mode": "ro"}},
            detach=True,
        )
        LOG.info(container.logs())
