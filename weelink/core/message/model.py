# standard library
from typing import Optional
from enum import Enum, auto
from xml.etree import ElementTree
from dataclasses import dataclass, field


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



class DataType(Enum):
    TEST = auto()
    ADDMSG = auto()
    MODCONTACTS = auto()
    DELCONTACTS = auto()
    OFFLINE = auto()


class AddMsgType(int, Enum):
    UNKNOWN = 0
    TEXT = 1
    IMAGE = 3
    VOICE = 34
    FRIENDADD = 37
    POSSIBLE_FRIEND_MSG = 40
    NAMECARD = 42
    VIDEO = 43
    EMOJI = 47
    LOCATION = 48
    APPMSG = 49 #  xml消息：公众号/文件/小程序/引用/转账/红包/视频号/群聊邀请/多选消息
    SYNC = 51 # 状态同步
    GROUPOP = 10000 # 被踢出群聊/更换群主/修改群名称
    SYSTEMMSG = 10002 # 撤回/拍一拍/成员被移出群聊/解散群聊/群公告/群待办
    

class SystemMsgType(str, Enum):
    REVOKE = "revokemsg"
    PAT = "pat"
    KICKOUT = "kickout"
    DISMISS = "dismiss"
    ANNOUNCEMENT = "mmchatroombarannouncememt"
    TODO = "roomtoolstips"
    EXTINFO = "ClientCheckGetExtInfo"
    FUNCTION = "functionmsg"
    TEMPLATE = "sysmsgtemplate"


class CacheType(Enum):
    FRIEND = auto()
    CHATROOM = auto()
    CONTACT = auto()
    
    
class XmlType(int, Enum):
    QUOTE = 57
    SHARE_LINK = 5
    FILE = 6
    FORWORD = 19 
    UPLOAD = 74


class ModContactType(Enum):
    NICKNAME_CHANGED = auto()
    REMARK_CHANGED = auto()
    OWNER_CHANGED = auto()
    MEMBER_DECREASED = auto()
    MEMBER_INCREASED = auto()
    UNKNOWN = auto()



__all__ = [
    "ChatroomMember", 
    "Friend", 
    "Chatroom", 
    "Contact",
    "DataType", 
    "AddMsgType", 
    "SystemMsgType", 
    "CacheType", 
    "XmlType", 
    "ModContactType"
]