from beanie import Document
from typing import Optional

    
class Account(Document):
    """微信账户信息表"""

    uuid: str
    wxid: str
    nickname: str
    phone: str
    device_name: str
    device_id: str
    alias: Optional[str] = None

    class Settings:
        name = "account"