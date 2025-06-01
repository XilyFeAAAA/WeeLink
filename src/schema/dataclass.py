from typing import Optional
from dataclasses import dataclass, field
from xml.etree import ElementTree


@dataclass
class ChatroomMember:
    """包含联系人和群成员的属性"""
    wxid: Optional[str] = None
    nickname: Optional[str] = None
    """微信昵称"""
    invite_wxid: Optional[str] = None
    displayname: Optional[str] = None
    """群名称"""
    big_image: Optional[str] = None
    small_image: Optional[str] = None
    
    @property
    def name(self) -> str:
        return self.displayname or self.nickname or self.wxid or "未知群聊成员" 
    
    
@dataclass
class Friend:
    wxid: Optional[str] = None
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    remark: Optional[str] = None
    alias: Optional[str] = None
    
    @property
    def name(self) -> str:
        return self.nickname or self.wxid or "未知好友"


@dataclass
class Chatroom:
    chatroom_id: Optional[str] = None
    nickname: Optional[str] = None
    remark: Optional[str] = None
    chatroom_owner: Optional[str] = None
    small_image: Optional[str] = None
    member_list: list[ChatroomMember] = field(default_factory=list)
    
    @property
    def name(self) -> str:
        return self.nickname or self.chatroom_id or "未知群聊"

@dataclass
class Contact:
    """联系人列表数据"""
    friends: list[str] = field(default_factory=list)
    """好友列表"""
    chatrooms: list[str] = field(default_factory=list)
    """群聊列表"""
    ghs: list[str] = field(default_factory=list)
    """公众号列表"""    


@dataclass
class Forward:
    """转发基类"""
    sourcename: str
    sourceheadurl: str
    sourcetime: str
    datadesc: str


@dataclass
class VoiceForward(Forward):
    """语音转发类"""
    pass


@dataclass
class TextForward(Forward):
    """文本转发类"""
    fromnewmsgid: str
    
    
@dataclass
class MediaForward(Forward):
    """媒体转发基类"""
    datafmt: str      # 数据格式
    cdndataurl: str   # CDN数据URL
    cdndatakey: str   # CDN数据密钥
    fullmd5: str      # 完整MD5值
    datasize: str     # 数据大小


@dataclass
class ImageForward(MediaForward):
    """图片转发数据"""
    pass


@dataclass
class VideoForward(MediaForward):
    """视频转发数据"""
    pass


@dataclass
class QuoteForward(Forward):
    """引用转发类"""
    fromnewmsgid: str
    refermsgitem: ElementTree.Element  # 目前还没想到优雅的办法解析引用


@dataclass
class LinkForward(Forward):
    """链接转发类"""
    sourcedisplayname: str
    weburlitem: ElementTree.Element

__all__ = [
    "ChatroomMember", 
    "Friend", 
    "Chatroom", 
    "Contact",
    "Forward",
    "VoiceForward",
    "TextForward",
    "MediaForward",
    "ImageForward",
    "VideoForward",
    "QuoteForward",
    "LinkForward"
]