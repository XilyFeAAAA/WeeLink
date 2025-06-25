# standard library
import uuid
from dataclasses import dataclass, field

# local library
from .adapter import Adapter
from .metadata import AdapterMetaData

@dataclass
class Bot:
    
    """机器人名"""
    alias: str
    
    """机器人介绍"""
    desc: str
    
    """创建时间"""
    create_time: int
    
    """状态"""
    is_running: bool
    
    """自启动"""
    auto_start: bool
    
    """适配器元信息"""
    adapter_metadata: AdapterMetaData

    """适配器实例"""
    adapter_obj: Adapter
    
    """适配器配置"""
    adapter_config: dict
    
    """机器人ID"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    
    
@dataclass
class BotConfig:

    """机器人名"""
    alias: str
    
    """机器人介绍"""
    desc: str
    
    """自启动"""
    auto_start: bool
    
    """适配器名"""
    adapter_name: str
    
    """适配器ID"""
    adapter_id: str    
    
    """适配器配置"""
    adapter_config: dict