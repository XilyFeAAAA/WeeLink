from src.bot import Bot
from src.model import Friend
from src.utils import logger
from .cache import Cache
import asyncio


bot = Bot.get_instance()

class FriendCache(Cache):
    
    def __init__(self) -> None:
        super().__init__()
        self._locks: dict[str, asyncio.Lock] = {}


    async def update(self, wxid: str) -> Friend:
        """调用接口更新好友信息"""
        friends = await bot.get_friend_info(wxid)
        if len(friends) != 1: 
            raise RuntimeError(f"获取好友信息失败，错误提示:返回联系人数量为{len(friends)}")
        
        logger.info(f"好友{wxid}信息已缓存")
        return await self._set(cache_key=wxid, cache_data=Friend(
            wxid=wxid,
            nickname=friends[0].get("UserName", {}).get("string"),
            avatar=friends[0].get("BigHeadImgUrl") or friends.get("SmallHeadImgUrl"),
            remark=friends[0].get("Remark", {}).get("string"),
            alias=friends[0].get("Alias"),
        ))
                

    async def get(self, wxid: str) -> Friend | None:
        if friend_info := await self._get(wxid):
            return friend_info
        lock = self._locks.setdefault(wxid, asyncio.Lock())
        async with lock:
            if not (friend_info := await self._get(wxid)):
                logger.warning(f"好友{wxid}缓存不存在，正在获取")
                friend_info = await self.update(wxid)
            return friend_info
        
        
    async def exist(self, wxid: str) -> bool:
        """检查好友是否存在于缓存中"""
        return await self._exists(wxid)