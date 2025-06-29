# local library
from .base import Middleware
from .metadata import MiddlewareMetaData
from weelink.core.utils import logger, Context
from weelink.core.internal.config import conf


middlewares: dict[str, MiddlewareMetaData] = {}


def registry_middleware(
    name: str,
    desc: str
) -> callable: 
    def decorator(cls: type[Middleware]) -> None:
        metadata = MiddlewareMetaData(
            name=name,
            desc=desc,
            cls=cls,
            obj=cls()
        )
        middlewares[metadata.name] = metadata
        return cls
    return decorator


class MiddlewareManager:
    """中间件管理器 - 负责中间件的注册、执行和生命周期管理"""
    
    def __init__(self) -> None:
        
        from .sources import mds
        self.active_mw_mds = [
            md for name, md in middlewares.items() if name not in conf["inactive_middlewares"]
        ]
    
    
    async def process(self, event: "MessageEvent") -> any:
        """处理事件，依次通过所有启用的中间件"""
        try:
            # 创建中间件执行链
            context = Context()
            return await self._create_middleware_chain(event, context)           
        except Exception as e:
            logger.error(f"中间件链执行错误: {e}")
    
    
    async def _create_middleware_chain(self, 
            event: "MessageEvent", context: Context, index: int = 0
    ) -> any:
        """递归创建中间件执行链"""
        # 如果已经处理完所有中间件，返回None
        
        active_middlewares = [md.obj for md in self.active_mw_mds]
        
        if index >= len(active_middlewares):
            return event
        
        middleware = active_middlewares[index]
        
        async def next_middleware():
            return await self._create_middleware_chain(event, context, index + 1)
        
        return await self._execute_middleware(middleware, event, context, next_middleware)
    
    
    async def _execute_middleware(
        self, 
        middleware: Middleware, 
        event: "MessageEvent", 
        context: Context,
        next_middleware: callable
    ) -> any:
        """执行单个中间件"""
        try:
            # 前置处理钩子
            await middleware.before_process(event, context)
            
            # 执行中间件主要逻辑
            result = await middleware.process(event, context, next_middleware)
            
            # 后置处理钩子
            await middleware.after_process(event, context, result)
            
            return result
        except Exception as e:
            # 调用错误处理钩子
            handled = await middleware.on_error(event, context, e)
            if handled:
                return logger.debug(f"由中间件 {middleware.name} 处理的错误 ")
            else:
                raise