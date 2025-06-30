from beanie import Document

    
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
    source: str
    content: str
    fromname: str
    
    class Settings:
        name = "message"
