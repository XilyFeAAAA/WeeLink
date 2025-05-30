from src.model import AddMsgType, SystemMsgType, DataType, ModContactType
from src.event import Message, ModContact
from src.utils import logger
from src.bot import Bot
from .rule import Rule
from datetime import datetime



class Matcher:
    
    matchers: dict[int, list["Matcher"]] = {}
    
    def __init__(
        self,
        type: DataType,
        rules: list[Rule],
        handler: callable,
        priority: int,
        block: bool,
        temp: bool,
        addmsg_type: AddMsgType,
        modcontact_type: ModContactType,
        sys_type: SystemMsgType = None,
        expire_time: datetime = None,
        extra_args: dict = None
    ):
        self.type = type
        self.addmsg_type = addmsg_type
        self.modcontact_type = modcontact_type
        self.rules = rules
        self.handler = handler
        self.priority = priority
        self.block = block
        self.temp = temp
        self.sys_type = sys_type,
        self.expire_time = expire_time
        self.extra_args = extra_args or {}
    

    @classmethod
    def new(
        cls,
        handler: callable,
        type: DataType,
        addmsg_type: AddMsgType = AddMsgType.UNKNOWN,
        modcontact_type: ModContactType = ModContactType.UNKNOWN,
        rules: list[Rule] = [],
        priority: int = 1,
        block: bool = False,
        temp: bool = False,
        sys_type: SystemMsgType = None,
        expire_time: datetime = None,
        extra_args: dict = None,
    ):
        matcher = cls(
            type=type, 
            rules=rules, 
            handler=handler, 
            priority=priority, 
            block=block, 
            temp=temp, 
            addmsg_type=addmsg_type, 
            modcontact_type=modcontact_type,
            sys_type=sys_type, 
            expire_time=expire_time, 
            extra_args=extra_args
        )
        Matcher.add_matcher(priority, matcher)
        return matcher
    
    
    def update_priority(self, priority: int):
        if priority == self.priority: return
        Matcher.remove_matcher(self)
        Matcher.add_matcher(priority, self)
    
    
    @classmethod
    def add_matcher(cls, priority: int, matcher: "Matcher"):
        if priority not in cls.matchers:
            cls.matchers[priority] = [matcher]
        else:
            cls.matchers[priority].append(matcher)
    
    
    @staticmethod
    def remove_matcher(matcher: "Matcher"):
        if matcher.priority in Matcher.matchers:
            Matcher.matchers[matcher.priority].remove(matcher)
    
    
    @classmethod
    async def handle_addmsg(cls, data: dict):
        if not (addmsg := await Message.new(data)):
            return
        for priority in sorted(cls.matchers.keys(), reverse=True):
            for matcher in cls.matchers[priority]:
                if await check_and_run_matcher(matcher, addmsg) and matcher.block:
                    return 
    
    @classmethod
    async def handle_modcontact(cls, data: dict):
        logger.debug("handle_modcontact")
        if not (modcontact := await ModContact.new(data)):
            return
        logger.debug("已创建ModContact")
        for priority in sorted(cls.matchers.keys(), reverse=True):
            for matcher in cls.matchers[priority]:
                if await check_and_run_matcher(matcher, modcontact) and matcher.block:
                    return 
        
    def __repr__(self):
        return (
            f"<Matcher handler={self.handler.__name__} "
            f"addmsg_type={self.addmsg_type} "
            f"rules={[str(r) for r in self.rules]} "
            f"priority={self.priority} "
            f"block={self.block} "
            f"temp={self.temp} "
            f"expire_time={self.expire_time}>"
        )


async def check_and_run_matcher(matcher: Matcher, data: Message | ModContact) -> bool:
    bot = await Bot.get_instance()
    # 类型检查
    if data.type == DataType.ADDMSG:
        if data.msg_type != matcher.addmsg_type or (
            matcher.addmsg_type == AddMsgType.SYSTEMMSG and data.sys_type != matcher.sys_type):
            return False
    elif data.type == DataType.MODCONTACTS:
        if data.modcontact_type != matcher.modcontact_type:
            return False
    else:
        raise Exception(f"未定义的数据类型：{data.type}")
    
    # 过期检查
    if matcher.expire_time and datetime.now() > matcher.expire_time:
        Matcher.remove_matcher(matcher)
        return False
    # 规则检查
    for rule in matcher.rules:
        if not rule.check(data):
            return False
    # 运行 matcher
    await matcher.handler(bot, data, **matcher.extra_args)
    # 一次性检查
    if matcher.temp:
        Matcher.remove_matcher(matcher)
    return True

