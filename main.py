import asyncio
from src.matcher import Matcher
from src.bot import Bot
from src.utils import logger, safe_create_task
from src.utils.exception import global_exception_handler, set_default_exception_handlers

class ChatBotApplication:
    """聊天机器人应用主类"""
    
    def __init__(self) -> None:
        self.bot = Bot.get_instance()
        self.is_running = False
        self.message_failure_count = 0
        self.max_failure_count = 3

    async def startup(self) -> None:
        """应用启动"""
        logger.info("ChatBot应用正在启动...")
        await self.bot.preload()
        await self.bot.check_protocol()
        await self.bot.login()
        await self.bot.keeplive()
        self.is_running = True
        logger.info("ChatBot应用启动完成")

    async def shutdown(self) -> None:
        """应用关闭"""
        logger.info("ChatBot应用正在关闭...")
        self.is_running = False
        await self.bot.destroy()
        logger.info("ChatBot应用已关闭")

    async def message_loop(self) -> None:
        """消息处理循环"""
        while self.is_running:
            try:
                status, data = await self.bot.sync_message()
                
                if status:
                    self.message_failure_count = 0
                    
                await self._process_message_data(data)
                
            except asyncio.CancelledError:
                logger.info("消息循环被取消")
                break
            except Exception as e:
                global_exception_handler(type(e), e, e.__traceback__)
                self.message_failure_count += 1
            
            if self.message_failure_count > self.max_failure_count:
                logger.warning(f"连续 {self.message_failure_count} 次失败，退出消息循环")
                break
                
            await asyncio.sleep(0.5)

    async def _process_message_data(self, data) -> None:
        """
        处理消息数据
        AddMsg
        ModContact 好友消息、群信息变更
        DelContact (自己)删除好友，(自己)退出群聊
        """
        if isinstance(data, dict):
            logger.debug(data)
            for msg in (data.get("AddMsgs") or []):
                safe_create_task(Matcher.handle_addmsg(msg))
            for msg in ( data.get("ModContacts") or []):
                logger.debug("遇到ModContacts")
                safe_create_task(Matcher.handle_modcontact(msg))
        elif isinstance(data, str):
            if "已退出登录" in data or "会话已过期" in data:
                logger.warning(f"接收到退出消息: {data}")
                self.message_failure_count += 1

    async def run(self) -> None:
        """运行应用"""
        try:
            await self.startup()
            await self.message_loop()
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