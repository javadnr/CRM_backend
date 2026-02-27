import logging
import os
from logging.handlers import TimedRotatingFileHandler


LOG_DIR = "logs"

LEVEL_DIRS = {
    "DEBUG": f"{LOG_DIR}/debug",
    "INFO": f"{LOG_DIR}/info",
    "WARNING": f"{LOG_DIR}/warning",
    "ERROR": f"{LOG_DIR}/error",
}


def create_log_dirs():
    for path in LEVEL_DIRS.values():
        os.makedirs(path, exist_ok=True)


def get_file_handler(level: str):
    handler = TimedRotatingFileHandler(
        filename=f"{LEVEL_DIRS[level]}/{level.lower()}.log",
        when="midnight",
        interval=1,
        backupCount=10,
        encoding="utf-8",
    )

    handler.setLevel(getattr(logging, level))

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    handler.setFormatter(formatter)
    return handler


def setup_logging():

    create_log_dirs()

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    # ---- console handler ----
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(
        logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        )
    )

    root_logger.addHandler(console)

    # ---- file handlers ----
    for level in LEVEL_DIRS.keys():
        root_logger.addHandler(get_file_handler(level))