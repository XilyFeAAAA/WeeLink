from beanie import Document
from pymongo import IndexModel, ASCENDING
from typing import Optional

    
class BotDocument(Document):
    """微信账户信息表"""
    alias: str
    desc: str
    auto_start: bool
    adapter_id: str
    adapter_name: str
    adapter_config: dict

    class Settings:
        name = "bot"


class MessageDocument(Document):
    msg_id: int
    new_msg_id: int
    data: dict
    adapter_name: str
    
    class Settings:
        name = "message"
