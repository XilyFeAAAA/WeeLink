from src.schema import (
    AddMsgType, ChatroomMember, 
    Friend, MessageSource, XmlType,
    Chatroom, EventType)
from src.schema.dataclass import TextForward, ImageForward, VoiceForward, LinkForward, VideoForward, QuoteForward, Forward
from src.manager import cache
from src.matcher import Matcher
from src.utils import logger, redis
from src.bot import Bot
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



class AddMessage:
    _type_registry: dict[AddMsgType, type["AddMessage"]] = {}

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
        # 事件类型
        self.event_type = None


    @classmethod
    def register_type(cls, msg_type: type["AddMessage"]):
        def decorator(subclass):
            cls._type_registry[msg_type] = subclass
            return subclass
        return decorator


    def _get_base_params(self):
        """获取基础参数，用于传递给子类构造函数"""
        return {
            'data': self.data,
            'from_wxid': self.from_wxid,
            'to_wxid': self.to_wxid,
            'msg_type': self.msg_type,
            'content': self.content,
            'create_time': self.create_time,
            'msg_source': self.msg_source,
            'msg_id': self.msg_id,
            'new_msg_id': self.new_msg_id,
            'msg_seq': self.msg_seq,
            'chatroom': self.chatroom,
            'sender': self.sender,
            'source': self.source
        }
        
    async def publish(self):
        """发布消息事件"""
        if self.event_type:
            await Matcher.publish(event=self.event_type, data=self)

    @classmethod
    async def new(cls, data) -> "AddMessage":
        bot = await Bot.get_instance()
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
        if data["FromUserName"]["string"] == bot.status.wxid: return
        # 群聊 or 私聊判断
        if from_wxid.endswith("@chatroom"):
            source = MessageSource.CHATROOM
            chatroom = await cache.chatroom.get(from_wxid)
        else:
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
            cls = await cls.process()
            # 处理完成后发布事件
            if cls is not None:
                await cls.publish()
        else:
            logger.warning(f"未识别的消息类型:{msg_type}")
            return None
        

# 可保存消息基类
class SavableMessage:
    
    def __init__(self):
        self.md5: str = ""
        self.ext: str = ""


    @property
    def filepath(self) -> str:
        """返回文件路径"""
        return f"{self.md5}.{self.ext}" if self.md5 and self.ext else ""
            
    
    def _get_file_format(self, data: bytes) -> str:
        """获取文件格式，由子类重写"""
    
    
    async def _download_file(self) -> bytes:
        """下载文件的具体实现，由子类重写"""
        raise NotImplementedError


    async def download(self) -> str:
        """统一的下载接口"""
        # 解析文件
        tmp_dir = os.path.join(os.getcwd(), "tmp")
        os.makedirs(tmp_dir, exist_ok=True)
        
        # MD5判断存在
        if self.md5:
            for fname in os.listdir(tmp_dir):
                if fname.split(".")[0] == self.md5:
                    self.ext = fname.split(".")[-1]
                    return os.path.join(tmp_dir, fname)
        
        # 下载
        file_data = await self._download_file()
        if not file_data:
            raise Exception(f"{self.__class__.__name__}下载失败")
        
        # 没有md5就生成
        if not self.md5:
            self.md5 = hashlib.md5(file_data).hexdigest()
        
        self.ext = self._get_file_format(file_data)
        
        # 保存文件
        file_name = f"{self.md5}.{self.ext}"
        file_path = os.path.join(tmp_dir, file_name)
        
        try:
            async with aiofiles.open(file_path, "wb") as f:
                await f.write(file_data)
                
            EXPIRE_SECONDS = 60 * 30
            exp = int(time.time()) + EXPIRE_SECONDS
            await redis.set(file_name, "", ex=exp)
            logger.info(f"文件已保存到: {self.filepath}")
            return file_path
        except Exception as e:
            logger.error(f"文件保存失败")
            raise



# 文字消息
@AddMessage.register_type(AddMsgType.TEXT)
class TextMessage(AddMessage):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.text: str = ""
        self.ats: list[ChatroomMember] = []
        self.at_me: bool = False
        self.event_type = EventType.TEXT
        

    async def process(self) -> "TextMessage":
        bot = await Bot.get_instance()
        
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
            self.at_me = any(at.wxid == bot.status.wxid for at in self.ats)
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


@AddMessage.register_type(AddMsgType.APPMSG)
class AppMessage(AddMessage):
   
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    async def process(self) -> "AppMessage":
        """解析XML消息"""
        if self.source == MessageSource.CHATROOM:
            # 分割群聊消息发送人
            sender_wxid, appmsg_xml = self.content.split(':\n')
            # 获取发送人信息
            self.sender = await cache.chatroom.get_member(sender_wxid, self.chatroom.chatroom_id)
        elif self.source == MessageSource.FRIEND:
            appmsg_xml = self.content
            
        try:
            root = ElementTree.fromstring(appmsg_xml)
            appmsg = root.find("appmsg")
            type = int(appmsg.findtext("type"))
            if type == XmlType.QUOTE:
                cls = QuoteMessage(**self._get_base_params())
            elif type == XmlType.FILE:
                cls = FileMessage(**self._get_base_params())
            elif type == XmlType.SHARE_LINK:
                cls = LinkMessage(**self._get_base_params())
            elif type == XmlType.UPLOAD:
                cls = UploadMessage(**self._get_base_params())
            elif type == XmlType.FORWORD:
                cls = ForwardMessage(**self._get_base_params())
            else:
                raise Exception(f"未识别的 XML 类型:{type}")
            
            return await cls.process(appmsg)
        except Exception as e:
            return logger.error(f"解析xml消息失败: {e}")
        

class QuoteMessage(AddMessage):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.quote_type: AddMsgType
        self.quote_content: str
        self.quote_data: AddMessage
        self.event_type = EventType.QUOTE
        
    async def process(self, appmsg: ElementTree.Element):
        """解析引用消息"""
        
        self.quote_content = appmsg.findtext("title")
        if refermsg := appmsg.find("refermsg"):
            msg_type = int(refermsg.findtext("type"))
            self.quote_type = AddMsgType(msg_type)
            
            # 构建参数
            kwargs = {
                "data": None,
                "from_wxid": refermsg.findtext("chatusr"),
                "to_wxid": self.to_wxid,
                "msg_type": msg_type,
                "content": refermsg.findtext("content"),
                "create_time": refermsg.findtext("createtime"),
                "msg_source": refermsg.findtext("msgsource"),
                "msg_id": 0,
                "new_msg_id": 0,
                "msg_seq": 0,
                "chatroom": None,
                "sender": None,
                "source": MessageSource.FRIEND
            }
            # 处理文本引用
            if self.quote_type == AddMsgType.TEXT:
                self.quote_data = TextMessage(**kwargs)
            # 处理图片引用
            elif self.quote_type == AddMsgType.IMAGE:
                self.quote_data = ImageMessage(**kwargs)
            # 处理多选消息引用
            elif self.quote_type == AddMsgType.APPMSG:
                return logger.warning("未适配转发消息")
            else:
                raise Exception(f"Quote 类型：{self.refer_type}未适配")
            
            await self.quote_data.process()
            return self
        else:
            raise Exception("XML 消息未能找到 refermsg")


class UploadMessage(AddMessage):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.upload_title: str
        self.upload_totallen: str
        self.upload_ext: str
        self.upload_token: str
        self.upload_status: str
        self.upload_md5: str
        self.event_type = EventType.UPLOAD
    
    
    async def process(self, appmsg: ElementTree.Element):
        """解析上传文件"""
        self.upload_title = appmsg.findtext("title")
        self.upload_md5 = appmsg.findtext("md5")
        
        # 从appattach节点获取其他属性
        if appattach := appmsg.find("appattach"):
            self.upload_totallen = appattach.findtext("totallen")
            self.upload_ext = appattach.findtext("fileext")
            self.upload_token = appattach.findtext("fileuploadtoken")
            self.upload_status = appattach.findtext("status")

        return self


class FileMessage(AddMessage, SavableMessage):
    
    def __init__(self, **kwargs):
        AppMessage.__init__(self, **kwargs)
        SavableMessage.__init__(self)
        self.file_title: str = None
        self._file_attachid: str = None
        self.event_type = EventType.FILE

    def _get_file_format(self, data: bytes) -> str:
        return self.ext


    async def process(self, appmsg: ElementTree.Element):
        """解析文件"""
        self.file_title = appmsg.findtext("title")
        self.md5 = appmsg.findtext("md5")
        
        appattach = appmsg.find("appattach")
        if appattach is not None:
            self._file_attachid = appattach.findtext("attachid")
            self.ext = appattach.findtext("fileext")
        else:
            raise Exception("未找到文件附件信息")
        return self

        
    async def _download_file(self) -> bytes:
        """下载文件"""
        if not self._file_attachid:
            raise Exception("文件附件ID不存在，无法下载文件")

        bot = await Bot.get_instance()
        base64_str = await bot.download_file(self._file_attachid)
        return base64.b64decode(base64_str)


class LinkMessage(AddMessage):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.link_title: str
        self.link_desc: str
        self.link_url: str
        self.link_displayname: str
        self.link_username: str
        self.event_type = EventType.LINK
    
    async def process(self, appmsg: ElementTree.Element):
        """解析分享消息"""        
        self.link_title = appmsg.findtext('title', '').strip()
        self.link_desc = appmsg.findtext('des', '').strip()
        self.link_url = appmsg.findtext('url', '').strip()
        self.link_username = appmsg.findtext('sourceusername', '').strip()
        self.link_displayname = appmsg.findtext('sourcedisplayname', '').strip()
        return self


class ForwardMessage(AddMessage):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.forward_title: str
        self.forward_desc: str
        self.forwards: list[Forward] = []
        self.event_type = EventType.FORWARD
        
    async def process(self, appmsg: ElementTree.Element):
        """解析转发消息"""
        self.forward_title = appmsg.findtext("title")
        self.forward_desc = appmsg.findtext("des")
        # 直接查找 recorditem 节点（获取CDATA文本）
        recorditem_cdata = appmsg.findtext("recorditem")
        # 解析CDATA内容为XML
        record_info = ElementTree.fromstring(recorditem_cdata)
        # 直接查找 datalist 节点
        datalist = record_info.find("datalist")
        for dataitem in datalist.findall("dataitem"):
            datatype = dataitem.attrib.get("datatype")
            param = {
                "sourcename": dataitem.findtext("sourcename"),
                "sourcetime": dataitem.findtext("sourcetime"),
                "datadesc": dataitem.findtext("datadesc"),
                "sourceheadurl": dataitem.findtext("sourceheadurl"),
            }
            if datatype == "1":  # 文本消息 or 引用消息 or 语音消息
                if dataitem.find("refermsgitem") is not None:
                    # 引用类型
                    forward = QuoteForward(
                        fromnewmsgid=dataitem.findtext("fromnewmsgid"),
                        refermsgitem=dataitem.find("refermsgitem"),
                        **param
                    )
                elif "语音" in param["datadesc"]:
                    forward = VoiceForward(**param)
                else:
                    forward = TextForward(
                        fromnewmsgid=dataitem.findtext("fromnewmsgid"),
                        **param
                    )
            elif datatype == "2":  # 图片消息
                forward = ImageForward(
                    datafmt=dataitem.findtext("datafmt"),
                    cdndataurl=dataitem.findtext("cdndataurl"),
                    cdndatakey=dataitem.findtext("cdndatakey"),
                    fullmd5=dataitem.findtext("fullmd5"),
                    datasize=dataitem.findtext("datasize"),
                    **param
                )
            elif datatype == "4":  # 视频消息
                forward = VideoForward(
                    datafmt=dataitem.findtext("datafmt"),
                    cdndataurl=dataitem.findtext("cdndataurl"),
                    cdndatakey=dataitem.findtext("cdndatakey"),
                    fullmd5=dataitem.findtext("fullmd5"),
                    datasize=dataitem.findtext("datasize"),
                    **param
                )
            elif datatype == "5":  # 链接消息
                forward = LinkForward(
                    sourcedisplayname=dataitem.findtext("sourcedisplayname"),
                    weburlitem=dataitem.find("weburlitem"),
                    **param
                )
            self.forwards.append(forward)


        return self

# 视频消息
@AddMessage.register_type(AddMsgType.VIDEO)
class VideoMessage(AddMessage, SavableMessage):
    def __init__(self, **kwargs):
        AddMessage.__init__(self, **kwargs)
        SavableMessage.__init__(self)
        self._video_length = None
        self.event_type = EventType.VIDEO
        
    
    def _get_file_format(self, data: bytes) -> str:
        """判断视频格式"""
        kind = filetype.guess(data)
        if kind and kind.mime.startswith("video/"):
            return kind.extension
        return "mp4"
    
    async def process(self) -> "VideoMessage":
        """解析视频数据"""
        if self.source == MessageSource.CHATROOM:
            sender_wxid, video_xml = self.content.split(':\n')
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
            self._video_length = video_msg.attrib.get("length")
        except:
            raise Exception("视频 XML 解析错误")
        return self
        
    
    async def _download_file(self) -> bytes:
        """分段下载视频"""
        if self._video_length and self._video_length.isdigit:
            bot = await Bot.get_instance()
            data_len = int(self._video_length)
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
        else:
            raise Exception("视频下载失败：缺少必要参数")
    

# 语音消息
@AddMessage.register_type(AddMsgType.VOICE)
class VoiceMessage(AddMessage, SavableMessage):
    def __init__(self, **kwargs):
        AddMessage.__init__(self, **kwargs)
        SavableMessage.__init__(self, )
        self._voice_url = None
        self._voice_length = None
        self.ext = "wav"
        self.event_type = EventType.VOICE
    
    def _get_file_format(self, data: bytes) -> str:
        """语音消息固定为wav格式"""
        return "wav"
    
    async def process(self) -> "VoiceMessage":
        if self.source == MessageSource.CHATROOM:
            # 分割群聊消息发送人
            sender_wxid, voice_xml = self.content.split(':\n')
            # 获取发送人信息
            self.sender = await cache.chatroom.get_member(sender_wxid, self.chatroom.chatroom_id)
        elif self.source == MessageSource.FRIEND:
            voice_xml = self.content
        
        root = ElementTree.fromstring(voice_xml)
        voice_msg = root.find("voicemsg")
        if voice_msg is not None:
            self._voice_url = voice_msg.attrib.get("voiceurl")
            self._voice_length = int(voice_msg.attrib.get("length"))
        return self


    async def _download_file(self) -> bytes:
        """下载语音文件"""
        bot = await Bot.get_instance()
        if self._voice_url and self._voice_length:
             base64_str = await bot.download_voice(
                 msg_id=self.msg_id, 
                 voiceurl=self._voice_url, 
                 length=self._voice_length
                )
        else:
            base64_str = self.data.get("ImgBuf", {}).get("buffer")
            
        if not base64_str:
            raise Exception("语音消息未找到base64数据")
        
        silk_byte = base64.b64decode(base64_str)
        return await pysilk.async_decode(silk_byte, to_wav=True)


# 系统消息
@AddMessage.register_type(AddMsgType.SYSTEMMSG)
class SystemMessage(AddMessage):
    """拍一拍/成员被移出群聊/解散群聊/群公告/群待办"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        
    async def process(self) -> "SystemMessage":
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
                cls = PatMessage(**self._get_base_params())
            elif root.find("mmchatroombarannouncememt") is not None:
                cls = AnnouncementMessage(**self._get_base_params())
            elif root.find("todo") is not None:
                cls = TodoMessage(**self._get_base_params())
            elif root.find("revokemsg") is not None:
                cls = RevokeMessage(**self._get_base_params())
            elif root.find("sysmsgtemplate") is not None:
                # rtn_msg = InviteMessage(**self.__dict__)
                return logger.warning("检测到群聊邀请 AddMsg消息，已忽略")
            elif root.find("ClientCheckGetExtInfo") is not None:
                # 忽略系统提示
                return None
            elif root.find("functionmsg") is not None:
                logger.warning("系统消息类型:functionmsg未适配")
                return None
            else:
                return logger.warning("系统消息XML解析失败: 无法确定消息类型")
            
            return await cls.process(root)
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
        self.event_type = EventType.INVITE
        
    async def process(self, root: ElementTree.Element) -> "InviteMessage":
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
        self.revoke_msg: AddMessage
        self.event_type = EventType.REVOKE
        
    async def process(self, root: ElementTree.Element) -> "RevokeMessage":
        """解析撤回消息"""
        revoke = root.find("revokemsg")
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
        self.event_type = EventType.ANNOUNCE
        # self.ann_data: list[AnnouncementData]  TODO
        
        
    async def process(self, root: ElementTree.Element) -> "AnnouncementMessage":
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
                else:
                    raise Exception("群公告解析失败: 无法获取发送人")
            else:
                raise Exception("群公告解析失败: 无法获取XML内容")
        else:
            raise Exception("找不到 mmchatroombarannouncememt 节点")
        return self


# 群待办消息
class TodoMessage(SystemMessage):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.todo_op: int
        self.todo_id: str
        self.todo_from: ChatroomMember
        self.event_type = EventType.TODO


    async def process(self, root: ElementTree.Element) -> "TodoMessage":
        """解析群待办消息""" 
        if (todo_node := root.find("todo")) is not None:        
            self.todo_op = todo_node.findtext("op")
            self.todo_id = todo_node.findtext("related_msgid")
            self.todo_from = todo_node.findtext("creator")
        else:
            raise Exception("找不到 todo 节点")
        return self


# 拍一拍消息
class PatMessage(SystemMessage):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pat_from: ChatroomMember | Friend
        self.pat_to: ChatroomMember | Friend
        self.patsuffix: str
        self.event_type = EventType.PAT
        
    async def process(self, root: ElementTree.Element) -> "PatMessage":
        """解析拍一拍消息"""
        pat = root.find("pat")
        fromusername = pat.findtext("fromusername")
        pattedusername = pat.findtext("pattedusername")
        chatusername = pat.findtext("chatusername")
        self.patsuffix = pat.findtext("patsuffix")

        if fromusername and pattedusername and chatusername:
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
@AddMessage.register_type(AddMsgType.IMAGE)
class ImageMessage(AddMessage, SavableMessage):
    
    def __init__(self, **kwargs):
        AddMessage.__init__(self, **kwargs)
        SavableMessage.__init__(self)
        self._img_aeskey = None
        self._img_cdnurl = None
        self._img_length = None
        self.event_type = EventType.IMAGE
    
    
    def _get_file_format(self, data: bytes) -> str:
        """判断图片格式"""
        kind = filetype.guess(data)
        if kind and kind.mime.startswith("image/"):
            return kind.extension
        return "jpg"  # 默认图片格式
    
    
    async def process(self) -> "ImageMessage":
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
                self._img_aeskey = img_element.get('aeskey')
                self._img_cdnurl = img_element.get('cdnmidimgurl')
                self._img_length = img_element.get('length')
                self.md5 = img_element.get('md5')
                logger.debug(f"解析图片XML成功: aeskey={self._img_aeskey}, length={self._img_length}, cdnmidimgurl={self._img_cdnurl} md5={self.md5}")
            else:
                return logger.error("解析图片消息失败：xml未找到标签img")
        except Exception as e:
            return logger.error(f"解析图片消息失败: {e}, ")
        
        return self
        
        
    async def _download_file(self):
        """下载图片"""
        bot = await Bot.get_instance()
        
        if self._img_length and self._img_length.isdigit():
            """采用分段下载"""
            try:
                data_len = int(self._img_length)
                logger.debug("正在尝试分段下载图片")
                
                chunk_size = 5 * 1024 * 1024  # 5M
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
                # 验证图片数据
                try:
                    ImageFile.LOAD_TRUNCATED_IMAGES = True
                    image_bytes = bytes(image_data)
                    Image.open(io.BytesIO(image_bytes))
                    return image_bytes
                except Exception as e:
                    logger.error(f"验证分段下载的图片数据失败: {e}")
                    # 验证失败，尝试CDN下载
                    if self._img_aeskey and self._img_cdnurl:
                        logger.warning("图片验证失败，尝试使用CDN下载...")
                        img_data = await bot.download_cdn_image(self.aeskey, self.cdnmidimgurl)
            except Exception as e:
                logger.warning(f"图片分段下载错误: {e}，正在尝试CDN下载...")
                img_data = await bot.download_cdn_image(self.aeskey, self.cdnmidimgurl)
        elif self.aeskey and self.cdnmidimgurl:
            logger.warning("图片下载失败尝试使用CDN...")
            img_data = await bot.download_cdn_image(self.aeskey, self.cdnmidimgurl)
                
        # 处理CDN下载返回的base64字符串
        return base64.b64decode(img_data)