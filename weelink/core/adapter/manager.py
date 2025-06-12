# standard library
import time
import asyncio

# local library
from .adapter import Adapter
from .metadata import AdapterMetaData
from .bot import Bot, BotConfig
from weelink.core.utils import logger, print_exc
from weelink.core.internal.db import BotRepository


""" name - AdapterMetaData """
adapters: dict[str, AdapterMetaData] = {}


def registry_adapter(
    name: str,
    desc: str,
) -> type[Adapter]:
    def decorator(cls: type[Adapter]) -> None:
        metadata = AdapterMetaData(
            name=name,
            desc=desc,
            cls=cls
        )
        adapters[name] = metadata
    return decorator


class AdapterManager:
    
    def __init__(self) -> None:
        self.bots: dict[str, Bot] = {}
        self.bot_tasks: dict[str, asyncio.Task] = {}
    
    
    async def initialize(self) -> None:
        """初始化适配器"""
        for bot_doc in await BotRepository.get_all_bots():
            await self.load_bot(BotConfig(
                **bot_doc.model_dump(exclude=["id"])
            ))
    
    
    async def load_bot(self, bot_config: BotConfig) -> None:
        """为适配器创建机器人"""
        adapter_name = bot_config.adapter_name
        
        match adapter_name:
            case "wechatpad855":
                from weelink.core.adapter.sources.wechatpad855 import wechat855_adapter
            case _:
                raise Exception(f"适配器 {adapter_name} 未设置文件路径，请在 Weelink/core/adapter/manager.py中配置")

        if not adapter_name in adapters:
            raise Exception(f"适配器{adapter_name}不存在")

        try:
            # 根据适配器元信息，构建Bot
            adapter_metadata = adapters[adapter_name]
            adapter_cls = adapter_metadata.cls
            bot = Bot(
                alias=bot_config.alias,
                desc=bot_config.desc,
                create_time=int(time.time()),
                state=True,
                adapter_metadata=AdapterMetaData(
                    name=adapter_metadata.name,
                    desc=adapter_metadata.desc,
                    cls=adapter_cls
                ), 
                adapter_obj=adapter_cls(bot_config.adapter_config), 
                adapter_config=bot_config.adapter_config
            )
            self.bots[bot.id] = bot
            
            # 创建运行任务并监控状态
            task = asyncio.create_task(self.run_and_monitor_bot(bot))
            self.bot_tasks[bot.id] = task
            
            logger.info(f"机器人 {bot.id} 适配器 {bot.adapter_metadata.name} 启动成功")
        except Exception as e:
            logger.critical(f"机器人{bot_config.alias} 适配器{adapter_name} 启动失败: {str(e)}")
    
    
    async def run_and_monitor_bot(self, bot: Bot) -> None:
        """运行并监控bot状态"""
        try:
            await bot.adapter_obj.run()
        except Exception as e:
            logger.error(f"机器人{bot.id} 适配器{bot.adapter_metadata.name} 运行出错: {str(e)}")
            print_exc(type(e), e, e.__traceback__)
        finally:
            bot.state = False
            await self._on_bot_terminated(bot)
    
    
    async def _on_bot_terminated(self, bot: Bot) -> None:
        """Bot终止时的回调函数"""
        logger.warning(f"机器人{bot.id} 适配器{bot.adapter_metadata.name} 已停止运行")
        # 这里可以添加更多回调逻辑，比如通知管理员、尝试重启等
    
    
    async def unload_bot(self, bot_id: str) -> None:
        """卸载指定的机器人"""
        if bot_id not in self.bots:
            raise Exception(f"Bot-{bot_id}不存在")

        task = self.bot_tasks.pop(bot_id)
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
        
        bot = self.bots[bot_id]
        try:
            await bot.adapter_obj.terminate()
        except Exception as e:
            logger.error(f"终止机器人{bot.id}时出错: {str(e)}")
        
        del self.bots[bot_id]
        return logger.success(f"机器人{bot.id} 已卸载")
    
    
    async def terminate(self) -> None:
        """终止所有机器人"""
        bot_ids = list(self.bots.keys())
        for bot_id in bot_ids:
            await self.unload_bot(bot_id)
    
    
    async def save_all_bots(self) -> None:
        """保存全部bot信息，以便下次启动"""
        bots = self.bots.copy()
        for bot in bots.values():
            try:
                await BotRepository.update_bot(bot)
            except Exception as e:
                logger.error(
                    f"机器人{bot.id}保存失败，注意信息是否保存"
                )
            


    def get_all_adapters(self) -> list[AdapterMetaData]:
        """返回全部适配器"""
        return list(adapters.values())
    
    
    def get_all_bots(self) -> list[Bot]:
        """返回全部机器人"""
        return list(self.bots.values())
    
    
    def get_bot_status(self, bot_id: str) -> bool:
        """获取指定机器人的状态"""
        if bot_id in self.bots:
            return self.bots[bot_id].state
        return False