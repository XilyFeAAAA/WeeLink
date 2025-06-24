# standard library
import io
import re
import math
import time
import pysilk
import hashlib
import base64
import asyncio
import filetype
import aiofiles
from PIL import Image, ImageFile
from xml.etree import ElementTree

# local library
from .api_mixin import ApiMixin
from .docs_mixin import DocsMixin
from weelink.core.flow import get_broker, EventType
from weelink.core.adapter import Adapter, registry_adapter
from weelink.core.adapter.metadata import ConfigField
from weelink.core.message import (
    Text, File, Link, Quote, MessageSource, MessageComponent, 
    XmlType, AddMsgType, MessageEvent
)
from weelink.core.utils import (
    create_device_name, create_device_id, logger, get, find_temp_file,
    TEMP_DIR
)



@registry_adapter(
    name="wechatpad855", 
    desc="855版本PAD协议",
    version="8.0.55",
    platform="ipad"
)
class WechatPad855Adapter(Adapter, ApiMixin, DocsMixin):
    
    CONFIG_FIELDS = [
        ConfigField(
            label="协议地址",
            key="url",
            type="string",
            required=True,
            placeholder="请输入协议服务地址",
            description="协议服务地址，例如：http://127.0.0.1:8000"
        )
    ]
    
    def __init__(self, adapter_config: dict):
        self.is_logged = False
        self.adapter_config = adapter_config

        # 协议配置项
        if "url" not in self.adapter_config:
            raise Exception("协议BASEURL为空")
        self.base_url = self.adapter_config.get("url")
        # 微信配置项
        self.wxid = self.adapter_config.get("wxid", "")
        self.nickname = self.adapter_config.get("nickname", "")
        self.phone = self.adapter_config.get("phone", "")
        self.device_name = self.adapter_config.get("device_name", "") or create_device_name()
        self.device_id = self.adapter_config.get("device_id", "") or create_device_id()

    
    async def run(self) -> None:
        """启动适配器"""
        
        # 检查协议
        max_retries = 3
        for cnt_retry in range(max_retries):
            try:
                resp = await get(self.base_url, json=False)
                if resp.status in [200, 201, 401, 404]:
                    logger.info("协议连接成功")
                    break
            except Exception as e:
                logger.warning(f"第{cnt_retry+1}次协议连接失败")
            await asyncio.sleep(5)
            if cnt_retry >= max_retries:
                raise Exception("协议连接超时")
        
        # 登录微信
        try:
            await self.api_login()
        except Exception as e:
            raise Exception(f"协议登录失败: {str(e)}")
        
        
        # 检查登录状态
        self.is_logged = await self.api_heartbeat()
        if not self.is_logged:
            return logger.warning(f"账号{self.wxid}登录失败，请检查日志文件")
        
        # 轮询消息
        failure_count, max_failures = 0, 3
        while True:
            status, data = await self.api_sync_message()
        
            if not status or data is None:
                failure_count += 1
                if failure_count > max_failures:
                    return logger.critical("接收消息失败次数过多，退出消息处理循环")
            failure_count = 0
            if isinstance(data, dict):
                for item in (data.get("AddMsgs") or []):
                    await self.process_message("AddMessage", item)
                for item in (data.get("ModContacts") or []):
                    await self.process_message("ModContact", item)
            elif isinstance(data, str):
                if "已退出登录" in data or "会话已过期" in data:
                    return logger.warning(f"接收到退出消息")      
            
            await asyncio.sleep(0.5)


    async def process_message(self, type: str, raw_data: dict) -> None:
        # 将通用信息独立出来，避免convert_message和convert_event耦合
        common_data = await self.extract_common_data(type, raw_data)
        if common_data is None:
            return
        
        component = await self.convert_component(type, common_data)
        if component is None:
            return
        
        event = await self.convert_event(type, common_data, component)
        if event:
            await get_broker().publish(event)


    async def extract_common_data(self, type: str, data: dict) -> dict:
        """提取消息的通用信息，包括发送者、接收者、内容等"""
        if type == "AddMessage":
            # 通用信息
            from_wxid = data.get("FromUserName", {}).get("string")
            # to_wxid = data.get("ToUserName", {}).get("string")
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
            if data["FromUserName"]["string"] == self.wxid:
                return None
            
            common_data = {
                "data": data,
                "from_wxid": from_wxid,
                "msg_type": msg_type,
                "content": content,
                "create_time": create_time,
                "msg_source": msg_source,
                "msg_id": msg_id,
                "new_msg_id": new_msg_id,
                "msg_seq": msg_seq,
            }
            
            # 群聊 or 私聊判断
            if from_wxid.endswith("@chatroom"):
                common_data["is_chatroom"] = True
                # AddMsg在群聊中无论什么消息，Content都是wxid:\n....
                if ":\n" not in content:
                    return logger.error("群聊消息解析失败，Content中不含:\n")
                sender_wxid, message_content = content.split(':\n', 1)
                common_data["sender_wxid"] = sender_wxid
                common_data["content"] = message_content
                
                # AT判断
                root = ElementTree.fromstring(msg_source)
                ats = root.find("atuserlist").text if root.find("atuserlist") is not None else ""
                ats = ats.lstrip(",").split(",") if ats else []
                common_data["at_wxids"] = ats
            else:
                common_data["is_chatroom"] = False
                common_data["sender_wxid"] = from_wxid
                common_data["content"] = content
                common_data["at_wxids"] = []
            
            return common_data
        
        return None


    async def convert_component(self, type: str, common_data: dict) -> MessageComponent:
        """将协议传来的JSON处理为MessageComponent"""
        component_params = {}
        if type == "AddMessage":
            component_params = {
                "content": common_data["content"],
                "create_time": common_data["create_time"],
                "msg_source": common_data["msg_source"],
                "msg_id": common_data["msg_id"],
                "new_msg_id": common_data["new_msg_id"],
                "msg_seq": common_data["msg_seq"],
            }
            msg_type = common_data["msg_type"]
            # 具体消息处理
            if msg_type == AddMsgType.TEXT:
                text = component_params["content"]
                if '\u2005' in text:  # 特殊空格，通常用于@消息
                    text = re.sub(r'@[^\u2005]*\u2005', '', text)
                return Text(
                    text=text,
                    **component_params
                )
            elif msg_type == AddMsgType.VOICE:
                root = ElementTree.fromstring(component_params["content"])
                if (voice_msg := root.find("voicemsg")) is None:
                    return logger.error("语音消息解析失败，voicemsg字段为空")
                
                voice_url = voice_msg.attrib.get("voiceurl")
                voice_length = int(voice_msg.attrib.get("length"))
                base64_str = await self.api_download_voice(
                    msg_id=component_params["msg_id"], 
                    voiceurl=voice_url, 
                    length=voice_length
                ) if voice_url and voice_length else common_data["data"].get("ImgBuf", {}).get("buffer")

                if not base64_str:
                    return logger.error("语音消息未找到base64数据")
        
                silk_byte = base64.b64decode(base64_str)
                voice_data = await pysilk.async_decode(silk_byte, to_wav=True)
                md5 = hashlib.md5(voice_data).hexdigest()
                
                if (file_name := find_temp_file(md5)) is None:
                    file_name = f"{md5}.wav"
                
                if not (file_path := TEMP_DIR / file_name).exists():
                    try:
                        async with aiofiles.open(file_path, "wb") as f:
                            await f.write(voice_data)
                    except Exception as e:
                        return logger.error(f"音频文件保存失败: {str(e)}")
                
                return File(
                    path=file_path,
                    md5=md5,
                    ext="wav",
                    **component_params
                )
            elif msg_type == AddMsgType.IMAGE:
                try:
                    root = ElementTree.fromstring(component_params["content"])
                    if (img_element := root.find('img')) is None:
                        return logger.error("解析图片消息失败：xml未找到标签img")
                    img_aeskey = img_element.get('aeskey')
                    img_cdnurl = img_element.get('cdnmidimgurl')
                    img_length = img_element.get('length')
                    md5 = img_element.get('md5')                        
                except Exception as e:
                    return logger.error(f"解析图片消息失败: str({e})")
                
                if (file_name := find_temp_file(md5)) is None:
                    # 不存在的话就下载 + 找后缀
                    if img_length and img_length.isdigit():
                        """采用分段下载"""
                        try:
                            data_len = int(img_length)
                            chunk_size = 512 * 1024  # 512KB
                            chunks = math.ceil(data_len / chunk_size)
                            image_data = bytearray()
                            for i in range(chunks):
                                sta_pos = i * chunk_size
                                download_size = min(chunk_size, data_len - sta_pos)
                                if data := await self.api_download_chunk_image(
                                    msg_id=component_params["msg_id"], 
                                    to_wxid=common_data["from_wxid"], 
                                    data_len=data_len, 
                                    sta_pos=sta_pos,
                                    download_size=download_size
                                ):
                                    image_data.extend(data)
                                else:
                                    return logger.error("图片分段下载，返回数据为空")
                            # 验证图片数据
                            try:
                                ImageFile.LOAD_TRUNCATED_IMAGES = True
                                image_bytes = bytes(image_data)
                                Image.open(io.BytesIO(image_bytes))
                            except Exception as e:
                                logger.error(f"验证分段下载的图片数据失败: {e}")
                                # 验证失败，尝试CDN下载
                                if img_aeskey and img_cdnurl:
                                    image_data = await self.api_download_cdn_image(img_aeskey, img_cdnurl)
                        except Exception as e:
                            image_data = await self.api_download_cdn_image(img_aeskey, img_cdnurl)
                    elif img_aeskey and img_cdnurl:
                        image_data = await self.api_download_cdn_image(img_aeskey, img_cdnurl)
                    
                    if image_data is None:
                        return logger.error("图片下载失败，请检查日志文件")
                    
                    if isinstance(image_data, str):
                        image_data = base64.b64decode(image_data)
                    
                    # 判断格式
                    kind = filetype.guess(image_data)
                    ext = kind.extension if kind and kind.mime.startswith("image/") else "jpg"
                    file_name = f"{md5}.{ext}"
                    file_path = TEMP_DIR / file_name
                    try:
                        async with aiofiles.open(file_path, "wb") as f:
                            await f.write(image_data)
                    except Exception as e:
                        return logger.error(f"图片保存失败: {str(e)}")
                else:
                    file_path = TEMP_DIR / file_name
                    ext = file_name.split('.')[-1]
                
                return File(
                    path=file_path,
                    md5=md5,
                    ext=ext,
                    **component_params
                )
            elif msg_type == AddMsgType.VIDEO:
                try:
                    root = ElementTree.fromstring(component_params["content"])
                    if (video_msg := root.find("videomsg")) is None:
                        return logger.error("视频消息解析失败，videomsg字段为空")
                    md5 = video_msg.attrib.get("md5")
                    video_length = video_msg.attrib.get("length")
                except Exception as e:
                    return logger.error(f"视频 XML 解析错误: {str(e)}")
                
                video_data = None
                if (file_name := find_temp_file(md5)) is None:
                    if video_length and video_length.isdigit:
                        data_len = int(video_length)
                        chunk_size = 64 * 1024
                        chunks = math.ceil(data_len / chunk_size)
                        video_data = bytearray()
                        for i in range(chunks):
                            sta_pos = i * chunk_size
                            download_size = min(chunk_size, data_len - sta_pos)
                            if data:= await self.api_download_chunk_video(
                                msg_id=component_params["msg_id"], 
                                to_wxid=common_data["from_wxid"], 
                                data_len=data_len, 
                                sta_pos=sta_pos,
                                download_size=download_size
                            ):
                                video_data.extend(data)
                            else:
                                return logger.error("视频下载失败，返回数据为空")
                    else:
                        return logger.error("视频下载失败：缺少必要参数")
                    
                    if video_data is None:
                        return logger.error("视频数据为空，请检查日志")
                    
                    kind = filetype.guess(video_data)
                    ext = kind.extension if kind and kind.mime.startswith("video/") else "mp4"
                    file_name = f"{md5}.{ext}"
                    file_path = TEMP_DIR / file_name
                    try:
                        async with aiofiles.open(file_path, "wb") as f:
                            await f.write(video_data)
                    except Exception as e:
                        return logger.error(f"视频文件保存失败: {str(e)}")
                else:
                    file_path = TEMP_DIR / file_name
                    ext = file_name.split('.')[-1]
                
                return File(
                    path=file_path,
                    md5=md5,
                    ext=ext,
                    **component_params
                )
            elif msg_type == AddMsgType.SYSTEMMSG:
                pass
            elif msg_type == AddMsgType.APPMSG:
                try:
                    root = ElementTree.fromstring(component_params["content"])
                    if (appmsg := root.find("appmsg")) is None:
                        return logger.error("App消息解析失败，appmsg字段为空")
                    type = int(appmsg.findtext("type"))                    
                    if type == XmlType.QUOTE:
                        title = appmsg.findtext("title")
                        # 去掉at信息，获得纯文本
                        if '\u2005' in title:
                            title = re.sub(r'@[^\u2005]*\u2005', '', title)
                        
                        if (refermsg := appmsg.find("refermsg")) is None:
                            return logger.error("XML 消息未能找到 refermsg")
                        msg_type = int(refermsg.findtext("type"))
                        quote_type = AddMsgType(msg_type)
                        
                        # 需要构造一个extracted_data
                        # 目前支持文本、图片、视频，
                        # 语音消息需要msg_id，但是refermsg只有new_msg_id可能需要数据库查记录
                        # APPMSG比较复杂，后面再说 TODO
                        quote_require = {
                            "msg_type": msg_type,
                            "msg_id": 0,
                            "new_msg_id": refermsg.findtext("svrid"),
                            "msg_seq": 0,
                            "content": refermsg.findtext("content"),
                            "create_time": refermsg.findtext("createtime"),
                        }
                        if quote_type in [AddMsgType.TEXT, AddMsgType.IMAGE, AddMsgType.VIDEO]:
                            return await self.convert_component("AddMessage", quote_require)
                        else:
                            return logger.warning(f"引用类型 {quote_type} 尚未支持")
                    elif type == XmlType.FILE:
                        md5 = appmsg.findtext("md5")
                        appattach = appmsg.find("appattach")
                        if appattach is None:
                            return logger.error("文件附件ID不存在，无法下载文件")
                        
                        file_attachid = appattach.findtext("attachid")
                        ext = appattach.findtext("fileext")
                        
                        # MD5判重
                        file_name = f"{md5}.{ext}"
                        if not (file_path := TEMP_DIR / file_name).exists():
                            base64_str = await self.api_download_file(file_attachid)
                            attach_data = base64.b64decode(base64_str)
                            try:
                                async with aiofiles.open(file_path, "wb") as f:
                                    await f.write(attach_data)
                            except Exception as e:
                                raise Exception(f"附件保存失败: {str(e)}")
                        return File(
                            path=file_path,
                            md5=md5,
                            ext=ext,
                            **component_params
                        )
                    elif type == XmlType.SHARE_LINK:
                        return Link(
                            title=appmsg.findtext('title', '').strip(),
                            desc=appmsg.findtext('des', '').strip(),
                            url=appmsg.findtext('url', '').strip(),
                            username=appmsg.findtext('sourceusername', '').strip(),
                            displayname=appmsg.findtext('sourcedisplayname', '').strip()
                        )
                    elif type == XmlType.UPLOAD:
                        return logger.warning("UPLOAD 类型 AppMessage 未适配")
                    elif type == XmlType.FORWORD:
                        return logger.warning("FORWARD 类型 AppMessage 未适配")
                    else:
                        return logger.warning(f"未识别的 XML 类型:{type}")
                except Exception as e:
                    return logger.error(f"解析xml消息失败: {e}")
            else:
                return logger.warning(f"未知的AddMessage类型: {msg_type}")
        elif type == "ModContact":
            pass


    async def convert_event(self, msg_type: str, common_data: dict, component: MessageComponent) -> MessageEvent:
        """根据消息信息和组件创建事件"""
        if msg_type == "AddMessage":
            event_params = {
                "component": component, 
                "data": common_data["data"]
            }
            
            # 为了和convert_message解耦合，不得不写重复的代码
            msg_type = common_data["msg_type"]
            msg_type_to_event = {
                AddMsgType.TEXT: EventType.TEXT,
                AddMsgType.VOICE: EventType.VOICE,
                AddMsgType.IMAGE: EventType.IMAGE,
                AddMsgType.VIDEO: EventType.VIDEO,
            }
            
            if msg_type in msg_type_to_event:
                event_params["event_type"] = msg_type_to_event[msg_type]
            elif msg_type == AddMsgType.APPMSG:
                # APPMSG类型根据组件类型决定
                component_to_event = {
                    Link: EventType.LINK,
                    File: EventType.FILE,
                    Quote: EventType.QUOTE
                }
                event_params["event_type"] = component_to_event[type(component)]
            else:
                return logger.error("未知的事件类型")
            
            # 设置来源和会话信息
            if common_data["is_chatroom"]:
                event_params["source"] = MessageSource.CHATROOM
                event_params["conversation"] = await self.get_chatroom(common_data["from_wxid"])
                event_params["sender"] = await self.get_chatroom_member(
                    chatroom_id=event_params["conversation"].chatroom_id, 
                    wxid=common_data["sender_wxid"]
                )
                
                # 处理AT信息
                at_members = []
                for at_wxid in common_data["at_wxids"]:
                    member = await self.get_chatroom_member(event_params["conversation"].chatroom_id, at_wxid)
                    if member:
                        at_members.append(member)
                
                event_params["ats"] = at_members
                event_params["is_at"] = any(member.wxid == self.wxid for member in at_members)
            else:
                event_params["source"] = MessageSource.FRIEND
                event_params["conversation"] = event_params["sender"] = await self.get_friend(common_data["from_wxid"])
                event_params["ats"] = []
                event_params["is_at"] = False
            
            # 创建并返回事件
            return MessageEvent(
                adapter_obj=self,
                adapter_cls=self.__class__,
                **event_params
            )
        
        return None


    async def terminate(self):
        pass


    async def alive(self) -> bool:
        """账号判活"""
        return await self.api_heartbeat()