# standard library
from enum import Enum, auto


class EventType(Enum):
    # LIFESTYLE
    STARTUP = auto()
    SHUTDOWN = auto()
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