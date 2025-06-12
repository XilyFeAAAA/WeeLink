# standard library
import pickle

# local library
from weelink.core.utils import logger, redis


class Cache:
    
    def __init__(self, cache_ttl: int = 60 * 30) -> None:
        self.cache_ttl: int = cache_ttl
    
        
    async def get(self, cache_key: str) -> any:
        """获取Cache信息"""
        try:
            pickled_data =  await redis.get(key=cache_key)
            if pickled_data is None:
                return pickled_data
            return pickle.loads(pickled_data)
        except Exception as e:
            logger.error(f"Cache读取key错误 - {str(e)}")
    
    
    async def set(self, cache_key: str, cache_data: any) -> any:
        """设置Cache信息"""
        try:
            pickled_data = pickle.dumps(cache_data)
            await redis.set(key=cache_key, value=pickled_data, ex=self.cache_ttl)
            return cache_data
        except Exception as e:
            logger.error(f"Cache设置key错误 - {str(e)}")
    
    
    async def remove(self, cache_key: str) -> None:
        """移除指定群聊的缓存"""
        try:
            await redis.delete(key=cache_key)
        except Exception as e:
            logger.error(f"Cache删除key错误 - {str(e)}")
        

    async def exists(self, cache_key: str) -> bool:
        """判断缓存是否存在"""
        try:
            return await redis.exists(cache_key)
        except Exception as e:
            logger.error(f"缓存[{cache_key}]存在性检查失败: {e}")
            return False