from src.utils import logger
from src.config import conf
from redis import asyncio as aioredis
from typing import AsyncGenerator, Optional


class Redis:
    
    _instance: Optional["Redis"] = None
    
    def __new__(cls) -> "Redis":
        """单例 Redis"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self) -> None:
        self._redis = None
        

    async def run(self) -> None:
        """初始化 Redis"""
        host = conf().get("REDIS_HOST")
        port = conf().get("REDIS_PORT")
        if not host and not port:
            raise Exception("Redis 配置错误")
        self._redis = aioredis.Redis(host=host, port=port)
        
        try:
            pong = await self._redis.ping()
            if pong:
                logger.info("Redis 连接成功")
            else:
                raise Exception("连接超时")
        except Exception as e:
            import sys
            logger.error(f"Redis 连接错误: {e}")
            sys.exit()
            
            
    async def close(self) -> None:
        try:
            await self._redis.close()
            logger.info("Redis 关闭成功")
        except Exception as e:
            logger.error(f"Redis 关闭失败: {e}")
                        
            
    async def set(self, key: str, value: any, **kwargs) -> None:
        """写入 Redis"""
        try:
            await self._redis.set(key, value, **kwargs)
        except Exception as e:
            logger.error(f"Redis 写入失败: {key}, 错误: {e}")
            raise


    async def get(self, key: str, **kwargs) -> any:
        """读取 Redis"""
        try:
            return await self._redis.get(key, **kwargs)
        except Exception as e:
            logger.error(f"Redis 读取失败: {key}, 错误: {e}")
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