from src.event import TextMessage, VoiceMessage, ImageMessage
from src.bot import Bot
from src.plugin import PluginBase
from src.model import MessageSource
from src.utils import logger


class Echo(PluginBase):
    
    __description__ = "消息提示"
    __author__ = "xilyfe"
    __version__ = "1.0.0"


    @PluginBase.on_message()
    async def echo_message(self, bot: Bot, msg: TextMessage):
        if msg.source ==  MessageSource.FRIEND:
            source_ = '私聊' 
            from_ = msg.sender.name
            
        else:
            source_ = '群聊'
            from_ = msg.chatroom.name
            
        logger.info(f"接受到{source_}{msg.from_wxid}文字消息,来自{from_},内容为{msg.text}")
        
    
    @PluginBase.on_voice()
    async def echo_voice(self, bot: Bot, msg: ImageMessage):
        if msg.source ==  MessageSource.FRIEND:
            source_ = '私聊' 
            from_ = msg.sender.name
            
        else:
            source_ = '群聊'
            from_ = msg.chatroom.name
            
        logger.info(f"接受到{source_}{msg.from_wxid}语音消息,来自{from_},文件位置:{msg.path}")