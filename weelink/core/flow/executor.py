# standard library
import datetime
import asyncio
from typing import TYPE_CHECKING

# local library
from .metadata import HandlerMetaData
# 避免循环导入
from weelink.core.on.registry import HandleRegistry

if TYPE_CHECKING:
    from weelink.core.message import MessageEvent



async def execute(handler: HandlerMetaData, event: "MessageEvent") -> bool:
    """执行处理器"""
    # 预检查
    if not await _pre_examine(handler, event):
        return
    
    # 执行处理器回调
    if asyncio.iscoroutinefunction(handler.callback):
        await handler.callback(event)
    else:
        handler.callback(event)
    
    return handler.block        
    
    
async def _pre_examine(handler: HandlerMetaData, event: "MessageEvent") -> bool:
    """过期检查"""
    if handler.expire_time and datetime.datetime.now() > handler.expire_time:
        HandleRegistry.unregister(handler=handler)
        return False
    
    """平台兼容性检查"""
    if handler.plugin is None:
        raise Exception("HandlerMetaData的plugin参数为空，请检查日志")
    
    if (accepted_adapters := handler.plugin.adapters) and event.adapter_cls not in accepted_adapters:
        return False
    
    """规则检查"""
    ctn = await handler.rule.check(event) \
        if asyncio.iscoroutinefunction(handler.rule.check) \
        else handler.rule.check(event)
    if not ctn:
        return False
    
    """一次性检查"""
    if handler.temp:
        HandleRegistry.unregister(handler=handler)
    
    return True