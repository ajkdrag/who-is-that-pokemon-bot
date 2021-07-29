import json
import logging
import time
import logging.config
from typing import Dict, Optional


class Singleton(type):
    _instances: Dict = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class BaseFormatter(logging.Formatter):
    def __init__(self, **kwargs):
        if "extraArgs" in kwargs:
            self.extraArgs = kwargs.get("extraArgs")
            del kwargs["extraArgs"]
        super().__init__(**kwargs)

    def formatTime(self, record, datefmt=None):
        ct = self.converter(record.created)
        if not datefmt:
            datefmt = "%Y-%m-%d %H:%M:%S"
        return time.strftime(datefmt, ct)

    def formatException(self, exc_info):
        result = super().formatException(exc_info)
        if result:
            result = result.replace("\n", " ")
        return result


class StandardFormatter(BaseFormatter):
    def format(self, record):
        formatted_record = []
        record.message = record.getMessage()
        record.asctime = self.formatTime(record, self.datefmt)
        formatted_record.append(record.asctime)
        if self.extraArgs is not None:
            for val in self.extraArgs.values():
                formatted_record.append(val)
        for key in ["module", "funcName", "levelname"]:
            formatted_record.append(getattr(record, key))
        formatted_record.append(record.message)
        if record.exc_info:
            formatted_record.append(self.formatException(record.exc_info))
        return " | ".join(map(str, formatted_record))


class JsonFormatter(BaseFormatter):
    def format(self, record):
        formatted_record = dict()
        record.message = record.getMessage()
        record.asctime = self.formatTime(record, self.datefmt)
        formatted_record["created"] = record.asctime
        if self.extraArgs is not None:
            for key, val in self.extraArgs.items():
                formatted_record[key] = val
        for key in ["module", "funcName", "levelname"]:
            formatted_record[key] = getattr(record, key)
        formatted_record["message"] = record.message
        if record.exc_info:
            formatted_record["traceback"] = self.formatException(record.exc_info)
        return json.dumps(formatted_record, indent=4)


class Logger(metaclass=Singleton):
    def __init__(
        self,
        log_level: Optional[str] = None,
        log_format: Optional[str] = None,
        **kwargs
    ) -> None:
        default_log_level = "INFO"
        default_format_type = "standard"

        valid_format_types = {"json", "standard"}
        valid_log_level_types = {
            "DEBUG",
            "INFO",
            "WARN",
            "WARNING",
            "CRITICAL",
            "ERROR",
        }

        if log_format is None or log_format not in valid_format_types:
            log_format = default_format_type

        if log_level is None or log_level.upper() not in valid_log_level_types:
            log_level = default_log_level

        self.extraArgs = kwargs
        self.log_level = log_level
        self.log_format = log_format

        self.config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {
                    "()": StandardFormatter,
                    "extraArgs": self.extraArgs,
                },
                "json": {
                    "()": JsonFormatter,
                    "extraArgs": self.extraArgs,
                },
            },
            "handlers": {
                "standard": {
                    "class": "logging.StreamHandler",
                    "formatter": self.log_format,
                    "stream": "ext://sys.stdout",
                }
            },
            "loggers": {
                "": {
                    "handlers": ["standard"],
                    "level": logging.getLevelName(self.log_level.upper()),
                }
            },
        }

    def setup(self):
        logging.config.dictConfig(self.config)
        LOG = logging.getLogger(__name__)
        LOG.info(
            "Logging setup completed. Using format: %s, with log_level: %s",
            self.log_format,
            self.log_level,
        )

    def update_logger(self, **kwargs):
        self.extraArgs.update(kwargs)
        self.setup()
