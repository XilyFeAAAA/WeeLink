import os
from pathlib import Path

# 项目根目录 - 使用当前工作目录
ROOT_DIR = Path.cwd()

# 数据目录
DATA_DIR = ROOT_DIR / "data"
# 日志目录
LOGS_DIR = DATA_DIR / "logs"
# 配置目录
CONFIG_DIR = DATA_DIR / "configs"
# 插件目录
PLUGIN_DIR = DATA_DIR  / "plugins"
# 适配器目录
ADAPTER_DIR = ROOT_DIR / "weelink" / "core" / "adapter"
# 临时文件目录
TEMP_DIR = DATA_DIR / "temp"


# 确保所有必要的目录存在
def ensure_directories():
    """确保所有必要的目录都存在，如果不存在则创建"""
    directories = [
        DATA_DIR,
        LOGS_DIR,
        TEMP_DIR
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

# 获取相对于根目录的路径
def get_path(relative_path):
    """获取相对于根目录的绝对路径"""
    return ROOT_DIR / relative_path


# 获取日志文件路径
def get_log_path(log_name):
    """获取日志文件的路径"""
    return LOGS_DIR / log_name 


def find_temp_file(md5: str):
    if not TEMP_DIR.exists():
        TEMP_DIR.mkdir(parents=True)
    
    for filename in os.listdir(TEMP_DIR):
        if filename.startswith(f"{md5}."):
            return filename
    return None



__all__ = [
    "ROOT_DIR",
    "DATA_DIR",
    "LOGS_DIR",
    "CONFIG_DIR",
    "PLUGIN_DIR",
    "ADAPTER_DIR",
    "TEMP_DIR",
    "ensure_directories",
    "get_path",
    "get_log_path",
    "find_temp_file"
]