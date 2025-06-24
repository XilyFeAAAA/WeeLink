# standard library
from dataclasses import dataclass

# local library
from .base import Plugin
from .config import PluginConfig


@dataclass
class PluginMetaData:
    
    
    """插件名"""
    name: str
    
    """插件作者"""
    author: str
    
    """插件版本"""
    version: str
    
    """插件模块"""
    module: str
    
    """支持的适配器, 默认支持全部"""
    adapters: list[type["Adapter"]]
    
    """插件实例"""
    obj: Plugin
    
    """插件对象"""
    cls: type[Plugin]
    
    """插件描述"""
    desc: str = ""
    
    """插件仓库"""
    repo: str = ""
    
    """插件配置"""
    config: PluginConfig = None
        
    
    async def check_version(self):
        pass
    
    
    def __repr__(self):
        return (f"<PluginMetaData name={self.name!r}, author={self.author!r}, version={self.version!r}>")