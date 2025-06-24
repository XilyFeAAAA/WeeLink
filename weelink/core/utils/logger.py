# standard library
import os
import sys
import asyncio
from loguru import logger
from pathlib import Path

# 获取项目根目录 - 使用当前工作目录
root_dir = Path.cwd()

# 日志目录
log_dir = root_dir / "logs"
os.makedirs(log_dir, exist_ok=True)


def queue_sink(message):
    from .sse import sse_manager
    
    record = message.record
    sse_manager.send_message("log", {
        'message': record['message'],
        'level': record['level'].name,
        'path': record['file'].path,
        'line': record['line'],
        'function': record['function'],
        'time': record['time'].isoformat()
    })

# loggers
logger.remove()
logger.add(
    sys.stdout,
    level="DEBUG",
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}"
)
logger.add(
    log_dir / "weelink_{time:YYYY-MM-DD}.log",
    rotation="1 day",
    retention="7 days",
    compression="zip",
    level="INFO",
    encoding="utf-8",
    enqueue=True,
    backtrace=True,
    diagnose=True
)
logger.add(queue_sink)

__all__ = [
    "logger"
]