from src.model import AddMsgType, SystemMsgType, DataType, ModContactType
import abc
import inspect


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


    # AddMsg 装饰器
        
    @staticmethod
    def on_message(**kwargs):
        kwargs.setdefault("type", DataType.ADDMSG)
        kwargs.setdefault("addmsg_type", AddMsgType.TEXT)
        def decorator(func):
            if not hasattr(func, '_event_handlers'):
                func._event_handlers = []
                
            func._event_handlers.append(kwargs)
            return func
        return decorator
    
    
    @staticmethod
    def on_voice(**kwargs):
        kwargs.setdefault("type", DataType.ADDMSG)
        kwargs.setdefault("addmsg_type", AddMsgType.VOICE)
        def decorator(func):
            if not hasattr(func, '_event_handlers'):
                func._event_handlers = []
                
            func._event_handlers.append(kwargs)
            return func
        return decorator
    
    
    @staticmethod
    def on_image(**kwargs):
        kwargs.setdefault("type", DataType.ADDMSG)
        kwargs.setdefault("addmsg_type", AddMsgType.IMAGE)
        def decorator(func):
            if not hasattr(func, '_event_handlers'):
                func._event_handlers = []
                
            func._event_handlers.append(kwargs)
            return func
        return decorator
    
    
    @staticmethod
    def on_video(**kwargs):
        kwargs.setdefault("type", DataType.ADDMSG)
        kwargs.setdefault("addmsg_type", AddMsgType.VIDEO)
        def decorator(func):
            if not hasattr(func, '_event_handlers'):
                func._event_handlers = []
                
            func._event_handlers.append(kwargs)
            return func
        return decorator
    
    
    @staticmethod
    def on_system(**kwargs):
        kwargs.setdefault("type", DataType.ADDMSG)
        kwargs.setdefault("addmsg_type", AddMsgType.SYSTEMMSG)
        def decorator(func):
            if not hasattr(func, '_event_handlers'):
                func._event_handlers = []
                
            func._event_handlers.append(kwargs)
            return func
        return decorator
    
    @staticmethod
    def on_pat(**kwargs):
        kwargs.setdefault("type", DataType.ADDMSG)
        kwargs.setdefault("addmsg_type", AddMsgType.SYSTEMMSG)
        kwargs.setdefault("sys_type", SystemMsgType.PAT)
        def decorator(func):
            if not hasattr(func, '_event_handlers'):
                func._event_handlers = []
                
            func._event_handlers.append(kwargs)
            return func
        return decorator
    
    @staticmethod
    def on_announcement(**kwargs):
        kwargs.setdefault("type", DataType.ADDMSG)
        kwargs.setdefault("addmsg_type", AddMsgType.SYSTEMMSG)
        kwargs.setdefault("sys_type", SystemMsgType.ANNOUNCEMENT)
        def decorator(func):
            if not hasattr(func, '_event_handlers'):
                func._event_handlers = []
                
            func._event_handlers.append(kwargs)
            return func
        return decorator
    
    @staticmethod
    def on_todo(**kwargs):
        kwargs.setdefault("type", DataType.ADDMSG)
        kwargs.setdefault("addmsg_type", AddMsgType.SYSTEMMSG)
        kwargs.setdefault("sys_type", SystemMsgType.TODO)
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
        kwargs.setdefault("type", DataType.ADDMSG)
        kwargs.setdefault("addmsg_type", AddMsgType.TEXT)
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
        kwargs.setdefault("type", DataType.ADDMSG)
        kwargs.setdefault("addmsg_type", AddMsgType.TEXT)
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
        kwargs.setdefault("type", DataType.ADDMSG)
        kwargs.setdefault("addmsg_type", AddMsgType.TEXT)
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
        kwargs.setdefault("type", DataType.ADDMSG)
        kwargs.setdefault("addmsg_type", AddMsgType.TEXT)
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
        kwargs.setdefault("type", DataType.ADDMSG)
        kwargs.setdefault("addmsg_type", AddMsgType.TEXT)
        def decorator(func):
            from src.matcher.rule import regex
            if not hasattr(func, '_event_handlers'):
                func._event_handlers = []
            
            kwargs["rules"] = [regex(patterns, flags)] + rules
            func._event_handlers.append(kwargs)
            return func
        return decorator
    
    
    # ModContacts 装饰器
    
    @staticmethod
    def on_chatroom_decrease(**kwargs):
        kwargs.setdefault("type", DataType.MODCONTACTS)
        kwargs.setdefault("modcontact_type", ModContactType.MEMBER_DECREASED)
        def decorator(func):
            if not hasattr(func, '_event_handlers'):
                func._event_handlers = []

            func._event_handlers.append(kwargs)
            return func
        return decorator
    
    
    @staticmethod
    def on_chatroom_increase(**kwargs):
        kwargs.setdefault("type", DataType.MODCONTACTS)
        kwargs.setdefault("modcontact_type", ModContactType.MEMBER_INCREASED)
        def decorator(func):
            if not hasattr(func, '_event_handlers'):
                func._event_handlers = []

            func._event_handlers.append(kwargs)
            return func
        return decorator
    
    
    def register_matchers(self):
        """
        注册所有用on装饰器装饰的方法到matcher系统
        """
        from src.matcher.matcher import Matcher
        for func_name, func in inspect.getmembers(self.__class__, predicate=inspect.isfunction):
            if hasattr(func, '_event_handlers'):
                for kwargs in func._event_handlers:
                    # 将实例方法绑定到matcher系统
                    bound_func = getattr(self, func_name)
                    func.matcher = Matcher.new(bound_func, **kwargs)