from src.event import TextMessage, QuoteMessage
from src.schema import AddMsgType
from src.matcher import from_friend, from_chatroom, to_me
from src.bot import Bot
from src.utils import download_image, logger
from src.plugin import PluginBase
from .client import GLMClient, DoubaoClient
import os
import aiofiles




class LLM(PluginBase):
    
    __description__ = "大模型助手"
    __author__ = "xilyfe"
    __version__ = "1.0.0"

    async def async_cleanup(self, bot: "Bot"):
        """清理函数"""
        await DoubaoClient.cleanup()

    
    @PluginBase.on_text(rules=[from_friend()])
    async def private(self, bot: Bot, msg: TextMessage):
        client = await GLMClient.get_instance(msg.from_wxid)
        try:
            reply = await client.generate_text(msg.text)
            if reply:
                await bot.send_text(msg.from_wxid, reply)
            else:
                await bot.send_text(msg.from_wxid, "返回结果为空，请检查系统日志")
        except Exception as e:
            await bot.send_text(msg.from_wxid, f"发生错误: {str(e)}")
            
    
    @PluginBase.on_fullmatch(text="重置聊天", rules=[from_friend()], priority=100, block=True)
    async def clear_msg(self, bot: Bot, msg: TextMessage):
        try:
            client = await GLMClient.get_instance(msg.from_wxid)
            client.clear_messages()
            await bot.send_text(msg.from_wxid, "记录重置成功")
        except Exception as e:
            await bot.send_text(msg.from_wxid, f"记录重置失败: {str(e)}")
            
            
    @PluginBase.on_text(rules=[from_chatroom(), to_me()])
    async def doubao_chat(self, bot: Bot, msg: TextMessage):
        client = await DoubaoClient.get_instance(msg.from_wxid)
        try:
            reply = await client.chat(msg.text)
            logger.debug(reply)
            if text := reply.get("text"):
                await bot.send_text(msg.from_wxid, text)
                logger.debug(f"已发送: {text}")
            if img_urls := reply.get("img_urls"):
                url = img_urls[0]
                print(url)
                base64 = await download_image(url)
                await bot.send_image(msg.from_wxid, base64)

        except Exception as e:
            await bot.send_text(msg.from_wxid, f"发生错误: {str(e)}")
    
    
    @PluginBase.on_quote(rules=[from_chatroom(), to_me()])
    async def echo_quote(self, bot: Bot, msg: QuoteMessage):
        logger.info(f"接收到{msg.from_wxid}引用消息,引用内容:{msg.quote_content}")
        if msg.quote_type != AddMsgType.IMAGE:
            return
        client = await DoubaoClient.get_instance(msg.from_wxid)
        path = await msg.quote_data.download()
        async with aiofiles.open(path, 'rb') as f:
            file_data = await f.read()
        attachment = await client.upload_file(ftype=2, fname=os.path.basename(path), fdata=file_data)
        logger.debug(f"图片上传豆包成功: {attachment}")
        reply = await client.chat(msg.quote_content, attachment)
        if text := reply.get("text"):
            await bot.send_text(msg.from_wxid, text)
            logger.debug(f"已发送: {text}")
        if img_urls := reply.get("img_urls"):
            url = img_urls[0]
            print(url)
            base64 = await download_image(url)
            await bot.send_image(msg.from_wxid, base64)