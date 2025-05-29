from src.utils import logger
from pathlib import Path
import json
import threading


class Config:
    
    def __init__(self, config_file: str = "config.json") -> None:
        self.config_file = Path(config_file)
        self._data: dict[str, any] = {}
        self._lock = threading.Lock()
    
    def load(self) -> None:
        """加载配置文件"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self._data = json.load(f)
            else:
                # 创建默认配置
                self._data = {
                    "MESSAGE_QUEUE": {"enable": True, "interval": 2.0},
                    "WHITELIST": {"enable": True, "users": [], "chatrooms": []},
                    "BASEURL": "http://127.0.0.1:9000",
                    "REDIS_HOST": "127.0.0.1",
                    "REDIS_PORT": 6379,
                    "REDIS_PASSWORD": "",
                    "REDIS_DB": 0
                }
                self.save()
        except Exception as e:
            logger.error(f"加载配置失败: {e}")
            
    def save(self) -> None:
        """保存配置到文件"""
        with self._lock:
            try:
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(self._data, f, indent=4, ensure_ascii=False)
            except Exception as e:
                logger.error(f"保存配置失败: {e}")
        
    def get(self, key: str, default: any = None) -> any:
        """获取配置键"""
        return self._data.get(key, default)
    
    def update(self, key: str, value: any) -> None:
        """设置配置键"""
        with self._lock:
            self._data[key] = value
            self.save()
            
_config = Config()
_config.load()

def conf():
    return _config