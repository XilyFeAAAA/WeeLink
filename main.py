import asyncio
from src.bot import Bot
from src.utils import logger
from src.db.create import close_db_connection


class ChatBotApplication:
    """聊天机器人应用主类"""
    
    def __init__(self) -> None:
        self.bot: Bot

    async def startup(self) -> None:
        """应用启动"""
        logger.info("WeeLink 正在启动...")
        self.bot = await Bot.get_instance()
        await self.bot.preload()
        await self.bot.check_protocol()
        await self.bot.login()
        await self.bot.keeplive()
        logger.info("WeeLink 启动完成")


    async def shutdown(self) -> None:
        """应用关闭"""
        logger.info("WeeLink 正在关闭...")
        await self.bot.destroy()
        await close_db_connection()
        logger.info("WeeLink 已关闭")


    async def run(self) -> None:
        """运行应用"""
        try:
            await self.startup()
            await self.bot.run()
        except (KeyboardInterrupt, asyncio.CancelledError):
            logger.info("检测到 KeyboardInterrupt 退出信号")
        finally:
            await self.shutdown()


if __name__ == "__main__":
    app = ChatBotApplication()
    try:
        asyncio.run(app.run())
    except Exception as e:
        print(f"主程序异常: {e}")