from src.db.model import Account
from src.utils import logger
from src import config
from beanie import init_beanie
from typing import AsyncGenerator
from contextlib import asynccontextmanager
from motor.motor_asyncio import AsyncIOMotorClient

class MongoDB:
    """企业级MongoDB连接管理器"""
    
    def __init__(self):
        self.client = None
        self.db = None
        self._connected: bool = False

    async def connect(self) -> None:
        """建立数据库连接并初始化Beanie"""
        try:
            self.client = AsyncIOMotorClient(config.MONGO_URI)
            await self.client.server_info()
            self.db = self.client[config.MONGO_DB_NAME]
            
            await init_beanie(
                database=self.db,
                document_models=[
                    Account, 
                ],
                allow_index_dropping=False
            )
            self.is_connected = True
            logger.success("MongoDB 连接成功")
            
        except Exception as e:
            self._connected = False
            logger.critical(f"MongoDB 连接失败: {e}")
            raise


    async def close(self) -> None:
        """关闭数据库连接"""
        if self.client and self._connected:
            self.client.close()
            self._connected = False
            logger.success("MongoDB 连接关闭")




db = MongoDB()
