# standard library
import qrcode
import base64
import asyncio
import functools

# local library
from weelink.core.utils import post, logger
from weelink.core.message import Chatroom, Friend, ChatroomMember
from weelink.core.internal.cache import cache

def require_login(func):
    @functools.wraps(func)
    async def wrapper(self, *args, **kwargs):
        if not self.is_logged:
            raise ValueError(f"登录状态下才能调用API {func.__name__}")
        return await func(self, *args, **kwargs)
    return wrapper


class ApiMixin:

    """登录相关"""

    async def api_login(self):
        if (profile := await self.api_get_profile()) is None:
            if await self.api_get_cached_info():
                logger.debug("尝试二次登录")
                if not await self.api_twice_login():
                    logger.debug("尝试唤醒登录...")
                    if not await self.api_revoke_login(self.device_name):
                        logger.debug("尝试二维码登录...")
                        await self.api_qrcode_login(self.device_name, self.device_id)
            else:
                await self.api_qrcode_login(self.device_name, self.device_id)
        else:
            self.nickname = profile.get("NickName", {}).get("string", "")
            self.alias = profile.get("Alias", "")
            self.phone = profile.get("BindMobile", {}).get("string", "")
        logger.info(f"设备登录成功: 微信号: {self.wxid}  昵称: {self.nickname} 手机号: {self.phone}")     


    async def api_get_cached_info(self):
        param = {
            "wxid": self.wxid
        }
        resp = await post(f"{self.base_url}/Login/GetCacheInfo", query=param)
        return resp.get("Data") if resp.get("Success") else None


    async def api_twice_login(self):
        param = {
            "wxid": self.wxid
        }
        resp = await post(f"{self.base_url}/Login/TwiceAutoAuth", body=param)
        if resp.get("Success"):
            return resp.get("Data") 
        else :
            return logger.error(f"二次登录失败: {resp.get('Message', '未知错误')}")


    async def api_revoke_login(self, device_name: str):
        param = {
            "OS": device_name or "iPad",
            "Proxy": {
                "ProxyIp": "",
                "ProxyPassword": "",
                "ProxyUser": ""
            },
            "Url": "",
            "Wxid": self.wxid
        }
        resp = await post(f"{self.base_url}/Login/Awaken", body=param)
        if resp.get("Success"):
            logger.success(f"唤醒登录成功...")
            return True
        else:
            logger.error(f"唤醒登录失败: {resp.get('Message', '未知错误')}")
            return False


    async def api_qrcode_login(self, device_name: str, device_id: str):
        param = {
            'DeviceName': device_name,
            'DeviceID': device_id
        }
        resp = await post(f"{self.base_url}/Login/GetQR", body=param)
        if resp.get("Success"):
            qr = qrcode.QRCode(
                        version=1,
                        error_correction=qrcode.constants.ERROR_CORRECT_L,
                        box_size=10,
                        border=4,
            )
            qr.add_data(f'http://weixin.qq.com/x/{resp.get("Data").get("Uuid")}')
            qr.make(fit=True)
            qr.print_ascii()
            uuid, url = resp.get("Data").get("Uuid"), resp.get("Data").get("QrUrl")
            logger.info(f"登录uuid: {uuid}, 二维码url: {url}")
        else:
            raise Exception(f"qrcode_login 接口错误, 返回结果{resp}")

        
        while True:
            stat, data = await self.api_check_login(uuid)
            if stat: break
            logger.info(f"等待登录中，过期倒计时：{data}")
            await asyncio.sleep(5)

        self.wxid = data.get("userName")
        self.nickname = data.get("nickName")
        self.alias = data.get("alias")
        self.phone = data.get("bindMobile")


    async def api_check_login(self, uuid: str):
        param = {
            "uuid": uuid
        }
        resp = await post(f"{self.base_url}/Login/CheckQR", query=param)
        if resp.get("Success"):
            if resp.get("Data").get("acctSectResp", ""):
                return True, resp.get("Data").get("acctSectResp")
            else:
                return False, resp.get("Data").get("expiredTime")
        else:
            raise Exception(f"check_login 接口错误")


    async def api_start_auto_heartbeat(self):
        param = {
            "wxid": self.wxid
        }
        resp = await post(f"{self.base_url}/Login/HeartBeatLong", query=param)
        if resp.get("Success"):
            logger.success("已开启自动心跳")
        else:
            logger.error(f"开启自动心跳失败: {resp}")


    async def api_heartbeat(self):
        param = {
            "wxid": self.wxid
        }
        resp = await post(f"{self.base_url}/Login/HeartBeat", query=param)
        return resp.get("Success", False)


    """消息相关"""

    @require_login
    async def api_sync_message(self):
        param = {
            "Wxid": self.wxid,
            "Scene": 0,
            "Synckey": ""
        }
        resp = await post(f"{self.base_url}/Msg/Sync", body=param)
        if resp.get("Success", False):
            return True, resp.get("Data")
        else:
            return False, resp.get("Message")


    @require_login
    async def api_send_text(self, to_wxid: str, content: str, at: str = "", type: int = 1):
        """发送文本消息，type=1文本，at为@人wxid，多个用,隔开"""
        param = {
            "ToWxid": to_wxid,
            "Content": content,
            "At": at,
            "Type": type,
            "Wxid": self.wxid
        }
        resp = await post(f"{self.base_url}/Msg/SendTxt", body=param)
        if resp.get("Success"):
            return resp.get("Data")
        else:
            raise Exception(f"send_text 接口错误")


    @require_login
    async def api_send_image(self, to_wxid: str, base64: str):
        """发送图片消息，base64为图片内容"""
        param = {
            "ToWxid": to_wxid,
            "Base64": base64,
            "Wxid": self.wxid
        }
        resp = await post(f"{self.base_url}/Msg/UploadImg", body=param)
        if resp.get("Success"):
            return resp.get("Data")
        else:
            raise Exception(f"send_image 接口错误")


    @require_login
    async def api_send_voice(self, to_wxid: str, base64: str, type: int, voice_time: int):
        """发送语音消息，type为音频类型，voice_time为时长(毫秒)"""
        param = {
            "ToWxid": to_wxid,
            "Base64": base64,
            "Type": type,
            "VoiceTime": voice_time,
            "Wxid": self.wxid
        }
        resp = await post(f"{self.base_url}/Msg/SendVoice", body=param)
        if resp.get("Success"):
            return resp.get("Data")
        else:
            raise Exception(f"send_image 接口错误")


    @require_login
    async def api_send_video(self, to_wxid: str, base64: str, image_base64: str, play_length: int):
        """发送视频消息，base64为视频内容，image_base64为封面，play_length为时长(秒)"""
        param = {
            "ToWxid": to_wxid,
            "Base64": base64,
            "ImageBase64": image_base64,
            "PlayLength": play_length,
            "Wxid": self.wxid
        }
        resp = await post(f"{self.base_url}/Msg/SendVideo", body=param)
        if resp.get("Success"):
            return resp.get("Data")
        else:
            raise Exception(f"send_video 接口错误")


    @require_login
    async def api_share_card(self, to_wxid: str, card_wxid: str, card_nickname: str, card_alias: str):
        """分享名片"""
        param = {
            "ToWxid": to_wxid,
            "CardWxId": card_wxid,
            "CardNickName": card_nickname,
            "CardAlias": card_alias,
            "Wxid": self.wxid
        }
        resp = await post(f"{self.base_url}/Msg/ShareCard", body=param)
        if resp.get("Success"):
            return resp.get("Data")
        else:
            raise Exception(f"share_card 接口错误")


    @require_login
    async def api_send_link(self, to_wxid: str, title: str, desc: str, url: str, thumb_url: str):
        """发送分享链接消息"""
        param = {
            "ToWxid": to_wxid,
            "Title": title,
            "Desc": desc,
            "Url": url,
            "ThumbUrl": thumb_url,
            "Wxid": self.wxid
        }
        resp = await post(f"{self.base_url}/Msg/ShareLink", body=param)
        if resp.get("Success"):
            return resp.get("Data")
        else:
            raise Exception(f"send_link 接口错误")


    @require_login
    async def api_revoke_message(self, client_msg_id: int, create_time: int, new_msg_id: int, to_user_name: str):
        """撤回消息"""
        param = {
            "ClientMsgId": client_msg_id,
            "CreateTime": create_time,
            "NewMsgId": new_msg_id,
            "ToUserName": to_user_name,
            "Wxid": self.wxid
        }
        resp = await post(f"{self.base_url}/Msg/Revoke", body=param)
        if resp.get("Success"):
            return resp.get("Data")
        else:
            raise Exception(f"revoke_message 接口错误")


    @require_login
    async def api_send_app(self, to_wxid: str, xml: str, type: int) -> tuple[int, int, int]:
        """发送app消息"""
        param = {
            "Wxid": self.wxid, 
            "ToWxid": to_wxid, 
            "Xml": xml, 
            "Type": type
        }
        resp = await post(f"{self.base_url}/Msg/SendApp", body=param)
        if resp.get("Success") and (data := resp.get("Data", {})):
            return data.get("clientMsgId"), data.get("createTime"), data.get("newMsgId")
        else:
            raise Exception(f"send_app 接口错误")

    """工具相关"""

    @require_login
    async def api_download_chunk_image(self, msg_id: str, to_wxid: str, 
                    data_len: int, sta_pos: int, download_size: int) -> bytes:
        """分段下载图片"""
        param = {
            "Wxid": self.wxid,
            "ToWxid": to_wxid,
            "MsgId": int(msg_id),
            "DataLen": data_len,
            "CompressType": 0,
            "Section": {
                "StartPos": sta_pos,
                "DataLen": download_size
            }
        }
        resp = await post(f"{self.base_url}/Tools/DownloadImg", body=param)
        if resp.get("Success", False):
            # 尝试从不同的响应格式中获取图片数据
            data = resp.get("Data")
            if isinstance(data, dict):
                # 如果是字典，尝试获取buffer字段
                if data.get("ret", -1) != 0:
                    raise Exception(data.get("errMsg", {}).get("string", "未知错误"))
                if "buffer" in data:
                    return base64.b64decode(data["buffer"])
                elif "data" in data and isinstance(data["data"], dict) and "buffer" in data["data"]:
                    return base64.b64decode(data["data"]["buffer"])
                else:
                    # 如果没有buffer字段，尝试直接解码整个data
                    try:
                        return base64.b64decode(str(data))
                    except:
                        logger.error(f"无法解析图片数据字典: {data}")
            elif isinstance(data, str):
                # 如果是字符串，直接解码
                try:
                    return base64.b64decode(data)
                except:
                    logger.error(f"无法解析图片数据字符串: {data[:100]}...")
            else:
                logger.error(f"无法解析图片数据类型: {type(data)}")
        else:
            return None


    @require_login
    async def api_download_cdn_image(self, aeskey: str, cdnmidimgurl: str) -> str:
        """CDN下载图片"""
        param = {
            "Wxid": self.wxid, 
            "FileAesKey": aeskey, 
            "FileNo": cdnmidimgurl
        }
        resp = await post(f"{self.base_url}/Tools/CdnDownloadImage", body=param)
        if resp.get("Success", False):
            return resp.get("Data").get("Image")
        else:
            raise Exception(f"download_cdn_image 接口错误")


    @require_login
    async def api_download_voice(self, msg_id: str, voiceurl: str, length: int) -> str:
        """下载语音文件"""
        param = {
            "Wxid": self.wxid, 
            "MsgId": msg_id, 
            "Voiceurl": voiceurl, 
            "Length": length
        }
        resp = await post(f"{self.base_url}/Tools/DownloadVoice", body=param)
        if resp.get("Success", False):
            return resp.get("Data", {}).get("data", {}).get("buffer")
        else:
            raise Exception(f"download_voice 接口错误")


    @require_login
    async def api_download_file(self, attach_id: str) -> dict:
        """下载附件"""
        param = {
            "Wxid": self.wxid,
            "AttachId": attach_id
        }
        resp = await post(f"{self.base_url}/Tools/DownloadFile", body=param)
        if resp.get("Success", False):
            return resp.get("Data", {}).get("data", {}).get("buffer")
        else:
            raise Exception(f"download_attach 接口错误")


    @require_login
    async def api_download_chunk_video(self, msg_id: str, to_wxid: str, 
                                data_len: int, sta_pos: int, download_size: int) -> str:
        """下载视频"""
        param = {
            "CompressType": 0,
            "DataLen": data_len,
            "MsgId": msg_id,
            "Section": {
                "DataLen": download_size,
                "StartPos": sta_pos
            },
            "ToWxid": to_wxid,
            "Wxid": self.wxid
        }
        resp = await post(f"{self.base_url}/Tools/DownloadVideo", body=param)
        if resp.get("Success", False):
            # 尝试从不同的响应格式中获取图片数据
            data = resp.get("Data")
            if isinstance(data, dict):
                # 如果是字典，尝试获取buffer字段
                if "buffer" in data:
                    return base64.b64decode(data["buffer"])
                elif "data" in data and isinstance(data["data"], dict) and "buffer" in data["data"]:
                    return base64.b64decode(data["data"]["buffer"])
                else:
                    # 如果没有buffer字段，尝试直接解码整个data
                    try:
                        return base64.b64decode(str(data))
                    except:
                        logger.error(f"无法解析图片数据字典: {data}")
            elif isinstance(data, str):
                # 如果是字符串，直接解码
                try:
                    return base64.b64decode(data)
                except:
                    logger.error(f"无法解析图片数据字符串: {data[:100]}...")
            else:
                logger.error(f"无法解析图片数据类型: {type(data)}")
        else:
            return None


    @require_login
    async def api_set_step(self, count: int) -> bool:
        """设置步数"""
        param = {
            "Wxid": self.wxid, 
            "StepCount": count
        }
        resp = await post(f"{self.base_url}/Tools/SetStep", body=param)
        if resp.get("Success", False):
            return True
        else:
            raise Exception(f"set_step 接口错误")

    """账户相关"""
    
    async def api_get_profile(self) -> dict:
        param = {
            "wxid": self.wxid
        }
        resp = await post(f'{self.base_url}/User/GetContractProfile', query=param)
        return resp.get("Data").get("userInfo") if resp.get("Success") else None

    """好友相关"""

    @require_login
    async def api_get_range_friends(self, wx_seq: int, chatroom_seq: int):
        param = {
            "CurrentChatRoomContactSeq": chatroom_seq,
            "CurrentWxcontactSeq": wx_seq,
            "Wxid": self.wxid
        }
        resp = await post(f"{self.base_url}/Friend/GetContractList", body=param)
        if resp.get("Success"):
            return resp.get("Data")
        else:
            raise Exception(f"get_range_friends 接口错误")


    @require_login
    async def api_get_friends(self) -> list[str]:
        id_list = []
        wx_seq, chatroom_seq = 0, 0
        while True:
            contact_list = await self.api_get_range_friends(wx_seq, chatroom_seq)
            id_list.extend(contact_list["ContactUsernameList"])
            wx_seq, chatroom_seq = contact_list["CurrentWxcontactSeq"], contact_list["CurrentChatRoomContactSeq"]
            if contact_list["CountinueFlag"] != 1:
                break
        return id_list


    @require_login
    async def api_get_friend_info(self, to_wxid: str) -> list[dict]:
        param = {
            "ChatRoom": "",
            "Towxids": to_wxid,
            "Wxid": self.wxid
        }
        resp = await post(f"{self.base_url}/Friend/GetContractDetail", body=param)
        if resp.get("Success"):
            return resp.get("Data").get("ContactList")
        else:
            raise Exception(f"get_friend_info 接口错误")

    """群聊相关"""
    
    @require_login
    async def api_get_chatroom_info(self, chatroom_id: str):
        """获取群详情(不带公告内容)"""
        param = {
            "QID": chatroom_id,
            "Wxid": self.wxid
        }
        resp = await post(f"{self.base_url}/Group/GetChatRoomInfo", body=param)
        return resp.get("Data") if resp.get("Success") else None


    @require_login
    async def api_get_chatroom_member(self, chatroom_id: str):
        """获取群成员"""
        param = {
            "QID": chatroom_id,
            "Wxid": self.wxid
        }
        resp = await post(f"{self.base_url}/Group/GetChatRoomMemberDetail", body=param)
        return resp.get("Data", {}).get("NewChatroomData", {}).get("ChatRoomMember", []) if resp.get("Success") else []
    
    """二次API"""
    
    async def get_chatroom(self, chatroom_id: str) -> Chatroom:
        if chatroom := await cache.get(cache_key=chatroom_id):
            return chatroom
        resp = await self.api_get_chatroom_info(chatroom_id)
        member_list = await self.api_get_chatroom_member(chatroom_id)
        if resp is None:
            raise RuntimeError(f"获取群聊{chatroom_id}信息失败: get_chatroom_info接口返回null")
        elif resp.get("ContactCount", 0) != 1:
            raise RuntimeError(f"获取群聊{chatroom_id}信息失败: ContactCount != 1")
        else:
            # 因为每次都只查询一个群聊，所以取[0]
            chatroom = resp.get("ContactList", [])[0]
            return await cache.set(
                cache_key=chatroom_id,
                cache_data=Chatroom(
                    chatroom_id=chatroom.get("UserName", {}).get("string", ""),
                    nickname=chatroom.get("NickName", {}).get("string", ""),
                    remark=chatroom.get("Remark", {}).get("string", ""),
                    chatroom_owner=chatroom.get("ChatRoomOwner", ""),
                    small_image=chatroom.get("SmallHeadImgUrl", ""),
                    member_list=[ChatroomMember(
                        wxid=member.get("UserName", ""),
                        nickname=member.get("NickName", ""),
                        invite_wxid=member.get("InviterUserName", ""),
                        displayname=member.get("DisplayName", ""),
                        big_image=member.get("BigHeadImgUrl", ""),
                        small_image=member.get("SmallHeadImgUrl", "")
                    ) for member in member_list]
                )
        )
    
    
    async def get_chatroom_member(self, chatroom_id: str, wxid: str) -> ChatroomMember:
        chatroom = await self.get_chatroom(chatroom_id)
        return next((member for member in chatroom.member_list if member.wxid == wxid), None)
    
    
    async def get_friend(self, wxid: str) -> Friend:
        if friend := await cache.get(wxid):
            return friend
        if len(friends := await self.api_get_friend_info(wxid)) != 1: 
            raise RuntimeError(f"获取好友信息失败，错误提示:返回联系人数量为{len(friends)}")
        friend = friends[0]
        return await cache.set(
            cache_key=wxid,
            cache_data=Friend(
                wxid=wxid,
                nickname=friend.get("UserName", {}).get("string"),
                avatar=friend.get("BigHeadImgUrl") or friends.get("SmallHeadImgUrl"),
                remark=friend.get("Remark", {}).get("string"),
                alias=friend.get("Alias"),
            )
        )