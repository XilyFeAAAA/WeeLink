# standard library
import asyncio
from typing import TYPE_CHECKING

# local library
from .executor import execute
from weelink.core.utils import logger
from weelink.core.middleware import MiddlewareManager
from weelink.core.on.registry import HandleRegistry

if TYPE_CHECKING:
    from weelink.core.message import MessageEvent


class MessageBroker:
    
    def __init__(self) -> None:
        self._background_tasks = set()
        self.middleware_manager = None
    
    
    async def publish(self, event: "MessageEvent") -> None:    
        """发布事件，立即返回，实际处理在后台进行"""
        task = asyncio.create_task(self._process_event(event))
        task.add_done_callback(self._background_tasks.discard)
        self._background_tasks.add(task)
    
    
    async def _process_event(self, event: "MessageEvent") -> None:
        """实际的事件处理逻辑"""
        try:
            processed_event = await self.middleware_manager.process(event)
            if processed_event is None:
                logger.debug(f"事件 {event.event_type} 被中间件过滤")
                return
            
            logger.debug(str(event))
            # 顺序执行处理器，遇到返回False则停止
            for handler in HandleRegistry.get_handlers_from_type(event.event_type):
                try:
                    should_continue = await execute(handler, processed_event)
                    if not should_continue:
                        return
                except Exception as e:
                    logger.error(f"消息订阅 {handler.id} 执行异常: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"消息处理失败: {str(e)}")
            
    
    async def wait_for_completion(self) -> None:
        """等待所有后台任务完成"""
        if self._background_tasks:
            await asyncio.gather(*self._background_tasks, return_exceptions=True)


    def set_middleware_manager(self, manager: MiddlewareManager) -> None:
        """配置中间件管理器"""
        self.middleware_manager = manager


_broker = None

def get_broker():
    global _broker
    if _broker is None:
        _broker = MessageBroker()
    return _broker
