from src import config
from src.mixin import (
    MessageMixIn, LoginMixIn, ProtocolMixIn, 
    UserMixIn, ChatroomMixIn, FriendMixIn, 
    ToolMixIn, PluginMixin, ScheduleMixin
)
from src.utils import logger, redis, print_exc
from src.status import StatusManager
from src.db import db
from typing import Optional
import asyncio



class Bot(
    ScheduleMixin, MessageMixIn, ToolMixIn, 
    LoginMixIn , ChatroomMixIn, FriendMixIn, 
    UserMixIn, PluginMixin, ProtocolMixIn
):
    """机器人主类，集成所有功能模块"""
    
    _instance: Optional['Bot'] = None
    _lock = asyncio.Lock()

    def __init__(self) -> None:
        MessageMixIn.__init__(self)
        ScheduleMixin.__init__(self)
        PluginMixin.__init__(self)
        
        self.status = StatusManager()
        self.db = db
    
    
    async def preload(self) -> None:
        """预加载机器人配置和插件"""
        self.start_schedule()
        self.use_queue()
        await self.db.connect()
        await self.status.load()
        await self.start_plugin()
        
        
    @classmethod
    async def get_instance(cls) -> 'Bot':
        """获取Bot单例实例"""
        if cls._instance is None:
            async with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance
               
               
    def use_queue(self) -> None:
        """设置消息队列"""
        try:
            enable = config.MESSAGE_QUEUE.get("enable", False)
            interval = config.MESSAGE_QUEUE.get("interval", 1.0)
            if enable:
                from src.event import MessageQueue
                MessageQueue.get_instance(interval).start()
                logger.success(f"消息队列已启动，全局发送间隔 {interval} 秒")
            else:
                logger.success("消息队列已禁用，消息将立即发送")
        except Exception as e:
            logger.error(f"初始化消息队列失败: {e}")
            
            
    async def keeplive(self) -> None:
        """保持连接活跃"""
        await self.start_auto_heartbeat()
    
    
    async def destroy(self) -> None:
        """销毁Bot实例，清理资源"""
        from src.event import MessageQueue
        self.stop_schedule()
        await redis.close()
        await self.stop_plugin()
        try:
            MessageQueue.get_instance().stop()
            logger.success("消息队列已关闭")
        except Exception as e:
            logger.error(f"关闭消息队列时出错: {e}")
            
        await self.status.save()
        await self.db.close()
        
        
    async def run(self):
        """
        处理消息数据
        AddMsg
        ModContact 好友消息、群信息变更
        DelContact (自己)删除好友，(自己)退出群聊
        """
        
        from src.event import AddMessage, ModContact
        failure_count = 0
        max_failures = 3
        async for data in self.message_generator():
            if data is None:
                failure_count += 1
                if failure_count > max_failures:
                    return logger.error("接收消息失败次数过多，退出消息处理循环")
            failure_count = 0
            try:  
                if isinstance(data, dict):
                    for addmsg in (data.get("AddMsgs") or []):
                        await AddMessage.new(addmsg)
                    for modcontact in ( data.get("ModContacts") or []):
                        await ModContact.new(modcontact)
                elif isinstance(data, str):
                    if "已退出登录" in data or "会话已过期" in data:
                        return logger.warning(f"接收到退出消息: {data}")        
            except Exception as e:
                print_exc(type(e), e, e.__traceback__)

"""
1. 通过生成器得到 data
2. 从data中的addmsgs和modcontacts中得到json
3. 通过AddMessage.new生成消息对象
4. new对象会通过self.parse生成一个对应的子类，调用self.publish发布事件
"""