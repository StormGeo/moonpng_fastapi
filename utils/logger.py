import json
import logging
import sys
from datetime import datetime


class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
        }
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_record)


def get_logger(name="moonpng"):
    logger = logging.getLogger(name)

    if logger.hasHandlers():
        return logger  # evita duplicação em reloads

    logger.setLevel(logging.INFO)

    # Formatação JSON
    json_formatter = JsonFormatter()

    # Terminal (stdout)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(json_formatter)
    logger.addHandler(stream_handler)

    # Arquivo
    file_handler = logging.FileHandler("moonpng_requests.log")
    file_handler.setFormatter(json_formatter)
    logger.addHandler(file_handler)

    return logger
