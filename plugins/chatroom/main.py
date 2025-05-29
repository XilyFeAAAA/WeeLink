from src.message import ChatroomModify
from src.bot import Bot
from src.plugin import PluginBase


class GroupDetect(PluginBase):
    
    __description__ = "群聊变动提示"
    __author__ = "xilyfe"
    __version__ = "1.0.0"


    @PluginBase.on_chatroom_decrease()
    async def decrease_notice(self, bot: Bot, msg: ChatroomModify):
        """退群提示"""
        await bot.send_text(
            msg.chatroom.chatroom_id,
            f"👋 {', '.join([m.name for m in msg.decreased_members])} 已退出群聊"
        )
        
    @PluginBase.on_chatroom_increase()
    async def increase_notice(self, bot: Bot, msg: ChatroomModify):
        """入群提示"""
        await bot.send_text(
            msg.chatroom.chatroom_id,
            f"🎉 欢迎 {', '.join([m.name for m in msg.increased_members])} 加入群聊"
        )
    