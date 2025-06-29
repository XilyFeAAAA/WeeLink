# standard library
import uuid
from enum import Enum, auto
from dataclasses import dataclass, field
# local library
from .component import MessageComponent
from .model import Chatroom, ChatroomMember, Friend
from weelink.core.flow.event import EventType
from weelink.core.adapter import AdapterMetaData, Adapter



class MessageSource(Enum):
    CHATROOM = auto()
    FRIEND = auto()
    SYSTEM = auto()


@dataclass
class MessageEvent:

    
    """消息来源"""
    source: MessageSource
    
    """消息发送人"""
    sender: ChatroomMember | Friend
    
    """消息会话"""
    conversation: Chatroom | Friend    
    
    """适配器元信息"""
    adapter_md: AdapterMetaData
    
    """原始数据"""
    data: dict
    
    """事件类型"""
    event_type: EventType
    
    """消息"""
    component: MessageComponent
    
    """谁否被AT"""
    is_at: bool = False

    """消息机器人"""
    bot: Adapter = None
    
    """AT对象"""
    ats: list[ChatroomMember] = field(default_factory=list)
    
    """消息ID"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    def __repr__(self) -> str:
        return f"MessageEvent(id={self.id}, event_type={self.event_type}, adapter={self.adapter_obj.__class__.__name__})"