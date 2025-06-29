# standard library
import time
import asyncio

# local library
from .adapter import Adapter
from .metadata import AdapterMetaData
from .bot import Bot, BotConfig
from weelink.core.utils import logger, print_exc
from weelink.core.internal.db import BotRepository


""" id - AdapterMetaData """
adapters: dict[str, AdapterMetaData] = {}


def registry_adapter(
    name: str,
    desc: str,
    platform: str,
    version: str
) -> type[Adapter]:
    def decorator(cls: type[Adapter]) -> None:
        metadata = AdapterMetaData(
            name=name,
            desc=desc,
            wechat_version=version,
            wechat_platform=platform,
            fields=cls.get_config_fields(),
            cls=cls
        )
        adapters[metadata.id] = metadata
        # 设置适配器类的metadata属性
        cls.metadata = metadata
        return cls
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
        adapter_id = bot_config.adapter_id
        
        match adapter_name:
            case "wechatpad855":
                from weelink.core.adapter.sources.wechatpad855 import wechat855_adapter
            case _:
                raise Exception(f"适配器 {adapter_name} 未设置文件路径，请在 Weelink/core/adapter/manager.py中配置")

        if not adapter_id in adapters:
            raise Exception(f"适配器 {adapter_id} 不存在")

        try:
            # 根据适配器元信息，构建Bot
            adapter_metadata = adapters[adapter_id]
            adapter_cls = adapter_metadata.cls
            bot = Bot(
                alias=bot_config.alias,
                desc=bot_config.desc,
                is_running=False,
                auto_start=bot_config.auto_start,
                create_time=int(time.time()),
                adapter_metadata=adapter_metadata, 
                adapter_obj=adapter_cls(bot_config.adapter_config), 
                adapter_config=bot_config.adapter_config
            )
            self.bots[bot.id] = bot
            if bot.auto_start:
                await self.start_bot(bot.id)
        except Exception as e:
            logger.critical(f"机器人 {bot_config.alias} 适配器{adapter_name} 启动失败: {str(e)}")
    
    
    async def run_and_monitor_bot(self, bot: Bot) -> None:
        """运行并监控bot状态"""
        try:
            await bot.adapter_obj.run()
        except Exception as e:
            logger.error(f"机器人 {bot.id} 适配器{bot.adapter_metadata.name} 运行出错: {str(e)}")
            # print_exc(type(e), e, e.__traceback__)
        finally:
            bot.is_running = False
            await self._on_bot_terminated(bot)
    
    
    async def _on_bot_terminated(self, bot: Bot) -> None:
        """Bot终止时的回调函数"""
        logger.warning(f"机器人 {bot.id} 适配器{bot.adapter_metadata.name} 已停止运行")
    
    
    async def start_bot(self, bot_id: str) -> None:
        """启动机器人"""
        if not bot_id in self.bots:
            return logger.warning(f"机器人 - {bot_id} 不存在")
        
        bot = self.bots[bot_id]
        if bot.is_running:
            return
        
        # 创建运行任务并监控状态
        task = asyncio.create_task(self.run_and_monitor_bot(bot))
        self.bot_tasks[bot.id] = task
        bot.is_running = True
        logger.info(f"机器人 {bot.id} 适配器 {bot.adapter_metadata.name} 启动成功")
    
    
    async def stop_bot(self, bot_id: str) -> None:
        """停止机器人"""
        # 判断bot_id是否存在
        if bot_id not in self.bots:
            return
        
        # 判断在不在运行
        bot = self.bots[bot_id]
        if not (bot.is_running and bot_id in self.bot_tasks):
            return
        
        # 取出bot的run_and_monitor_bot任务
        task = self.bot_tasks.pop(bot_id)
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
        
        try:
            await bot.adapter_obj.terminate()
            bot.is_running = False
        except Exception as e:
            logger.error(f"终止机器人{bot.id}时出错: {str(e)}")
    
    
    async def delete_bot(self, bot_id: str) -> None:
        """卸载指定的机器人"""
        if bot_id not in self.bots:
            logger.warning(f"机器人 - {bot_id} 不存在，删除失败")
        
        await self.stop_bot(bot_id)
        
        bot = self.bots.pop(bot_id)
        await BotRepository.delete_bot(bot)
        return logger.success(f"机器人- {bot.id} 已删除")
    
    
    async def terminate(self) -> None:
        """终止所有机器人"""
        bot_ids = list(self.bots.keys())
        for bot_id in bot_ids:
            await self.stop_bot(bot_id)
    
    
    async def save_all_bots(self) -> None:
        """保存全部bot信息，以便下次启动"""
        bots = self.bots.copy()
        for bot in bots.values():
            try:
                await BotRepository.update_bot(bot)
            except Exception as e:
                logger.error(
                    f"机器人 {bot.id} 保存失败，注意信息是否保存"
                )


    async def add_bot(self, bot_config: BotConfig) -> None:
        """添加Bot"""
        await BotRepository.add_bot(bot_config)
        await self.load_bot(bot_config)
        return {}


    def get_all_adapters(self) -> list[AdapterMetaData]:
        """返回全部适配器"""
        return list(adapters.values())
    
    
    def get_adapter(self, adapter_id: str) -> AdapterMetaData:
        """返回指定适配器"""
        return adapters.get(adapter_id)
    
    
    def get_bot(self, bot_id: str) -> Bot:
        """返回指定Bot"""
        return self.bots.get(bot_id)
    
    def get_all_bots(self) -> list[Bot]:
        """返回全部机器人"""
        return list(self.bots.values())
    
    
    def get_bot_status(self, bot_id: str) -> bool:
        """获取指定机器人的状态"""
        if bot_id in self.bots:
            return self.bots[bot_id].is_running
        return False