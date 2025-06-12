# standard library
import uuid
from types import ModuleType
from dataclasses import dataclass

# local library
from .base import Plugin

@dataclass
class PluginMetaData:
    
    """启用"""
    enable: bool    
    
    """插件名"""
    name: str
    
    """插件作者"""
    author: str
    
    """插件版本"""
    version: str
    
    """插件模块"""
    module: ModuleType
    
    """支持的适配器, 默认支持全部"""
    adapters: list["Adapter"]
    
    """插件实例"""
    obj: Plugin
    
    """插件对象"""
    cls: type[Plugin]
    
    """插件描述"""
    desc: str = ""
    
    """插件仓库"""
    repo: str = ""
    
    """插件ID"""
    id: str = str(uuid.uuid4())
    
    
    async def check_version(self):
        pass
    
    
    def __repr__(self):
        return (f"<PluginMetaData name={self.name!r}, author={self.author!r}, "
                f"version={self.version!r}, enable={self.enable!r}>")