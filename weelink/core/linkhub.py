# standard library
import sys
import asyncio

# local library
from weelink.core.plugin import PluginManager
from weelink.core.adapter import AdapterManager
from weelink.core.utils import logger, print_exc
from weelink.core.middleware import MiddlewareManager
from weelink.core.flow import get_broker, EventType
from weelink.core.on import HandleRegistry


class Linkhub:

    def __init__(self) -> None:
        self.task = None
        self.broker = get_broker()
        self.plugin = PluginManager()
        self.adapter = AdapterManager()
        self.middleware_manager = MiddlewareManager()


    async def preload(self) -> None:
        """Linkhub预加载"""
        try:
            self.broker.set_middleware_manager(self.middleware_manager)
            
            from weelink.core.internal.db import mongodb
            from weelink.core.utils import redis, schedule       
            schedule.start()
            await redis.connect()
            await mongodb.connect()
            
            await self.plugin.run()
            logger.info("LinkHub 初始化成功")
        except Exception as e:
            logger.critical(f"LinkHub 初始化失败: {str(e)}")
            sys.exit()


    async def start(self) -> None:
        """开始Weelink的事件循环队列"""
        for handler in HandleRegistry.get_handlers_from_type(EventType.STARTUP):
            try:
                await handler.callback()
            except Exception as e:
                logger.critical(f"插件{str(handler.module)}的STARTUP回调失败: {str(e)}")
        try:
            await self.adapter.initialize()
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print_exc(type(e), e, e.__traceback__)
        
        self.lifecycle = asyncio.Event()
        await self.lifecycle.wait()


    async def stop(self) -> None:
        """结束Weelink的事件循环队列"""
        for handler in HandleRegistry.get_handlers_from_type(EventType.STARTUP):
            try:
                await handler.callback()
            except Exception as e:
                logger.critical(f"插件{str(handler.module)}的 SHUTDOWN 回调失败: {str(e)}")
        try:
            if self.task is not None:
                self.task.cancel()
            
            await self.broker.wait_for_completion()
            
            from weelink.core.internal.db import mongodb
            from weelink.core.utils import redis, schedule
            schedule.stop()
            mongodb.close()
            await redis.close()
            await self.plugin.terminate()
            await self.adapter.terminate()
            self.lifecycle.set()
        except Exception as e:
            logger.critical(f"退出 Linkhub 异常，数据可能保存失败: {str(e)}")


    @staticmethod
    def on_startup(priority: int) -> callable:
    
        def decorator(func: callable) -> None:
            if not asyncio.iscoroutinefunction(func):
                return logger.warning(f"同步函数 {func.__name__} 无法绑定 on_startup 事件")
            broker.subscribe(
                event_type=EventType.STARTUP,
                priority=priority,
                callback=func
            )
        return decorator
    
    
    @staticmethod
    async def on_shutdown(priority: int) -> callable:
            
        def decorator(func: callable) -> None:
            if not asyncio.iscoroutinefunction(func):
                return logger.warning(f"同步函数 {func.__name__} 无法绑定 on_shutdown 事件")
            broker.subscribe(
                event_type=EventType.STARTUP,
                priority=priority,
                callback=func
            )
        return decorator