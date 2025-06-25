# standard library
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

# local library
from weelink.core.utils import logger
from weelink.core.internal.config import conf
from weelink.core.internal.db.model import BotDocument, MessageDocument


class MongoDB:
    """MongoDB连接管理器"""
    
    def __init__(self):
        self.client = None
        self.db = None
        self._connected: bool = False

    async def connect(self) -> None:
        """建立数据库连接并初始化Beanie"""
        try:
            self.client = AsyncIOMotorClient(conf["MONGO_URI"])
            await self.client.server_info()
            self.db = self.client[conf["MONGO_DB_NAME"]]
            
            await init_beanie(
                database=self.db,
                document_models=[
                    BotDocument,
                    MessageDocument
                ],
                allow_index_dropping=False
            )
            self.is_connected = True
            logger.success("MongoDB 连接成功")
            
        except Exception as e:
            self._connected = False
            logger.critical(f"MongoDB 连接失败: {e}")
            raise


    def close(self) -> None:
        """关闭数据库连接"""
        if self.client is not None and self._connected:
            self.client.close()
            self._connected = False
            logger.success("MongoDB 连接关闭")


