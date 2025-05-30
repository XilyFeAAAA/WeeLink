from src.utils.http import post
from src.mixin.base import BaseMixIn
from .constants import URL

class ChatroomMixIn(BaseMixIn):
    
    async def get_chatroom_info(self, chatroom_id: str):
        """获取群详情(不带公告内容)"""
        param = {
            "QID": chatroom_id,
            "Wxid": self.status.wxid
        }
        resp = await post(f"{URL}/Group/GetChatRoomInfo", body=param)
        return resp.get("Data") if resp.get("Success") else None



    async def get_chatroom_member(self, chatroom_id: str):
        """获取群成员"""
        param = {
            "QID": chatroom_id,
            "Wxid": self.status.wxid
        }
        resp = await post(f"{URL}/Group/GetChatRoomMemberDetail", body=param)
        return resp.get("Data", {}).get("NewChatroomData", {}).get("ChatRoomMember", []) if resp.get("Success") else []
    
