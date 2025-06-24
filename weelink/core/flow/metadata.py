# standard library
import uuid
from types import ModuleType
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

# local library
from .event import EventType
from weelink.core.plugin.metadata import PluginMetaData

if TYPE_CHECKING:
    from weelink.core.on.rule import Rule


@dataclass(order=True)
class HandlerMetaData:
    
    """优先级"""
    priority: int
    
    """一次性检查"""
    temp: bool = field(compare=False)
    
    """阻塞检查"""
    block: bool = field(compare=False)
    
    """过期时间"""
    expire_time: int = field(compare=False)
    
    """回调方法"""
    callback: callable = field(compare=False)
    
    """模块"""
    module: ModuleType = field(compare=False)
    
    """插件"""
    plugin: PluginMetaData = field(compare=False)
    
    """事件类型"""
    event_type: EventType = field(compare=False)
    
    """规则"""
    rule: "Rule" = field(compare=False)

    """ID"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def __repr__(self):
        return (f"<Subscriber id={self.id} module={self.module.__name__} "
                f"event={self.event_type} priority={self.priority}>")