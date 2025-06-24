# standard library
import json
import datetime
from pathlib import Path


# local library
from .base import Middleware
from weelink.core.message import MessageEvent
from weelink.core.utils import logger, DATA_DIR, Context


class MiddlewareManager:
    """中间件管理器 - 负责中间件的注册、执行和生命周期管理"""
    
    def __init__(self, config_file: Path = None):
        self._middlewares: list[Middleware] = []
        self._middleware_map: dict[str, Middleware] = {}
        self._global_context = Context()
        
        # 配置文件管理
        self._config_file = config_file or DATA_DIR / "middleware_config.json"
        self._config_data = self.import_config()
    
    
    def import_config(self) -> None:
        """加载配置项"""
        if self._config_file.exists():
            try:
                with open(self._config_file) as f:
                    return json.loads(f)
            except Exception as e:
                logger.error(f"中间件配置文件读取失败: {str(e)}")
        
        return {
            'enabled_middlewares': [],
            'last_updated': None
        }
    
    
    def save(self) -> None:
        """保存配置项"""

        try:
            self._config_data["last_updated"] = datetime.now().isoformate()
            self._config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self._config_file, "w", encoding='utf-8') as f:
                json.dump(self._config_data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            logger.error(f"中间件配置文件保存失败: {str(e)}")
    
    
    async def reset_config(self) -> None:
        """重置所有配置到默认状态"""
        self._config_data = {
            'enabled_middlewares': [],
            'last_updated': None
        }
        
        for middleware in self._middlewares:
            middleware.enable()
    
    
    def add_middleware(self, middleware: Middleware) -> None:
        """添加中间件到管理器"""
        if middleware.name in self._middleware_map:
            return logger.warning(f"中间件 {middleware.name} 已经存在")
        
        self._middlewares.append(middleware)
        self._middleware_map[middleware.name] = middleware
    
        # 配置文件中恢复上次状态
        enabled_mws = self._config_data["enabled_middlewares"]
        middleware.enabled = middleware in enabled_mws
            
        self._middlewares.sort(key=lambda x: (x.priority, self._middlewares.index(x)))
    
    
    def remove_middleware(self, name: str) -> None:
        """移除指定名称的中间件"""
        if name not in self._middleware_map:
            logger.warning(f"中间件 {name} 未找到")
        
        middleware = self._middleware_map.pop(name)
        self._middlewares.remove(middleware)
    
    
    def get_middleware(self, name: str) -> Middleware:
        """获取指定名称的中间件"""
        return self._middleware_map.get(name)
    
    
    def list_middlewares(self) -> list[dict[str, any]]:
        """列出所有中间件的基本信息"""
        return [
            {
                'name': mw.name,
                'priority': mw.priority,
                'enabled': mw.enabled,
                'class_name': mw.__class__.__name__
            }
            for mw in self._middlewares
        ]
    
    
    def enable_middleware(self, name: str) -> bool:
        """启用指定中间件"""
        middleware = self.get_middleware(name)
        if middleware:
            middleware.enable()
            self._config_data["enabled_middlewares"].append(middleware)
    
    
    def disable_middleware(self, name: str) -> bool:
        """禁用指定中间件"""
        middleware = self.get_middleware(name)
        if middleware:
            middleware.disable()
            self._config_data["enabled_middlewares"].remove(middleware)
    
    
    async def process(self, event: MessageEvent) -> any:
        """处理事件，依次通过所有启用的中间件"""
        try:
            # 创建中间件执行链
            context = Context()
            return await self._create_middleware_chain(event, context)           
        except Exception as e:
            logger.error(f"中间件链执行错误，请检查日志文件")
    
    
    async def _create_middleware_chain(self, 
            event: MessageEvent, context: Context, index: int = 0
    ) -> any:
        """递归创建中间件执行链"""
        enabled_middlewares = self._get_enabled_middlewares()
        
        # 如果已经处理完所有中间件，返回None
        if index >= len(enabled_middlewares):
            return event
        
        middleware = enabled_middlewares[index]
        
        async def next_middleware():
            return await self._create_middleware_chain(event, context, index + 1)
        
        return await self._execute_middleware(middleware, event, context, next_middleware)
    
    
    async def _execute_middleware(
        self, 
        middleware: Middleware, 
        event: MessageEvent, 
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
                return logger.debug(f"由中间件处理的错误 {middleware.name}")
            else:
                raise
    
    
    def _get_enabled_middlewares(self) -> list[Middleware]:
        """获取所有启用的中间件列表"""
        return [mw for mw in self._middlewares if mw.enabled]
