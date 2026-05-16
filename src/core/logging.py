"""结构化日志配置 — 生产环境输出 JSON 格式，开发环境保持人类可读。"""

import logging
import sys

from core.config import settings


class RequestIdFilter(logging.Filter):
    """日志过滤器：自动注入 request_id 到每条日志。"""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = getattr(record, "request_id", "-")
        return True


def setup_structured_logging(level: str = "INFO") -> None:
    is_dev = settings.MODE.lower() in ("dev", "development")

    root = logging.getLogger()
    if root.handlers:
        return
    root.handlers.clear()
    root.setLevel(getattr(logging, level.upper(), logging.INFO))

    handler = logging.StreamHandler(sys.stdout)
    handler.addFilter(RequestIdFilter())

    if is_dev:
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | [%(request_id)s] | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    else:
        try:
            from pythonjsonlogger import jsonlogger
            formatter = jsonlogger.JsonFormatter(
                fmt="%(asctime)s %(levelname)s %(name)s %(message)s %(request_id)s",
                datefmt="%Y-%m-%dT%H:%M:%S",
                rename_fields={
                    "asctime": "timestamp",
                    "levelname": "level",
                    "name": "logger",
                },
            )
        except ImportError:
            formatter = logging.Formatter(
                fmt="%(asctime)s | %(levelname)-8s | %(name)s | [%(request_id)s] | %(message)s",
                datefmt="%Y-%m-%dT%H:%M:%S",
            )

    handler.setFormatter(formatter)
    root.addHandler(handler)

    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("litellm").setLevel(logging.WARNING)
