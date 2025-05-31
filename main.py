import asyncio
from src.bot import Bot
from src.utils import logger, Exc
from src.db.create import close_db_connection

class ChatBotApplication:
    """聊天机器人应用主类"""
    
    def __init__(self) -> None:
        self.bot: Bot

    async def startup(self) -> None:
        """应用启动"""
        logger.info("ChatBot应用正在启动...")
        self.bot = await Bot.get_instance()
        await self.bot.preload()
        await self.bot.check_protocol()
        await self.bot.login()
        await self.bot.keeplive()
        logger.info("ChatBot应用启动完成")

    async def shutdown(self) -> None:
        """应用关闭"""
        logger.info("ChatBot应用正在关闭...")
        await self.bot.destroy()
        await close_db_connection()
        logger.info("ChatBot应用已关闭")


    async def run(self) -> None:
        """运行应用"""
        try:
            await self.startup()
            await self.bot.run()
        finally:
            await self.shutdown()


async def main() -> None:
    """主函数"""
    exc = Exc()
    loop = asyncio.get_running_loop()
    exc.install_exception_hook(loop)
    app = ChatBotApplication()
    await app.run()

if __name__ == "__main__":
    asyncio.run(main())