# standard library
import os
import sys
import json
from loguru import logger
from datetime import date

# local library
from .paths import LOGS_DIR

# 确保目录存在
os.makedirs(LOGS_DIR, exist_ok=True)


# SSE管理器
def queue_sink(message):
    from .sse import sse_manager
    
    record = message.record
    sse_manager.send_message("log", {
        'message': record['message'],
        'level': record['level'].name,
        'path': record['file'].path,
        'line': record['line'],
        'function': record['function'],
        'time': record['time'].timestamp()
    })


class LoggerManager:
    """日志管理器，提供日志配置和检索功能"""
    
    def __init__(self) -> None:
        # 移除默认处理器
        logger.remove()
        
        # 添加处理器
        self.console_handler = logger.add(
            sys.stdout,
            level="DEBUG",
            format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}"
        )
        
        self.file_handler = logger.add(
            LOGS_DIR / "weelink_{time:YYYY-MM-DD}.log",
            rotation="1 day",
            retention="7 days",
            compression="zip",
            level="INFO",
            encoding="utf-8",
            enqueue=True,
            backtrace=True,
            diagnose=True,
            serialize=True
        )
        
        self.sse_handler = logger.add(queue_sink)
    
    def get_today_logs(self):
        """获取当日日志"""
        today = date.today()
        log_file = LOGS_DIR / f"weelink_{today.strftime('%Y-%m-%d')}.log"
        
        if not log_file.exists():
            return []
        
        logs = []
        try:
            with open(log_file, "r", encoding="utf-8") as f:
                for line in f:
                    log_data = json.loads(line)
                    record = log_data["record"]
                    logs.append({
                        'message': record['message'],
                        'level': record['level']["name"],
                        'path': record['file']["path"],
                        'line': record['line'],
                        'function': record['function'],
                        'time': record['time']["timestamp"]
                    })
        except Exception as e:
            logger.error(f"读取日志文件失败: {e}")
        
        return logs

log_manager = LoggerManager()
__all__ = [
    "logger",
    "log_manager"
]