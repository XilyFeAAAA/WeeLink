# standard library
import sys
from typing import AsyncGenerator
from redis import asyncio as aioredis

# local library
from weelink.core.utils import logger
from weelink.core.internal.config import conf

class Redis:
    
    
    def __init__(self) -> None:
        self.host = conf["REDIS_HOST"]
        self.port = conf["REDIS_PORT"]
    
    async def connect(self) -> None:
        if not self.host and not self.port:
            raise Exception("Redis 配置错误")
        try:
            self._redis = aioredis.Redis(host=self.host, port=self.port)
        except:
            logger.critical("Redis服务连接失败，请检查配置文件")
            sys.exit()


    async def close(self) -> None:
        try:
            await self._redis.close()
            logger.success("Redis 关闭成功")
        except Exception as e:
            logger.error(f"Redis 关闭失败: {e}")
                        
            
    async def set(self, key: str, value: any, **kwargs) -> None:
        """写入 Redis"""
        try:
            await self._redis.set(key, value, **kwargs)
            return value
        except Exception as e:
            logger.error(f"Redis 写入失败: {key}, 错误: {e}")
            raise


    async def get(self, key: str, **kwargs) -> any:
        """读取 Redis"""
        try:
            return await self._redis.get(key, **kwargs)
        except Exception as e:
            logger.error(f"Redis 读取失败: {key}, 错误: {e}")
            
            logger.debug(self)
            raise
        
        
    async def delete(self, key: str, **kwargs) -> None:
        """删除 Redis"""
        try:
            await self._redis.delete(key, **kwargs)
            logger.debug(f"Redis 删除成功: {key}")
        except Exception as e:
            logger.error(f"Redis 删除失败: {key}, 错误: {e}")
            raise
        
        
    async def async_scan_keys(self, pattern: str = '*') -> AsyncGenerator[bytes, None]:
        """异步 key 扫描生成器 (使用 aioredis)"""
        async for key in self._redis.scan_iter(match=pattern):
            yield key
            
            
    async def exists(self, key: str) -> bool:
        """
        判断指定 key 是否存在于 Redis
        """
        try:
            return bool(await self._redis.exists(key))
        except Exception as e:
            logger.error(f"Redis exists 检查失败: {key}, 错误: {e}")
            raise
        
redis = Redis()