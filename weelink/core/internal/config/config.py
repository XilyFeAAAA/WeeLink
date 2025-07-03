# standard library
import json
from pathlib import Path

# local library
from .default_config import DEFAULT_CONFIG
from weelink.core.utils.paths import DATA_DIR

WEELINK_CONFIG_PATH: Path = DATA_DIR / "config.json"
WEELINK_CONFIG_SCHEME_PATH: Path = Path(__file__).parent / "scheme.json"

class WeelinkConfig(dict):

    def __init__(
        self,
        config_path = WEELINK_CONFIG_PATH,
        default_config = DEFAULT_CONFIG,
    ):
        if not WEELINK_CONFIG_PATH.exists():
            # 不存在测创建文件夹并且写入默认配置
            WEELINK_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
            WEELINK_CONFIG_PATH.touch()
            with open(WEELINK_CONFIG_PATH, "w") as f:
                json.dump(default_config, f, indent=4, ensure_ascii=False)
        
        with open(WEELINK_CONFIG_SCHEME_PATH, "r", encoding="utf-8") as f:
            self.scheme = json.loads(f.read())
        
        with open(WEELINK_CONFIG_PATH, "r") as f:
            conf = json.loads(f.read())
        
        self.update(conf)


    def __getitem__(self, key: str):
        try:
            return super().__getitem__(key)
        except KeyError:
            return None


    def __setitem__(self, key, value):
        try:
            super().__setitem__(key, value)
            self.save()
        except:
            raise Exception(f"Key: '{key}' 不存在")
    
    def save(self):
        if not WEELINK_CONFIG_PATH.exists():
            WEELINK_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
            WEELINK_CONFIG_PATH.touch()
        with open(WEELINK_CONFIG_PATH, "w") as f:
            json.dump(self or self, f, indent=4, ensure_ascii=False)

conf = WeelinkConfig()