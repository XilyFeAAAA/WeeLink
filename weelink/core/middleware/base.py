# standard library
import abc

# local library
from weelink.core.utils import logger, Context
from weelink.core.message import MessageEvent


class Middleware():
    """中间件基类"""
    
    def __init__(self) -> None:
        self.enabled = True
    
    
    @abc.abstractmethod
    async def process(self, event: MessageEvent, context: Context, next_middleware: callable) -> any:
        raise NotImplementedError
    
    
    async def before_process(self, event: MessageEvent, context: Context) -> None:
        pass
    
    
    async def after_process(self, event: MessageEvent, context: Context, result: any) -> None:
        pass
    
    
    async def on_error(self, event: MessageEvent, context: Context, err: Exception) -> bool:
        raise NotImplementedError
    
    
    def enable(self) -> None:
        """启用中间件"""
        self.enabled = True
        logger.info(f"中间件 {self.name} 已启用")
    
    
    def disable(self) -> None:
        """禁用中间件"""
        self.enabled = False
        logger.info(f"中间件 {self.name} 已停止")