from abc import ABC, abstractmethod


class BaseProcess(ABC):
    def __init__(self, name, proc_type, is_active, is_sequential, config):
        self.name = name
        self.proc_type = proc_type
        self.is_active = is_active
        self.is_sequential = is_sequential
        self.config = config
        self.subprocesses = []

    def add_subprocess(self, another_process):
        self.subprocesses.append(another_process)

    def execute(self):
        for subprocess in self.subprocesses:
            subprocess.execute()
        self._execute()

    @abstractmethod
    def _execute(self):
        ...
