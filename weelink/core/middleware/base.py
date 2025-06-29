# standard library
import abc

# local library
from weelink.core.utils import Context


class Middleware():
    """中间件基类"""
        
    
    @abc.abstractmethod
    async def process(self, event: "MessageEvent", context: Context, next_middleware: callable) -> any:
        raise NotImplementedError
    
    
    async def before_process(self, event: "MessageEvent", context: Context) -> None:
        pass
    
    
    async def after_process(self, event: "MessageEvent", context: Context, result: any) -> None:
        pass
    
    
    async def on_error(self, event: "MessageEvent", context: Context, err: Exception) -> bool:
        raise NotImplementedError
    