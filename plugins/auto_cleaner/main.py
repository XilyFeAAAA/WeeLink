from src.bot import Bot
from src.plugin import PluginBase
from src.utils import logger, Redis
import os


class AutoCleaner(PluginBase):
    
    __description__ = "缓存文件自动清理"
    __author__ = "xilyfe"
    __version__ = "1.0.0"


    async def async_init(self, bot: Bot) -> None:
        """初始化"""
        bot.add_task(
            handle=self.cleaner,
            task_id="auto-cleaner",
            trigger="interval",
            minutes=60
        )
    
    
    async def cleaner(self) -> None:
        """清理tmp"""
        tmp_dir = os.path.join(os.getcwd(), "tmp")
        if not os.path.exists(tmp_dir):
            logger.info("tmp目录不存在，无需清理")
            return
        
        redis = Redis()
        to_del = []
        for fname in os.listdir(tmp_dir):
            if not await redis.exists(key=fname):
                to_del.append(fname)
        try:
            for file_name in to_del:
                file_path = os.path.join(tmp_dir, file_name)
                os.remove(file_path)
                logger.info(f"已删除过期缓存: {file_name}")
        except Exception as e:
            logger.error(f"删除缓存图片文件失败, 错误: {e}")