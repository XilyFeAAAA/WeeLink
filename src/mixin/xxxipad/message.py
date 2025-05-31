from src.utils import post, logger
from .constants import URL
import asyncio


class MessageMixIn:
    
    def __init__(self):
        # 避免循环引用
        from src.event.queue import MessageQueue
        self.queue = MessageQueue.get_instance()
    

    # @BaseMixIn.require_login
    async def sync_message(self):
        param = {
            "Wxid": self.status.wxid,
            "Scene": 0,
            "Synckey": ""
        }
        resp = await post(f"{URL}/Msg/Sync", body=param)
        if resp.get("Success", False):
            return True, resp.get("Data")
        else:
            return False, resp.get("Message")

    async def send_text(self, to_wxid: str, content: str, at: str = "", type_: int = 1):
        """调用消息队列"""
        
        self.queue.add_message(self._send_text, to_wxid, content, at, type_)

    async def _send_text(self, to_wxid: str, content: str, at: str = "", type_: int = 1):
        """发送文本消息，type=1文本，at为@人wxid，多个用,隔开"""
        param = {
            "ToWxid": to_wxid,
            "Content": content,
            "At": at,
            "Type": type_,
            "Wxid": self.status.wxid
        }
        resp = await post(f"{URL}/Msg/SendTxt", body=param)
        if resp.get("Success"):
            return resp.get("Data")
        else:
            raise Exception(f"_send_text 接口错误")

    async def _send_image(self, to_wxid: str, base64: str):
        """发送图片消息，base64为图片内容"""
        param = {
            "ToWxid": to_wxid,
            "Base64": base64,
            "Wxid": self.status.wxid
        }
        resp = await post(f"{URL}/Msg/UploadImg", body=param)
        if resp.get("Success"):
            return resp.get("Data")
        else:
            raise Exception(f"_send_image 接口错误")

    # async def send_voice(self, to_wxid: str, base64: str, type_: int, voice_time: int):
    #     """发送语音消息，type为音频类型，voice_time为时长(毫秒)"""
    #     param = {
    #         "ToWxid": to_wxid,
    #         "Base64": base64,
    #         "Type": type_,
    #         "VoiceTime": voice_time,
    #         "Wxid": self.status.wxid
    #     }
    #     resp = await post(f"{URL}/Msg/SendVoice", body=param)
    #     if resp.get("Success"):
    #         return resp.get("Data")
    #     else:
    #         self.error_handler(resp)

    # async def send_video(self, to_wxid: str, base64: str, image_base64: str, play_length: int):
    #     """发送视频消息，base64为视频内容，image_base64为封面，play_length为时长(秒)"""
    #     param = {
    #         "ToWxid": to_wxid,
    #         "Base64": base64,
    #         "ImageBase64": image_base64,
    #         "PlayLength": play_length,
    #         "Wxid": self.status.wxid
    #     }
    #     resp = await post(f"{URL}/Msg/SendVideo", body=param)
    #     if resp.get("Success"):
    #         return resp.get("Data")
    #     else:
    #         self.error_handler(resp)

    # async def share_card(self, to_wxid: str, card_wxid: str, card_nickname: str, card_alias: str):
    #     """分享名片"""
    #     param = {
    #         "ToWxid": to_wxid,
    #         "CardWxId": card_wxid,
    #         "CardNickName": card_nickname,
    #         "CardAlias": card_alias,
    #         "Wxid": self.status.wxid
    #     }
    #     resp = await post(f"{URL}/Msg/ShareCard", body=param)
    #     if resp.get("Success"):
    #         return resp.get("Data")
    #     else:
    #         self.error_handler(resp)

    async def send_link(self, to_wxid: str, title: str, desc: str, url: str, thumb_url: str):
        self.queue.add_message(self._send_link, to_wxid, title, desc, url, thumb_url)

    async def _send_link(self, to_wxid: str, title: str, desc: str, url: str, thumb_url: str):
        """发送分享链接消息"""
        param = {
            "ToWxid": to_wxid,
            "Title": title,
            "Desc": desc,
            "Url": url,
            "ThumbUrl": thumb_url,
            "Wxid": self.status.wxid
        }
        resp = await post(f"{URL}/Msg/ShareLink", body=param)
        logger.debug(resp)
        if resp.get("Success"):
            return resp.get("Data")
        else:
            raise Exception(f"_send_link 接口错误")

    async def _revoke(self, client_msg_id: int, create_time: int, new_msg_id: int, to_user_name: str):
        """撤回消息"""
        param = {
            "ClientMsgId": client_msg_id,
            "CreateTime": create_time,
            "NewMsgId": new_msg_id,
            "ToUserName": to_user_name,
            "Wxid": self.status.wxid
        }
        resp = await post(f"{URL}/Msg/Revoke", body=param)
        if resp.get("Success"):
            return resp.get("Data")
        else:
            raise Exception(f"_revoke 接口错误")
            

    async def send_app(self, to_wxid: str, xml: str, type: int):
        """调用消息队列"""
        self.queue.add_message(self._send_app,  to_wxid, xml, type)


    async def _send_app(self, to_wxid: str, xml: str, type: int) -> tuple[int, int, int]:
        """发送app消息"""
        param = {
            "Wxid": self.status.wxid, 
            "ToWxid": to_wxid, 
            "Xml": xml, 
            "Type": type
        }
        resp = await post(f"{URL}/Msg/SendApp", body=param)
        logger.debug(resp)
        if resp.get("Success") and (data := resp.get("Data", {})):
            logger.info(f"发送app消息: 对方wxid:{to_wxid} 类型:{type} ")
            return data.get("clientMsgId"), data.get("createTime"), data.get("newMsgId")
        else:
            raise Exception(f"_send_app 接口错误")
            
    async def message_generator(self):
        """消息处理循环，作为生成器返回消息数据"""
        while True:
            status, data = await self.sync_message()
            if status:
                yield data
            else:
                yield None
            await asyncio.sleep(0.5)

            
