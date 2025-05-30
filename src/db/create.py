from src.utils import logger
from .base import Base
from .engine import async_engine

async def init_models():
    async with async_engine.begin() as session:
        await session.run_sync(Base.metadata.drop_all)
        await session.run_sync(Base.metadata.create_all)
        
    logger.warning("初始化Mysql数据库成功")

async def close_db_connection():
    await async_engine.dispose()
    logger.info("数据库连接已关闭")
