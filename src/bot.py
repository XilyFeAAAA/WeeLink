from src.mixin import (
    MessageMixIn, LoginMixIn, ProtocolMixIn, 
    UserMixIn, ChatroomMixIn, FriendMixIn, 
    ToolMixIn, PluginMixin, ScheduleMixin
)
from src.utils import logger, Whitelist, Redis, safe_create_task
from src.status import StatusManager
from src.config import conf
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
        super().__init__()
        self.whitelist = Whitelist()
        self.redis = Redis()
        self.status = StatusManager()
    
    
    async def preload(self) -> None:
        """预加载机器人配置和插件"""
        self.run_schedule()
        self.load_whitelist()
        self.use_queue()
        await self.redis.run()
        await self.status.load()
        await self.load_plugin_from_dictionary()
        
        
    @classmethod
    async def get_instance(cls) -> 'Bot':
        """获取Bot单例实例"""
        if cls._instance is None:
            async with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance


    def load_whitelist(self) -> None:
        """加载白名单配置"""
        whitelist_config = conf().get("WHITELIST", {})
        self.whitelist.enable() if whitelist_config.get("enable") else self.whitelist.disable()
        
        for user in whitelist_config.get("users", []):
            self.whitelist.add_user(user)
        
        for group in whitelist_config.get("chatrooms", []):
            self.whitelist.add_chatroom(group)
               
               
    def use_queue(self) -> None:
        """设置消息队列"""
        try:
            enable = conf().get("MESSAGE_QUEUE",{}).get("enable", False)
            interval = conf().get("MESSAGE_QUEUE",{}).get("interval", 1.0)
            if enable:
                from src.event import MessageQueue
                MessageQueue.get_instance(interval).start()
                logger.info(f"消息队列已启动，全局发送间隔 {interval} 秒")
            else:
                logger.info("消息队列已禁用，消息将立即发送")
        except Exception as e:
            logger.warning(f"初始化消息队列失败: {e}")
            
            
    async def keeplive(self) -> None:
        """保持连接活跃"""
        await self.start_auto_heartbeat()
    
    
    async def destroy(self) -> None:
        """销毁Bot实例，清理资源"""
        from src.event import MessageQueue
        self.stop_schedule()
        await self.redis.close()
        try:
            MessageQueue.get_instance().stop()
            logger.info("消息队列已关闭")
        except Exception as e:
            logger.warning(f"关闭消息队列时出错: {e}")
            
        await self.status.save()
        
        
    async def run(self):
        """
        处理消息数据
        AddMsg
        ModContact 好友消息、群信息变更
        DelContact (自己)删除好友，(自己)退出群聊
        """
        
        from src.matcher import Matcher
        
        failure_count = 0
        max_failures = 3
        async for data in self.message_generator():
            if data is None:
                failure_count += 1
                if failure_count > max_failures:
                    return logger.error("接收消息失败次数过多，退出消息处理循环")
            failure_count = 0        
            if isinstance(data, dict):
                # logger.debug(data)
                for msg in (data.get("AddMsgs") or []):
                    safe_create_task(Matcher.handle_addmsg(msg))
                for msg in ( data.get("ModContacts") or []):
                    logger.debug("遇到ModContacts")
                    safe_create_task(Matcher.handle_modcontact(msg))
            elif isinstance(data, str):
                if "已退出登录" in data or "会话已过期" in data:
                    return logger.warning(f"接收到退出消息: {data}")
                    