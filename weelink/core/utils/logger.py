# standard library
import os
import sys
from loguru import logger
from pathlib import Path

# 注意：这里不能直接导入 paths 模块，因为 paths 模块会导入 logger 模块，会导致循环导入
# 所以这里直接计算日志目录路径

# 获取项目根目录 - 使用当前工作目录
root_dir = Path.cwd()

# 日志目录
log_dir = root_dir / "logs"
os.makedirs(log_dir, exist_ok=True)

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

__all__ = [
    "logger"
]