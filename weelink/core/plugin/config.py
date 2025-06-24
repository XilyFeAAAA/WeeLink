# standard library
import json

# local library
from weelink.core.utils import logger
from weelink.core.utils.paths import PLUGIN_DIR, CONFIG_DIR

class PluginConfig:
    """
    1. 实例化时候传folder_name去data/config下面读
    2. 不存在的话找config_scheme.json复制一份
    """
    
    
    def __init__(self, folder_name: str) -> None:
        self._conf = {}
        self._scheme = {}
        self.folder_name = folder_name
        self.config_path = CONFIG_DIR / f"{folder_name}_config.json"
        self.scheme_path = PLUGIN_DIR / folder_name / "scheme.json"
        
        self.load()
    
    
    def create(self):
        """根据scheme创建config"""        
        config = { item["key"]: item["default"] for item in self._scheme}
        
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)        
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
    
    
    def load(self):
        """读取配置"""
        if not self.scheme_path.exists():
            return logger.warning(f"插件 {self.folder_name} 配置模板不存在")
        with open(self.scheme_path, "r", encoding='utf-8') as f:
            self._scheme = json.load(f)
        
        if not self.config_path.exists():
            self.create()
    
        if self.config_path.exists():
            with open(self.config_path, "r", encoding='utf-8') as f:
                self._conf = json.load(f)
        else:
            logger.warning(f"插件 {self.folder_name} 配置读取失败")
    
    
    def save(self) -> None:
        """保存插件配置"""
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)        
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self._conf, f, ensure_ascii=False, indent=4)
    
    
    def update(self, new_conf: dict):
        """更新插件配置"""
        for key, value in new_conf.items():
            self._conf[key] = value
        self.save()
    
    def __getitem__(self, key: str) -> any:
        """重写[]"""
        if key in self._conf:
            return self._conf[key]
    
    
    def __setitem__(self, key: str, value: any) -> None:
        """重写[] = """
        self._conf[key] = value
    
    def output(self) -> tuple[dict, dict]:
        """返回scheme和conf"""
        return self._scheme, self._conf