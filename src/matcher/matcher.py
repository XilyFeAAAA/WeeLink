from src.schema import AddMsgType, ModContactType, EventType
from src.bot import Bot
from .rule import Rule
from datetime import datetime
from collections import defaultdict
import heapq



class Matcher:
    
    subscribers: dict[EventType, list[tuple[int, "Matcher"]]] = defaultdict(list)
    
    def __init__(
        self,
        rules: list[Rule],
        handler: callable,
        priority: int,
        block: bool,
        temp: bool,
        addmsg_type: AddMsgType,
        modcontact_type: ModContactType,
        expire_time: datetime = None,
        extra_args: dict = None
    ):
        self.addmsg_type = addmsg_type
        self.modcontact_type = modcontact_type
        self.rules = rules
        self.handler = handler
        self.priority = priority
        self.block = block
        self.temp = temp
        self.expire_time = expire_time
        self.extra_args = extra_args or {}
    

    @classmethod
    def new(
        cls,
        event: EventType,
        handler: callable,
        addmsg_type: AddMsgType = AddMsgType.UNKNOWN,
        modcontact_type: ModContactType = ModContactType.UNKNOWN,
        rules: list[Rule] = [],
        priority: int = 1,
        block: bool = False,
        temp: bool = False,
        expire_time: datetime = None,
        extra_args: dict = None,
    ):
        matcher = cls(
            rules=rules, 
            handler=handler, 
            priority=priority, 
            block=block, 
            temp=temp, 
            addmsg_type=addmsg_type, 
            modcontact_type=modcontact_type,
            expire_time=expire_time, 
            extra_args=extra_args
        )
        Matcher.subscribe(event, priority, matcher)
        return matcher
    
    
    # def update_priority(self, priority: int):
    #     if priority == self.priority: return
    #     Matcher.remove_matcher(self)
    #     Matcher.add_matcher(priority, self)
    
    
    @classmethod
    def subscribe(cls, event: EventType, priority: int, matcher: "Matcher"):
        """发布订阅"""
        heapq.heappush(cls.subscribers[event], (-priority, matcher))
    
    
    @classmethod
    def unsubscribe(cls, event: EventType, matcher: "Matcher"):
        """取消订阅"""
        cls.subscribers[event] = [
            (p, m) for (p, m) in cls.subscribers[event] if m != matcher
        ]
        heapq.heapify(cls.subscribers[event])
    
    
    @classmethod
    async def publish(cls, event: EventType, data):
        for _, matcher in sorted(cls.subscribers[event]):
            if await check_and_run_matcher(matcher, data) and matcher.block:
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


async def check_and_run_matcher(matcher: Matcher, data) -> bool:
    bot = await Bot.get_instance()
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

