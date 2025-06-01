from enum import Enum, auto



class EventType(Enum):
    # MESSAGE
    TEXT = auto()
    VOICE = auto()
    IMAGE = auto()
    VIDEO = auto()
    EMOJI = auto()
    # XML
    UPLOAD = auto()
    FILE = auto()
    LINK = auto()
    QUOTE = auto()
    FORWARD = auto()
    # SYSTEM
    PAT = auto()
    INVITE = auto()
    REVOKE = auto()
    ANNOUNCE = auto()
    TODO = auto()
    FRIEND_ADD = auto()
    FRIEND_DEL = auto()
    FRIEND_MODIFY = auto()
    CHATROOM_ADD = auto()
    CHATROOM_DEL = auto()
    CHATROOM_INCREASE = auto()
    CHATROOM_DECREASE = auto()


class DataType(Enum):
    TEST = auto()
    ADDMSG = auto()
    MODCONTACTS = auto()
    DELCONTACTS = auto()
    OFFLINE = auto()


class MessageSource(Enum):
    CHATROOM = auto()
    FRIEND = auto()
    OTHER = auto()


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
    "AddMsgType", 
    "SystemMsgType", 
    "CacheType", 
    "XmlType", 
    "ModContactType", 
    "EventType", 
    "MessageSource"
]
