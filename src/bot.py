from typing import Optional, TYPE_CHECKING
from src.mixin import (
    MessageMixIn, LoginMixIn, StatusMixIn, 
    UserMixIn, ChatroomMixIn, FriendMixIn, 
    ToolMixIn, PluginMixin, ScheduleMixin,
    ProtocolMixIn
)
from src.utils import logger, Whitelist, Redis
from src.config import conf

if TYPE_CHECKING:
    pass


class Bot(
    ScheduleMixin, MessageMixIn, LoginMixIn, 
    UserMixIn, ChatroomMixIn, FriendMixIn, 
    ToolMixIn, PluginMixin, ProtocolMixIn,
    StatusMixIn
):
    """机器人主类，集成所有功能模块"""
    
    _instance: Optional['Bot'] = None

    def __init__(self) -> None:
        super().__init__()
        self.whitelist = Whitelist()
        self.redis = Redis()
    
    
    async def preload(self) -> None:
        """预加载机器人配置和插件"""
        self.run_schedule()
        self.load_whitelist()
        self.use_queue()
        await self.redis.run()
        await self.load_status()
        await self.load_plugin_from_dictionary()
        
        
    @classmethod
    def get_instance(cls) -> 'Bot':
        """获取Bot单例实例"""
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
                from src.message import MessageQueue
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
        from src.message import MessageQueue
        self.is_logged = False
        self.stop_schedule()
        await self.redis.close()
        try:
            MessageQueue.get_instance().stop()
            logger.info("消息队列已关闭")
        except Exception as e:
            logger.warning(f"关闭消息队列时出错: {e}")
            
        self.save_status()