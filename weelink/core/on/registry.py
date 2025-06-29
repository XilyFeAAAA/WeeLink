# standard library
import heapq
from types import ModuleType
from collections import defaultdict

# local librarye
from weelink.core.flow.event import EventType
from weelink.core.flow.metadata import HandlerMetaData


class HandleRegistry:

    handlers: dict[EventType, list[HandlerMetaData]] = defaultdict(list)

    @classmethod
    def register(
        cls, 
        priority: int, 
        temp: bool,
        block: bool,
        expire_time: int,
        callback: callable,
        module: str,
        event_type: EventType,
        rule: "Rule"
    ) -> HandlerMetaData:
        heapq.heappush(cls.handlers[event_type], HandlerMetaData(
            priority=priority,
            temp=temp,
            block=block,
            expire_time=expire_time,
            callback=callback, 
            module=module,
            plugin=None,  # 在插件加载时候赋值 
            event_type=event_type,
            rule=rule
        ))


    @classmethod
    def unregister(cls, handler: HandlerMetaData) -> None:
        event_type = handler.event_type
        handlers = cls.handlers.get(event_type, [])            
        cls.handlers[event_type] = [h for h in handlers if h != handler]
        heapq.heapify(cls.handlers[event_type])


    @classmethod
    def get_handlers_from_type(cls, event_type: EventType) -> list[HandlerMetaData]:
        """根据事件类型返回订阅"""
        return cls.handlers.get(event_type, [])


    @classmethod
    def get_handlers_from_module(cls, module: str) -> list[HandlerMetaData]:
        """根据所在模块返回订阅"""
        res = []
        for handlers in cls.handlers.values():
            res.extend(
                [handler for handler in handlers if handler.module == module]
            )
        
        return res
    
    @classmethod
    def get_handlers_from_plugin(cls, plugin_md: "PluginMetaData") -> list[HandlerMetaData]:
        """根据所在插件返回订阅"""
        res = []
        for handlers in cls.handlers.values():
            res.extend(
                [handler for handler in handlers if handler.plugin == plugin_md]
            )
        
        return res


    @classmethod
    def get_handler_from_id(cls, module: ModuleType) -> HandlerMetaData:
        """根据所在模块返回订阅"""
        return next(
            (handler for handlerlist in cls.handlers.values() for handler in handlerlist if handler.module == module),
            None
        ) 