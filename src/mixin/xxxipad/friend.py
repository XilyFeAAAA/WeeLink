from src.utils.http import post
from .constants import URL

class FriendMixIn:

                
    async def get_range_friends(self, wx_seq: int, chatroom_seq: int):
        param = {
            "CurrentChatRoomContactSeq": chatroom_seq,
            "CurrentWxcontactSeq": wx_seq,
            "Wxid": self.status.wxid
        }
        resp = await post(f"{URL}/Friend/GetContractList", body=param)
        if resp.get("Success"):
            return resp.get("Data")
        else:
            raise Exception(f"get_range_friends 接口错误")
     
    async def get_friends(self) -> list[str]:
        id_list = []
        wx_seq, chatroom_seq = 0, 0
        while True:
            contact_list = await self.get_range_friends(wx_seq, chatroom_seq)
            id_list.extend(contact_list["ContactUsernameList"])
            wx_seq, chatroom_seq = contact_list["CurrentWxcontactSeq"], contact_list["CurrentChatRoomContactSeq"]
            if contact_list["CountinueFlag"] != 1:
                break
        return id_list
        
    async def get_friend_info(self, to_wxid: str) -> list[dict]:
        param = {
            "ChatRoom": "",
            "Towxids": to_wxid,
            "Wxid": self.status.wxid
        }
        resp = await post(f"{URL}/Friend/GetContractDetail", body=param)
        if resp.get("Success"):
            return resp.get("Data").get("ContactList")
        else:
            raise Exception(f"get_friend_info 接口错误")
        