from src.utils import logger, redis
from abc import ABC, abstractmethod
import pickle

class Cache(ABC):
    
    def __init__(self, cache_ttl: int = 60 * 30) -> None:
        self.cache_ttl: int = cache_ttl
    
    
    @abstractmethod
    async def update(self):
        raise NotImplementedError
    
    
    async def _get(self, cache_key: str) -> any:
        """获取Cache信息"""
        pickled_data =  await redis.get(key=cache_key)
        if pickled_data is None:
            return pickled_data
        return pickle.loads(pickled_data)
    
    
    async def _set(self, cache_key: str, cache_data: any) -> None:
        """设置Cache信息"""
        pickled_data = pickle.dumps(cache_data)
        return await redis.set(key=cache_key, value=pickled_data, ex=self.cache_ttl)
    
        
    async def _remove(self, cache_key: str) -> None:
        """移除指定群聊的缓存"""
        await redis.delete(key=cache_key)
        logger.debug(f"缓存[{self.cache_type}:{cache_key}]已移除")  
        

    async def _exists(self, cache_key: str) -> bool:
        """判断缓存是否存在"""
        try:
            return await redis.exists(cache_key)
        except Exception as e:
            logger.error(f"缓存[{cache_key}]存在性检查失败: {e}")
            return False