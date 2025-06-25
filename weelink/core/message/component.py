# standard library
from pathlib import Path
from dataclasses import dataclass

# local library
from weelink.core.message import AddMsgType


@dataclass
class MessageComponent:
    
    """消息时间"""
    create_time: int

@dataclass
class AddMessage(MessageComponent):
    
    """消息ID"""
    msg_id: int
    
    """消息新ID"""
    new_msg_id: str
    
    """消息source字段"""
    msg_source: str
    
    """消息sequence字段"""
    msg_seq: int
    
    """消息原始内容"""
    content: str
    
    def __repr__(self) -> str:
        """返回消息的字符串表示"""
        return f"{self.__class__.__name__}(msg_id={self.msg_id})"


@dataclass
class Text(AddMessage):
    
    """处理后的消息文本"""
    text: str


@dataclass
class File(AddMessage):
    
    """文件路径"""
    path: Path
    
    """文件MD5"""
    md5: str
    
    """文件扩展名"""
    ext: str


@dataclass
class Emoji(AddMessage):
    pass


@dataclass
class Link(AddMessage):
    
    """链接标题"""
    title: str
    
    """链接描述"""
    desc: str
    
    """链接地址"""
    url: str
    
    """链接用户名"""
    username: str
    
    """链接展示名"""
    displayname: str


@dataclass
class Quote(AddMessage):
    
    """引用类型"""
    quote_type: AddMsgType
    
    """引用标题"""
    title: str
    
    """引用内容(组件)"""
    component: MessageComponent


@dataclass
class Forward(AddMessage):
    ...


__all__ = [
    "MessageComponent",
    "Text",
    "File",
    "Emoji",
    "File",
    "Link",
    "Quote",
    "Forward"
]