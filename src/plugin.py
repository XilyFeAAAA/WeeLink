from src.schema import EventType
import abc


class PluginBase(abc.ABC):
    """
    Base class for all plugins to interact with chatbox
    """
    
    # MetaData
    __description__: str = ""
    __author__: str = ""
    __version__: str = "1.0.0"
    __enabled__: bool = True
    
    def __init__(self) -> None:
        super().__init__()
        self.matchers: dict[str, any] = {}
        
    async def async_init(self, bot: "Bot"):
        """
        初始化插件的异步操作
        """
        return

    async def async_cleanup(self, bot: "Bot"):
        """
        清理插件的异步操作
        """
        return


    # AddMsg 装饰器
        
    @staticmethod
    def on_text(**kwargs):
        kwargs.setdefault("event", EventType.TEXT)
        def decorator(func):
            if not hasattr(func, '_event_handlers'):
                func._event_handlers = []
                
            func._event_handlers.append(kwargs)
            return func
        return decorator
    
    
    @staticmethod
    def on_voice(**kwargs):
        kwargs.setdefault("event", EventType.VOICE)
        def decorator(func):
            if not hasattr(func, '_event_handlers'):
                func._event_handlers = []
                
            func._event_handlers.append(kwargs)
            return func
        return decorator
    
    
    @staticmethod
    def on_image(**kwargs):
        kwargs.setdefault("event", EventType.IMAGE)
        def decorator(func):
            if not hasattr(func, '_event_handlers'):
                func._event_handlers = []
                
            func._event_handlers.append(kwargs)
            return func
        return decorator
    
    
    @staticmethod
    def on_video(**kwargs):
        kwargs.setdefault("event", EventType.VIDEO)
        def decorator(func):
            if not hasattr(func, '_event_handlers'):
                func._event_handlers = []
                
            func._event_handlers.append(kwargs)
            return func
        return decorator
    
    
    @staticmethod
    def on_pat(**kwargs):
        kwargs.setdefault("event", EventType.PAT)
        def decorator(func):
            if not hasattr(func, '_event_handlers'):
                func._event_handlers = []
                
            func._event_handlers.append(kwargs)
            return func
        return decorator
    
    @staticmethod
    def on_announcement(**kwargs):
        kwargs.setdefault("event", EventType.ANNOUNCE)
        def decorator(func):
            if not hasattr(func, '_event_handlers'):
                func._event_handlers = []
                
            func._event_handlers.append(kwargs)
            return func
        return decorator
    
    @staticmethod
    def on_todo(**kwargs):
        kwargs.setdefault("event", EventType.TODO)
        def decorator(func):
            if not hasattr(func, '_event_handlers'):
                func._event_handlers = []
                
            func._event_handlers.append(kwargs)
            return func
        return decorator
    
    
    @staticmethod
    def on_forward(**kwargs):
        kwargs.setdefault("event", EventType.FORWARD)
        def decorator(func):
            if not hasattr(func, '_event_handlers'):
                func._event_handlers = []
                
            func._event_handlers.append(kwargs)
            return func
        return decorator
    
    
    @staticmethod
    def on_startswith(
        text: str,
        rules: list["Rule"] = [],
        ignorecase: bool = False,
        **kwargs
    ):
        kwargs.setdefault("event", EventType.TEXT)
        def decorator(func):
            from src.matcher.rule import startswith
            if not hasattr(func, '_event_handlers'):
                func._event_handlers = []
            
            kwargs["rules"] = [startswith(text, ignorecase)] + rules
            func._event_handlers.append(kwargs)
            return func
        return decorator
    
    @staticmethod
    def on_endswith(
        text: str,
        rules: list["Rule"] = [],
        ignorecase: bool = False,
        **kwargs
    ):
        kwargs.setdefault("event", EventType.TEXT)
        def decorator(func):
            from src.matcher.rule import endswith
            if not hasattr(func, '_event_handlers'):
                func._event_handlers = []
            
            kwargs["rules"] = [endswith(text, ignorecase)] + rules
            func._event_handlers.append(kwargs)
            return func
        return decorator
    
    @staticmethod
    def on_fullmatch(
        text: str,
        rules: list["Rule"] = [],
        ignorecase: bool = False,
        **kwargs
    ):
        kwargs.setdefault("event", EventType.TEXT)
        def decorator(func):
            from src.matcher.rule import fullmatch
            if not hasattr(func, '_event_handlers'):
                func._event_handlers = []
            
            kwargs["rules"] = [fullmatch(text, ignorecase)] + rules
            func._event_handlers.append(kwargs)
            return func
        return decorator
    
    @staticmethod
    def on_keyword(
        keywords: set[str],
        rules: list["Rule"] = [],
        **kwargs
    ):
        kwargs.setdefault("event", EventType.TEXT)
        def decorator(func):
            from src.matcher.rule import keyword
            if not hasattr(func, '_event_handlers'):
                func._event_handlers = []
       
            kwargs["rules"] = [keyword(keywords)] + rules
            func._event_handlers.append(kwargs)
            return func
        return decorator
    
    
    @staticmethod
    def on_regex(
        patterns: list[str],
        rules: list["Rule"] = [],
        flags: int = 0,
        **kwargs
    ):
        kwargs.setdefault("event", EventType.TEXT)
        def decorator(func):
            from src.matcher.rule import regex
            if not hasattr(func, '_event_handlers'):
                func._event_handlers = []
            
            kwargs["rules"] = [regex(patterns, flags)] + rules
            func._event_handlers.append(kwargs)
            return func
        return decorator
    
    
    # XML 装饰器
    
    @staticmethod
    def on_file(**kwargs):
        kwargs.setdefault("event", EventType.FILE)
        def decorator(func):
            if not hasattr(func, '_event_handlers'):
                func._event_handlers = []
                
            func._event_handlers.append(kwargs)
            return func
        return decorator
    
    
    @staticmethod
    def on_upload(**kwargs):
        kwargs.setdefault("event", EventType.UPLOAD)
        def decorator(func):
            if not hasattr(func, '_event_handlers'):
                func._event_handlers = []
                
            func._event_handlers.append(kwargs)
            return func
        return decorator
    
    @staticmethod
    def on_quote(**kwargs):
        kwargs.setdefault("event", EventType.QUOTE)
        def decorator(func):
            if not hasattr(func, '_event_handlers'):
                func._event_handlers = []
                
            func._event_handlers.append(kwargs)
            return func
        return decorator
    
    @staticmethod
    def on_link(**kwargs):
        kwargs.setdefault("event", EventType.LINK)
        def decorator(func):
            if not hasattr(func, '_event_handlers'):
                func._event_handlers = []
                
            func._event_handlers.append(kwargs)
            return func
        return decorator
    
    # ModContacts 装饰器
    
    @staticmethod
    def on_chatroom_decrease(**kwargs):
        kwargs.setdefault("event", EventType.CHATROOM_DECREASE)
        def decorator(func):
            if not hasattr(func, '_event_handlers'):
                func._event_handlers = []

            func._event_handlers.append(kwargs)
            return func
        return decorator
    
    
    @staticmethod
    def on_chatroom_increase(**kwargs):
        kwargs.setdefault("event", EventType.CHATROOM_INCREASE)
        def decorator(func):
            if not hasattr(func, '_event_handlers'):
                func._event_handlers = []

            func._event_handlers.append(kwargs)
            return func
        return decorator
    
    
    def register_matchers(self):
        """注册所有用on装饰器装饰的方法到matcher"""
        from src.matcher.matcher import Matcher
        
        for func_name in dir(self.__class__):
            func = getattr(self.__class__, func_name)
            if callable(func) and hasattr(func, "_event_handlers"):
                # 获取实例方法
                bound_func = getattr(self, func_name)
                bound_func.matchers = {}
                for kwargs in func._event_handlers:
                    bound_func.matchers.set Matcher.new(handler=bound_func, **kwargs)
    
    def destroy_matchers(self):
        """卸载注册的matcher"""