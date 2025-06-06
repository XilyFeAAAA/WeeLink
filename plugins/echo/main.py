from src.event import (TextMessage, VoiceMessage, ImageMessage, VideoMessage, UploadMessage,
                       FileMessage, PatMessage, LinkMessage, QuoteMessage, ForwardMessage)
from src.schema import (AddMsgType, TextForward, ImageForward, VoiceForward, 
                        LinkForward, VideoForward, QuoteForward)
from src.bot import Bot
from src.plugin import PluginBase
from src.utils import logger


class Echo(PluginBase):
    
    __description__ = "消息提示"
    __author__ = "xilyfe"
    __version__ = "1.0.0"


    @PluginBase.on_text()
    async def echo_message(self, bot: Bot, msg: TextMessage):
        logger.info(f"接受到{msg.from_wxid}文字消息,   内容为{msg.text}")
    
    
    @PluginBase.on_voice()
    async def echo_voice(self, bot: Bot, msg: VoiceMessage):
        path = await msg.download()
        logger.info(f"接受到{msg.from_wxid}语音消息,文件位置:{path}")
    
    
    @PluginBase.on_image()
    async def echo_image(self, bot: Bot, msg: ImageMessage):
        path = await msg.download()
        logger.info(f"接受到{msg.from_wxid}图片消息,文件位置:{path}")
    
    
    @PluginBase.on_video()
    async def echo_video(self, bot: Bot, msg: VideoMessage):
        path = await msg.download()
        logger.info(f"接受到{msg.from_wxid}视频消息,文件位置:{path}")
    
    
    @PluginBase.on_file()
    async def echo_file(self, bot: Bot, msg: FileMessage):
        path = await msg.download()
        logger.info(f"接受到{msg.from_wxid}文件消息,文件位置:{path}")
    
    
    @PluginBase.on_upload()
    async def echo_upload(self, bot: Bot, msg: UploadMessage):
        logger.info(f"接受到{msg.from_wxid}正在上传文件,标题:{msg.upload_title},大小:{msg.upload_totallen},扩展名:{msg.upload_ext}")
    
    
    @PluginBase.on_link()
    async def echo_link(self, bot: Bot, msg: LinkMessage):
        logger.info(f"接受到{msg.from_wxid}链接消息,标题:{msg.link_title},描述:{msg.link_desc},来自:{msg.link_displayname}")
    
    
    @PluginBase.on_pat()
    async def echo_pat(self, bot: Bot, msg: PatMessage):
        logger.info(f"接受到{msg.from_wxid}拍一拍消息")
    
    
    @PluginBase.on_quote()
    async def echo_quote(self, bot: Bot, msg: QuoteMessage):
        logger.info(f"接收到{msg.from_wxid}引用消息,引用内容:{msg.quote_content}")
        
        if hasattr(msg, 'quote_data') and msg.quote_data:
            if msg.quote_type == AddMsgType.TEXT:
                logger.info(f"引用的是文本消息,内容为:{msg.quote_data.text}")
            elif msg.quote_type == AddMsgType.IMAGE:
                path = await msg.quote_data.download()
                logger.info(f"引用的是图片消息,文件位置:{path}")
    
    
    @PluginBase.on_forward()
    async def echo_forward(self, bot: Bot, msg: ForwardMessage):
        logger.info(f"接收到{msg.from_wxid}转发消息,标题:{msg.forward_title},描述:\n{msg.forward_desc}")
        for forward in msg.forwards:
            if isinstance(forward, TextForward):
                logger.info(f"转发的文本消息,来源:{forward.sourcename},时间:{forward.sourcetime},内容:{forward.datadesc}")
            elif isinstance(forward, ImageForward):
                logger.info(f"转发的图片消息,来源:{forward.sourcename},时间:{forward.sourcetime},cdnurl:{forward.cdndataurl[:10]}...")
            elif isinstance(forward, VideoForward):
                logger.info(f"转发的视频消息,来源:{forward.sourcename},时间:{forward.sourcetime},cdnurl:{forward.cdndataurl[:10]}...")
            elif isinstance(forward, VoiceForward):
                logger.info(f"转发的语音消息,来源:{forward.sourcename},时间:{forward.sourcetime},内容:{forward.datadesc}")
            elif isinstance(forward, LinkForward):
                logger.info(f"转发的链接消息,来源:{forward.sourcename},时间:{forward.sourcetime},来自:{forward.sourcedisplayname}")
            elif isinstance(forward, QuoteForward):
                logger.info(f"转发的引用消息,来源:{forward.sourcename},时间:{forward.sourcetime},引用内容:{forward.refermsgitem}")
    
    
    # @PluginBase.on_revoke()
    # async def echo_revoke(self, bot: Bot, msg: RevokeMessage):
    #     logger.info(f"接受到{msg.from_wxid}撤回消息")
    
    