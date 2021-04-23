import typing
import os
import time
import uuid
import logging
import traceback
from logging.handlers import RotatingFileHandler
from flask import g, has_request_context, request

from config.settings import LOG_DIR
from utils.fs import make_dirs

logger = logging.getLogger("app")


def get_request_attrs(*attrs):
    result = {}
    for attr in attrs:
        if hasattr(request, attr):
            result[attr] = getattr(request, attr)
    return result


def bind_request_id_to_g():
    g.request_id = str(uuid.uuid4())


def get_request_id():
    if not hasattr(g, "request_id"):
        bind_request_id_to_g()
    return g.request_id


class RequestIdFilter(logging.Filter):
    def filter(self, record):
        record.request_id = get_request_id() if has_request_context() else "----"
        return True


def log_err(func: typing.Callable):
    def log_func(err: Exception):
        logger.error(traceback.format_exc())
        return func(err)

    return log_func


def add_console_handler(*loggers: logging.Logger) -> None:
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(
        logging.Formatter(
            "%(request_id)s - %(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)s - %(message)s"
        )
    )
    stream_handler.addFilter(RequestIdFilter())
    stream_handler.setLevel(logging.INFO)

    for l in loggers:
        l.addHandler(stream_handler)


def add_file_handler(*loggers: logging.Logger) -> None:
    make_dirs(LOG_DIR)
    log_file_path = os.path.join(LOG_DIR, time.strftime("%Y-%m-%d", time.localtime(time.time())) + ".log")
    file_handler = RotatingFileHandler(log_file_path)
    file_handler.setFormatter(
        logging.Formatter(
            "%(request_id)s - %(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)s - %(message)s"
        )
    )
    file_handler.addFilter(RequestIdFilter())
    file_handler.setLevel(logging.INFO)

    for l in loggers:
        l.addHandler(file_handler)
