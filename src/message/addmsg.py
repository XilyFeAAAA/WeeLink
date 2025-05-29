from src.model import (
    AddMsgType, DataType, ChatroomMember, 
    Friend, MessageSource, XmlType, QuoteType,
    SystemMsgType, Chatroom)
from src.manager import cache
from src.utils import logger
from src.bot import Bot
from src.config import conf
from xml.etree import ElementTree
from PIL import Image, ImageFile
import filetype
import pysilk
import base64
import aiofiles
import io
import os
import re
import hashlib
import time
import math

bot = Bot.get_instance()

class Message:
    _type_registry: dict = {}

    def __init__(self,
                *, 
                data: dict,
                from_wxid: str,
                to_wxid: str, 
                msg_type: AddMsgType,
                content: str,
                create_time: int,
                msg_source: str,
                msg_id: int,
                new_msg_id: int,
                msg_seq: int,
                chatroom: Chatroom | None = None,
                sender: Friend | ChatroomMember | None = None,
                source: MessageSource = MessageSource.OTHER):
        # 原始数据
        self.data = data
        # 发送人wxid
        self.from_wxid = from_wxid
        # 接收人wxid
        self.to_wxid = to_wxid
        # 消息类型
        self.msg_type = msg_type
        # 消息内容
        self.content = content
        # 发送时间
        self.create_time = create_time
        # 消息来源字段
        self.msg_source = msg_source
        # 消息id
        self.msg_id = msg_id
        # 消息new_id
        self.new_msg_id = new_msg_id
        # 消息序列化
        self.msg_seq = msg_seq
        # 群聊对象
        self.chatroom = chatroom
        # 私聊对象
        self.sender = sender
        # 聊天类型
        self.source = source
        # 数据类型
        self.type = DataType.ADDMSG


    @classmethod
    def register_type(cls, msg_type):
        def decorator(subclass):
            cls._type_registry[msg_type] = subclass
            return subclass
        return decorator


    @classmethod
    async def new(cls, data) -> "Message":
        # 处理通用信息
        from_wxid = data.get("FromUserName", {}).get("string")
        to_wxid = data.get("ToUserName", {}).get("string")
        msg_type = data.get("MsgType")
        content = data.get("Content", {}).get("string")
        create_time = data.get("CreateTime")
        msg_source = data.get("MsgSource")
        msg_id = data.get("MsgId")
        new_msg_id = data.get("NewMsgId")
        msg_seq = data.get("MsgSeq")
        # 过滤过期信息
        if time.time() - create_time >= 60 * 5:
            return None
        # 过滤自己发的消息
        if data["FromUserName"]["string"] == bot.wxid: return
        # 白名单过滤
        # 群聊 or 私聊判断
        if from_wxid.endswith("@chatroom"):
            if not bot.whitelist.is_chatroom_allowed(from_wxid): return
            source = MessageSource.CHATROOM
            chatroom = await cache.chatroom.get(from_wxid)
        else:
            if not bot.whitelist.is_user_allowed(from_wxid): return
            source = MessageSource.FRIEND
            sender = await cache.friend.get(from_wxid)
        # 根据消息类型分发
        if (subclass := cls._type_registry.get(msg_type)) is not None:
            cls = subclass(
                data=data,
                from_wxid=from_wxid,
                to_wxid=to_wxid,
                msg_type=msg_type,
                content=content,
                create_time=create_time,
                msg_source=msg_source,
                msg_id=msg_id,
                new_msg_id=new_msg_id,
                msg_seq=msg_seq,
                chatroom=chatroom if source == MessageSource.CHATROOM else None,
                sender=sender if source == MessageSource.FRIEND else None,
                source=source
            )
        else:
            logger.warning(f"未识别的消息类型:{msg_type}")
            return None
        return await cls.parse()
        

# 文字消息
@Message.register_type(AddMsgType.TEXT)
class TextMessage(Message):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.text: str = ""
        self.ats: list[ChatroomMember] = []
        self.at_me: bool = False
        

    async def parse(self) -> "TextMessage":
        if self.source == MessageSource.CHATROOM:
            # 分割群聊消息发送人
            sender_wxid, self.content = self.content.split(':\n')
            # 去掉at信息，获得纯文本
            self.text = re.sub(r'@[^\u2005]*\u2005', '', self.content) if '\u2005' in self.content else self.content
            # 获取发送人信息
            if self.chatroom is None:
                logger.error("chatroom为null")
            self.sender = await cache.chatroom.get_member(sender_wxid, self.chatroom.chatroom_id)
            # 获取at信息
            self.ats = await self.get_ats()
            self.at_me = any(at.wxid == bot.wxid for at in self.ats)
        elif self.source == MessageSource.FRIEND:
            self.text = self.content
        
        return self

    async def get_ats(self) -> list[ChatroomMember]:
        """群内at,如果设置了群内昵称则会显示群内昵称displayName,否则为微信名nickName"""
        root = ElementTree.fromstring(self.msg_source)
        ats = root.find("atuserlist").text if root.find("atuserlist") is not None else ""
        ats = ats.lstrip(",")
        ats = ats.split(",") if ats else []
        return [await cache.chatroom.get_member(at, self.from_wxid) for at in ats]


    def __repr__(self):
        return f"<TextMessage sender={self.sender} text={self.text}>"


@Message.register_type(AddMsgType.APPMSG)
class XmlMessage(TextMessage):
   
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    async def parse(self) -> "XmlMessage":
        await super().parse()
        try:
            root = ElementTree.fromstring(self.content)
            type = int(root.find("appmsg").findtext("type"))
            if type == XmlType.QUOTE:
                await self.handle_quote()
            elif type == XmlType.FILE:
                logger.warning("未适配FILE类型XML")
                raise NotImplementedError()
            elif type == XmlType.SHARE_LINK:
                logger.warning("未适配SHARE_LINK类型XML")
                raise NotImplementedError()
            elif type == XmlType.UPLOAD:
                logger.warning("未适配UPLOAD类型XML")
                raise NotImplementedError()
            else:
                raise Exception(f"未识别的 XML 类型:{type}")
        except Exception as e:
            logger.error(f"解析xml消息失败: {e}")
            return  
        finally:
            return self
        
        
    async def handle_quote(self, appmsg: ElementTree.Element) -> None:
        """处理引用消息"""
        if refermsg := appmsg.find("type"):
            self.refer_type = refermsg.findtext("type")
            self.new_msg_id = refermsg.find("svrid").text
            self.to_wxid = refermsg.find("fromusr").text
            self.from_wxid = refermsg.find("chatusr").text
            self.nickname = refermsg.find("displayname").text
            self.msg_source = refermsg.find("msgsource").text
            self.createtime = refermsg.find("createtime").text
            self.content = refermsg.find("content").text
            
            # 处理文本引用
            if self.refer_type == QuoteType.TEXT:
                # 无需处理
                pass
            # 处理图片引用
            elif self.refer_type == QuoteType.IMAGE:
                ...
            # 处理多选消息引用
            elif self.refer_type == QuoteType.HISTORY:
                ...
            else:
                raise Exception(f"Quote 类型：{self.refer_type}未适配")
        else:
            raise Exception("XML 消息未能找到 refermsg")
         

class DownloadMessage(Message):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.md5: str = ""
        self.suffix: str = ""
        self.aeskey: str = ""
        self.cdnmidimgurl: str = ""
        self.length: str = ""
        
    @property
    def filepath(self) -> str:
        """返回文件路径"""
        if self.md5 and self.suffix:
            return f"{self.md5}.{self.suffix}"
        else: 
            return ""
    

# 视频消息
@Message.register_type(AddMsgType.VIDEO)
class VideoMessage(DownloadMessage):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def parse(self) -> "VideoMessage":
        """解析视频数据"""
        
        def get_format(data) -> str:
            """判断视频格式"""
            kind = filetype.guess(data)
            if kind and kind.mime.startswith("video/"):
                return kind.extension
            return "mp4"
            # raise Exception("未知的视频格式")
        
        if self.source == MessageSource.CHATROOM:
            # 分割群聊消息发送人
            sender_wxid, video_xml = self.content.split(':\n')
            # 获取发送人信息
            self.sender = await cache.chatroom.get_member(sender_wxid, self.chatroom.chatroom_id)
        elif self.source == MessageSource.FRIEND:
            video_xml = self.content

        """
        生成文件的 xml 中携带 md5 和 newmd5 两个字段，文件的唯一性以xml中的 md5 为标准，而不是解码之后的 md5。
        """
        root = ElementTree.fromstring(video_xml)
        try:
            video_msg = root.find("videomsg")
            self.md5 = video_msg.attrib.get("md5")
            self.aeskey = video_msg.attrib.get("aeskey")
            self.length = video_msg.attrib.get("length")
            self.cdnmidimgurl = video_msg.attrib.get('cdnvideourl')
        except:
            raise Exception("视频 XML 解析错误")
        
        # 检查本地是否已存在相同md5的视频文件
        tmp_dir = os.path.join(os.getcwd(), "tmp")
        if not os.path.exists(tmp_dir):
            os.makedirs(tmp_dir)
        
        # 遍历tmp文件夹，查找以相同md5开头的文件
        for fname in os.listdir(tmp_dir):
            if fname.split(".")[0] == self.md5:
                self.suffix = fname.split(".")[-1]
                return self
        
        # 如果本地不存在，则下载视频
        if self.length and self.length.isdigit:
            video_bytes = await self.chunk_download()
        else:
            raise Exception("视频下载失败: 参数错误")
        
        # 确定视频格式
        self.suffix = get_format(video_bytes)
            
        # 保存视频文件
        file_name = f"{self.md5}.{self.suffix}"
        file_path = os.path.join(tmp_dir, file_name)
        
        try:
            async with aiofiles.open(file_path, "wb") as f:
                await f.write(video_bytes)
                
            # Redis 记录过期时间, 如果能 get 到说明还没过期 
            exp = int(time.time()) + conf().get("VIDEO_EXPIRE", 60*2)
            await bot.redis.set(file_name, "", ex=exp)
            logger.info(f"视频已保存到: {self.filepath}")
        except Exception as e:
            logger.error(f"视频保存失败: {e}")
            
        return self
    
    async def chunk_download(self) -> bytes:
        """分段下载视频"""
        data_len = int(self.length)
        chunk_size = 64 * 1024
        chunks = math.ceil(data_len / chunk_size)
        video_data = bytearray()
        for i in range(chunks):
            logger.debug(f"正在下载 chunk{i+1}")
            sta_pos = i * chunk_size
            download_size = min(chunk_size, data_len - sta_pos)
            data = await bot.download_chunk_video(
                msg_id=self.msg_id, 
                to_wxid=self.from_wxid, 
                data_len=data_len, 
                sta_pos=sta_pos,
                download_size=download_size)
            if data:
                video_data.extend(data)
                logger.debug(f"视频分段{i+1}下载成功")
            else:
                raise Exception("视频下载失败，返回数据为空")
        return video_data
    

# 语音消息
@Message.register_type(AddMsgType.VOICE)
class VoiceMessage(DownloadMessage):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.suffix = "wav"
    
    async def parse(self) -> "VoiceMessage":
        if self.source == MessageSource.CHATROOM:
            # 分割群聊消息发送人
            sender_wxid, voice_xml = self.content.split(':\n')
            # 获取发送人信息
            self.sender = await cache.chatroom.get_member(sender_wxid, self.chatroom.chatroom_id)
        elif self.source == MessageSource.FRIEND:
            voice_xml = self.content
        
        root = ElementTree.fromstring(voice_xml)
        voice_url = voice_length = None
        if voice_msg := root.find("voicemsg"):
            voice_url = voice_msg.attrib.get("voiceurl")
            voice_length = int(voice_msg.attrib.get("length"))
        
        # 长语音消息返回的是 voice_url 和 length
        if voice_url and voice_length:
            base64_str = await bot.download_voice(msg_id=self.msg_id, voiceurl=voice_url, length=voice_length)
        else:
            base64_str = self.data.get("ImgBuf", {}).get("buffer")
        
        if not base64_str:
            raise Exception("语音消息未找到 base64 数据")
        
        # 保存语音消息
        await self.save_voice(base64_str)    
        return self


    async def save_voice(self, data) -> str:
        """silk 格式的 base64 数据保存到 {md5}.wav"""
        try:
            silk_byte = base64.b64decode(data)
            wav_data = await pysilk.async_decode(silk_byte, to_wav=True)
            self.md5 = hashlib.md5(wav_data).hexdigest()
            file_name = f"{self.md5}.{self.suffix}"
            tmp_dir = os.path.join(os.getcwd(), "tmp")
            os.makedirs(tmp_dir, exist_ok=True)  # 确保目录存在
            filepath = os.path.join(tmp_dir, file_name)
            if not os.path.exists(filepath):
                async with aiofiles.open(filepath, "wb") as f:  # 二进制写入
                    await f.write(wav_data)
            
            # Redis 记录过期时间
            exp = int(time.time()) + conf().get("VOICE_EXPIRE", 60*2)
            await bot.redis.set(file_name, "", ex=exp)
            logger.info(f"图片已保存到: {self.filepath}")
        except Exception as e:
            logger.error(f"图片保存失败: {e}")
            raise


# 系统消息
@Message.register_type(AddMsgType.SYSTEMMSG)
class SystemMessage(Message):
    """拍一拍/成员被移出群聊/解散群聊/群公告/群待办"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sys_type: SystemMsgType
        
        
    async def parse(self) -> "SystemMessage":
        """解析系统消息"""
        if self.source == MessageSource.CHATROOM:
            # 分割群聊消息发送人
            sender_wxid, sysmsg_xml = self.content.split(':\n')
            # 获取发送人信息
            self.sender = await cache.chatroom.get_member(sender_wxid, self.chatroom.chatroom_id)
        elif self.source == MessageSource.FRIEND:
            sysmsg_xml = self.content
            
        try:
            root = ElementTree.fromstring(sysmsg_xml)
            # 检查XML中存在的节点来确定消息类型
            if root.find("pat") is not None:
                self.sys_type = SystemMsgType.PAT
                rtn_msg = PatMessage(**self.__dict__)
            elif root.find("mmchatroombarannouncememt") is not None:
                self.sys_type = SystemMsgType.ANNOUNCEMENT
                rtn_msg = AnnouncementMessage(**self.__dict__)
            elif root.find("todo") is not None:
                self.sys_type = SystemMsgType.TODO
                rtn_msg = TodoMessage(**self.__dict__)
            elif root.find("revokemsg") is not None:
                self.sys_type = SystemMsgType.REVOKE
                rtn_msg = RevokeMessage(**self.__dict__)
            elif root.find("sysmsgtemplate") is not None:
                # self.sys_type = SystemMsgType.TEMPLATE
                # rtn_msg = InviteMessage(**self.__dict__)
                return logger.warning("检测到群聊邀请 AddMsg消息，已忽略")
            elif root.find("ClientCheckGetExtInfo") is not None:
                # 忽略系统提示
                return None
            elif root.find("functionmsg") is not None:
                logger.warning("系统消息类型:functionmsg未适配")
                return None
            else:
                raise Exception("系统消息XML解析失败: 无法确定消息类型")
            
            return await rtn_msg.parse(root)
        except Exception as e:
            logger.error(f"系统消息XML解析失败: {e}")
            raise


# 群聊邀请消息
class InviteMessage(SystemMessage):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.invite_type: int  # 0： 直接    1： 扫码
        self.invite_from: ChatroomMember
        self.invite_to: list[ChatroomMember] = []
        
    async def parse(self, root: ElementTree.Element) -> "InviteMessage":
        """解析群聊邀请信息"""
        # 判断 System Template 类型
        if (sysmsgtemplate := root.find("sysmsgtemplate")) is not None:
            if (content_template := sysmsgtemplate.find("content_template")) is not None:
                template_type = content_template.attrib.get("type")
                if template_type not in ["tmpl_type_profile", "tmpl_type_profilewithrevoke"]:
                    logger.warning("System Template消息，非群聊邀请")
                    return None
                template = content_template.find("template").text
                self.invite_type = 1 if "二维码" in template else 0
            else:
                raise Exception("解析System Template消息错误: 未找到 content_template 节点")
        else:
            raise Exception("解析System Template消息错误: 未找到 sysmsgtemplate 节点")
        
        # 解析邀请人
        if (link_list := content_template.find("link_list")) is None:
            raise Exception("解析System Template消息错误: 未找到 link_list 节点")
        
        for link in link_list.findall("link"):
            link_name = link.attrib.get("name")
            if (member_list := link.find("memberlist")) is None:
                continue
            # 邀请人
            if link_name == "username" and member_list.find("member"):
                member = member_list.find("member")
                wxid = member.findtext("username")
                self.invite_from = await cache.chatroom.get_member(wxid, self.chatroom.chatroom_id)
            elif link_name == "names" or link_name == "adder":  # 被邀请人
                for member in member_list.findall("member"):
                    wxid = member.findtext("username")
                    invitee = await cache.chatroom.get_member(wxid, self.chatroom.chatroom_id)
                    self.invite_to.append(invitee)
            else:
                logger.warning(f"解析群聊邀请信息错误：未知的link_name - {link_name}")
                    
        return self


# 撤回消息
class RevokeMessage(SystemMessage):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.revoke_msgid: str
        self.revoke_newmsgid: str
        self.revoke_session: str
        self.revoke_replacemsg: str
        self.revoke_msg: Message
        
    async def parse(self, root: ElementTree.Element) -> "RevokeMessage":
        """解析撤回消息"""
        revoke = root.find("revoke")
        self.revoke_msgid = revoke.findtext("msgid")
        self.revoke_newmsgid = revoke.findtext("newmsgid")
        self.revoke_session = revoke.findtext("session")
        self.revoke_replacemsg = revoke.findtext("replacemsg")

        if self.revoke_msgid and self.revoke_newmsgid:
            # TODO 提取之前的消息对象：需要保存之前的消息 redis or 数据库
            self.revoke_msg = None
        else:
            raise Exception(f"撤回消息解析错误: msgid 或 newmsgid 为空，无法找到源消息")

        return self


# 群公告会发送AppMsg：MsgType: 49, type: 87和SystemMsg：MsgType：10002两种消息，检测SystemMsg这个消息
class AnnouncementMessage(SystemMessage):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ann_from: ChatroomMember
        self.ann_text: str
        self.ann_from_wxid: str
        self.ann_edit_time: str
        self.ann_ctrlflag: str
        # self.ann_data: list[AnnouncementData]  TODO
        
        
    async def parse(self, root: ElementTree.Element) -> "AnnouncementMessage":
        """解析群公告消息"""
        ann_node = root.find("mmchatroombarannouncememt")
        if ann_node is not None:
            # 获取内容
            self.ann_text = ann_node.findtext("content")
            
            # 获取 xmlcontent 并解析
            xml_text = ann_node.findtext("xmlcontent")
            if xml_text:
                group_notice = ElementTree.fromstring(xml_text)
                
                # 提取关键信息
                self.ann_edit_time = group_notice.findtext("edittime")
                self.ann_ctrlflag = group_notice.findtext("ctrlflag")
                
                # 获取发送人
                if (source := group_notice.find("source")) is not None:
                    from_wxid = source.findtext("fromusr")
                    self.ann_from = await cache.chatroom.get_member(from_wxid, self.chatroom.chatroom_id)
                    return self
                else:
                    raise Exception("群公告解析失败: 无法获取发送人")
            else:
                raise Exception("群公告解析失败: 无法获取XML内容")
        else:
            raise Exception("找不到 mmchatroombarannouncememt 节点")


# 群待办消息
class TodoMessage(SystemMessage):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.todo_op: int
        self.todo_id: str
        self.todo_from: ChatroomMember


    async def parse(self, root: ElementTree.Element) -> "TodoMessage":
        """解析群待办消息""" 
        if (todo_node := root.find("todo")) is not None:        
            self.todo_op = todo_node.findtext("op")
            self.todo_id = todo_node.findtext("related_msgid")
            self.todo_from = todo_node.findtext("creator")
            return self
        else:
            raise Exception("找不到 todo 节点")


# 拍一拍消息
class PatMessage(SystemMessage):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pat_from: ChatroomMember | Friend
        self.pat_to: ChatroomMember | Friend
        
    async def parse(self, root: ElementTree.Element) -> "PatMessage":
        """解析拍一拍消息"""
        pat = root.find("pat")
        fromusername = pat.findtext("fromusername")
        pattedusername = pat.findtext("pattedusername")
        chatusername = pat.findtext("chatusername")
        patsuffix = pat.findtext("patsuffix")

        if fromusername and pattedusername and chatusername and patsuffix:
            if self.source == MessageSource.CHATROOM:
                self.pat_from = await cache.chatroom.get_member(fromusername, chatusername)
                self.pat_to = await cache.chatroom.get_member(pattedusername, chatusername)
            elif self.source == MessageSource.FRIEND:
                self.pat_from = await cache.friend.get(fromusername)
                self.pat_to = await cache.friend.get(pattedusername)
            else:
                raise Exception(f"拍一拍消息解析错误: 消息来源未知: {self.source}")
        else:
            raise Exception(f"拍一拍消息解析错误: XML参数为空")

        return self
    
    
# 图片消息
@Message.register_type(AddMsgType.IMAGE)
class ImageMessage(DownloadMessage):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    
    async def parse(self) -> "ImageMessage":
        """解析图片消息"""
        if self.source == MessageSource.CHATROOM:
            # 分割群聊消息发送人
            sender_wxid, img_xml = self.content.split(':\n')
            # 获取发送人信息
            self.sender = await cache.chatroom.get_member(sender_wxid, self.chatroom.chatroom_id)
        elif self.source == MessageSource.FRIEND:
            img_xml = self.content
        
        try:
            root = ElementTree.fromstring(img_xml)
            img_element = root.find('img')
            if img_element is not None:
                self.aeskey = img_element.get('aeskey')
                self.cdnmidimgurl = img_element.get('cdnmidimgurl')
                self.length = img_element.get('length')
                self.md5 = img_element.get('md5')
                logger.debug(f"解析图片XML成功: aeskey={self.aeskey}, length={self.length}, cdnmidimgurl={self.cdnmidimgurl} md5={self.md5}")
                # 遍历tmp文件夹，检查是否已存在相同md5的图片文件
                tmp_dir = os.path.join(os.getcwd(), "tmp")
                if not os.path.exists(tmp_dir):
                    os.makedirs(tmp_dir)
                for fname in os.listdir(tmp_dir):
                    if fname.split(".")[0] == self.md5:
                        self.path = os.path.join(tmp_dir, fname)
                        return self
                await self.download()
                return self
            else:
                return logger.error("解析图片消息失败：xml未找到标签img")
        except Exception as e:
            return logger.error(f"解析图片消息失败: {e}, ")
        
        
    async def download(self):
        """下载图片"""
        
        def get_format(data) -> str:
            """判断图片格式"""
            kind = filetype.guess(data)
            if kind and kind.mime.startswith("image/"):
                return kind.extension
            raise Exception("未知的图片格式")
        
        if self.length and self.length.isdigit:
            """采用分段下载"""
            try:
                data_len = int(self.length)
                logger.debug("正在尝试分段下载图片")
                
                chunk_size = 64 * 1024
                chunks = math.ceil(data_len / chunk_size)
                image_data = bytearray()
                for i in range(chunks):
                    logger.debug(f"正在下载 chunk{i+1}")
                    sta_pos = i * chunk_size
                    download_size = min(chunk_size, data_len - sta_pos)
                    data = await bot.download_chunk_image(
                        msg_id=self.msg_id, 
                        to_wxid=self.from_wxid, 
                        data_len=data_len, 
                        sta_pos=sta_pos,
                        download_size=download_size)
                    if data:
                        image_data.extend(data)
                        logger.debug(f"图片分段{i+1}下载成功")
                    else:
                        raise Exception("图片下载失败，返回数据为空")
                if len(image_data) > 0:
                    logger.debug("图片下载完成，正在验证完整性...")
                    try:
                        ImageFile.LOAD_TRUNCATED_IMAGES = True  # 允许加载截断的图片

                        image_data = bytes(image_data)
                        # 验证图片数据
                        Image.open(io.BytesIO(image_data))
                        img_data = base64.b64encode(image_data).decode('utf-8')
                        logger.info(f"分段下载图片成功，总大小: {len(image_data)} 字节")
                    except Exception as img_error:
                        logger.error(f"验证分段下载的图片数据失败: {img_error}")
                        # 如果验证失败，尝试使用download_image
                        if self.aeskey and self.cdnmidimgurl:
                            logger.warning("图片下载失败尝试使用CDN...")
                            img_data = await bot.download_cdn_image(self.aeskey, self.cdnmidimgurl)
            except Exception as e:
                logger.warning(f"图片分段下载错误: {e}，正在尝试CDN下载...")
                img_data = await bot.download_cdn_image(self.aeskey, self.cdnmidimgurl)
        elif self.aeskey and self.cdnmidimgurl:
            logger.warning("图片下载失败尝试使用CDN...")
            img_data = await bot.download_cdn_image(self.aeskey, self.cdnmidimgurl)
                
        
        # 保存图片
        if img_data and self.md5:
            try:
                image_data = base64.b64decode(img_data)

                # 确保files目录存在
                files_dir = os.path.join(os.getcwd(), "tmp")
                os.makedirs(files_dir, exist_ok=True)

                # 根据MD5值生成文件名
                file_extension = get_format(image_data)
                file_name = f"{self.md5}.{file_extension}"
                file_path = os.path.join(files_dir, file_name)

                # 保存图片文件（使用aiofiles异步方式
                async with aiofiles.open(file_path, "wb") as f:
                    await f.write(image_data)
                    
                self.suffix = file_extension
                logger.info(f"图片已保存到: {self.filepath}")
                
                # Redis 记录过期时间
                exp = int(time.time()) + conf().get("IMG_EXPIRE", 60*2)
                await bot.redis.set(file_name, "", ex=exp)
            except Exception as save_error:
                logger.error(f"保存图片文件失败: {save_error}")