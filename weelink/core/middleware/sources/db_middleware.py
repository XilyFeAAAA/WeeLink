# standard library
import asyncio

# local library
from weelink.core.internal.db import MessageRepository
from weelink.core.utils import Context
from weelink.core.message import MessageEvent, AddMessage
from weelink.core.middleware.base import Middleware
from weelink.core.middleware.manager import registry_middleware


@registry_middleware(
    name="MsgCollectMiddleware",
    desc="收藏聊天记录中的AddMessage存储在Mongodb"
)
class DBMiddleware(Middleware):
    """中间件基类"""
        
    async def process(self, event: MessageEvent, context: Context, next_middleware: callable) -> any:
        """中间件处理"""
        component = event.component
        if isinstance(component, AddMessage):
            asyncio.create_task(MessageRepository.add_message(
                adapter_name=event.adapter_md.name,
                msg_id=component.msg_id,
                new_msg_id=component.new_msg_id,
                data=event.data
            ))
        
        return await next_middleware()    
    
    
    async def on_error(self, event: MessageEvent, context: Context, err: Exception) -> bool:
        """错误响应"""
        return False