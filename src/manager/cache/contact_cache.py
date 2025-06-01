from src.schema import Contact
from src.utils import logger
from .cache import Cache
import asyncio


class ContactCache(Cache):
    
    def __init__(self) -> None:
        super().__init__()
        self._locks: dict[str, asyncio.Lock] = {}
        
    async def update(self) -> Contact:
        """
        调用接口更新联系人信息
        TODO 暂时只有好友列表
        """
        return await self._set("contact", Contact(friends=await bot.get_friends()))
        

    async def get(self) -> Contact | None:
        if contact_info := await self._get("contact"):
            return contact_info
        async with self._lock:
            if contact_info := await self._get("contact"):
                return contact_info
            logger.warning(f"联系人缓存不存在，正在获取")
            contact_info = await self.update()
            return contact_info