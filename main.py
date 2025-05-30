import asyncio
from src.bot import Bot
from src.utils import logger
from src.utils.exception import global_exception_handler, set_default_exception_handlers

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
    set_default_exception_handlers()
    
    app = ChatBotApplication()
    try:
        await app.run()
    except KeyboardInterrupt:
        logger.info("接收到键盘中断信号")
    except Exception as e:
        logger.critical("应用发生致命错误")
        global_exception_handler(type(e), e, e.__traceback__)


if __name__ == "__main__":
    logger.info("程序启动...")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("程序被用户中断")
    finally:
        logger.info("程序已退出")