# local library
from .rule import (
    keyword, regex, startswith, endswith, fullmatch, Rule
)
from weelink.core.flow import EventType
from weelink.core.on.registry import HandleRegistry



def on(
    event_type: EventType,
    priority: int = 1,
    temp: bool = False,
    block: bool = False,
    expire_time: int = None,
    rule: Rule = None
) -> callable:
    
    def decorator(func: callable) -> callable:
        HandleRegistry.register(
            priority=priority,
            temp=temp,
            block=block,
            expire_time=expire_time,
            callback=func,
            module=func.__module__,
            event_type=event_type,
            rule=Rule() & rule
        )
        return func
    
    return decorator
    


def on_text(**kwargs) -> callable:
    return on(
        event_type=EventType.TEXT,
        **kwargs
    )

def on_image(**kwargs) -> callable:
    return on(
        event_type=EventType.IMAGE,
        **kwargs
    )

def on_video(**kwargs) -> callable:
    return on(
        event_type=EventType.VIDEO,
        **kwargs
    )

def on_voice(**kwargs) -> callable:
    return on(
        event_type=EventType.VOICE,
        **kwargs
    )

def on_file(**kwargs) -> callable:
    return on(
        event_type=EventType.FILE,
        **kwargs
    )


def on_link(**kwargs) -> callable:
    return on(
        event_type=EventType.LINK,
        **kwargs
    )

def on_startup(**kwargs) -> callable:
    return on(
        event_type=EventType.STARTUP,
        **kwargs
    )

def on_shutdown(**kwargs) -> callable:
    return on(
        event_type=EventType.SHUTDOWN,
        **kwargs
    )

def on_emoji(**kwargs) -> callable:
    return on(
        event_type=EventType.EMOJI,
        **kwargs
    )

def on_upload(**kwargs) -> callable:
    return on(
        event_type=EventType.UPLOAD,
        **kwargs
    )

def on_quote(**kwargs) -> callable:
    return on(
        event_type=EventType.QUOTE,
        **kwargs
    )

def on_forward(**kwargs) -> callable:
    return on(
        event_type=EventType.FORWARD,
        **kwargs
    )

def on_pat(**kwargs) -> callable:
    return on(
        event_type=EventType.PAT,
        **kwargs
    )

def on_invite(**kwargs) -> callable:
    return on(
        event_type=EventType.INVITE,
        **kwargs
    )

def on_revoke(**kwargs) -> callable:
    return on(
        event_type=EventType.REVOKE,
        **kwargs
    )

def on_announce(**kwargs) -> callable:
    return on(
        event_type=EventType.ANNOUNCE,
        **kwargs
    )

def on_todo(**kwargs) -> callable:
    return on(
        event_type=EventType.TODO,
        **kwargs
    )

def on_friend_add(**kwargs) -> callable:
    return on(
        event_type=EventType.FRIEND_ADD,
        **kwargs
    )

def on_friend_del(**kwargs) -> callable:
    return on(
        event_type=EventType.FRIEND_DEL,
        **kwargs
    )

def on_friend_modify(**kwargs) -> callable:
    return on(
        event_type=EventType.FRIEND_MODIFY,
        **kwargs
    )

def on_chatroom_add(**kwargs) -> callable:
    return on(
        event_type=EventType.CHATROOM_ADD,
        **kwargs
    )

def on_chatroom_del(**kwargs) -> callable:
    return on(
        event_type=EventType.CHATROOM_DEL,
        **kwargs
    )

def on_chatroom_increase(**kwargs) -> callable:
    return on(
        event_type=EventType.CHATROOM_INCREASE,
        **kwargs
    )

def on_chatroom_decrease(**kwargs) -> callable:
    return on(
        event_type=EventType.CHATROOM_DECREASE,
        **kwargs
    )

def on_keyword(
    keywords: list[str], 
    rule: Rule = None,
    **kwargs
) -> callable:
    return on_text(
        rule=keyword(keywords) & rule,
        **kwargs
    )

def on_regex(
    pattern: str,
    flag: int,
    rule: Rule = None,
    **kwargs
) -> callable:
    return on_text(
        rule=regex(pattern, flag) & rule,
        **kwargs
    )

def on_startswith(
    prefix: str, 
    ignore_case: bool = False, 
    rule: Rule = None,
    **kwargs
) -> callable:
    return on_text(
        rule=startswith(prefix, ignore_case) & rule,
        **kwargs
    )

def on_endswith(
    suffix: str,
    ignore_case: bool = False, 
    rule: Rule = None,
    **kwargs
) -> callable:
    return on_text(
        rule=endswith(suffix, ignore_case) & rule,
        **kwargs
    )

def on_fullmatch(
    text: str,
    ignore_case: bool = False,
    rule: Rule = None,
    **kwargs
) -> callable:
    return on_text(
        rule=fullmatch(text, ignore_case) & rule,
        **kwargs
    )
