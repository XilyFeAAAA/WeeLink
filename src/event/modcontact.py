from src.model import Chatroom, ChatroomMember, ModContactType, DataType, Friend
from src.manager import cache
from src.utils import logger

class ModContact:
    _type_registry: dict = {}

    def __init__(self,
                *, 
                data: dict,
                username: str,
                nickname: str,
                pyinitial: str,
                quanpin: str,
                bitmask: int,
                bitval: int,
                imgflag: int,
                chatroom_notify: int,
                chatroom_owner_wxid: str,
                chatroom_status: int,
                small_head_imgurl: str,
                description: str,
                chatroom: Chatroom,
                friend: Friend):
        self.data = data
        self.username = username
        self.nickname = nickname
        self.pyinitial = pyinitial
        self.quanpin = quanpin
        self.bitmask = bitmask
        self.bitval = bitval
        self.imgflag = imgflag
        self.chatroom_notify = chatroom_notify
        self.chatroom_owner_wxid = chatroom_owner_wxid
        self.chatroom_status = chatroom_status
        self.small_head_imgurl = small_head_imgurl
        self.description = description
        self.modcontact_type = None
        self.chatroom = chatroom
        self.friend = friend
        # 数据类型
        self.type = DataType.MODCONTACTS


    @classmethod
    async def new(cls, data: dict) -> "ModContact":
        # 处理通用信息
        username = data.get("UserName", {}).get("string")
        nickname = data.get("NickName", {}).get("string")
        pyinitial = data.get("PyInitial", {}).get("string")
        quanpin = data.get("QuanPin", {}).get("string")
        bitmask = data.get("BitMask")
        bitval = data.get("BitVal")
        imgflag = data.get("ImgFlag")
        chatroom_notify = data.get("ChatRoomNotify")
        chatroom_owner_wxid = data.get("ChatRoomOwner")
        small_head_imgurl = data.get("SmallHeadImgUrl")
        chatroom_status = data.get("ChatroomMaxCount")
        description = data.get("Description")
        # 群聊 or 私聊判断
        if username.endswith("@chatroom"):
            # 判断cache是否存在信息
            if await cache.chatroom.exist(username):
                past = await cache.chatroom.get(username)
                cur = await cache.chatroom.update(username)
                cls = ChatroomModify(
                    data=data,
                    username=username,
                    nickname=nickname,
                    pyinitial=pyinitial,
                    quanpin=quanpin,
                    bitmask=bitmask,
                    bitval=bitval,
                    imgflag=imgflag,
                    chatroom_notify=chatroom_notify,
                    chatroom_owner_wxid=chatroom_owner_wxid,
                    chatroom_status=chatroom_status,
                    small_head_imgurl=small_head_imgurl,
                    description=description,
                    chatroom=cur,
                    friend=None)
                return await cls.parse(past, cur)
            else:
                # 如果没有缓存则更新
                await cache.chatroom.update(username)
        else:
            # 更新好友信息
            if await cache.friend.exist(username):
                return logger.warning("未适配ModContact - Friend")
                #  return FriendModify(
                #     data=data,
                #     username=username,
                #     nickname=nickname,
                #     pyinitial=pyinitial,
                #     quanpin=quanpin,
                #     bitmask=bitmask,
                #     bitval=bitval,
                #     imgflag=imgflag,
                #     chatroom_notify=chatroom_notify,
                #     chatroom_owner_wxid=chatroom_owner_wxid,
                #     chatroom_status=chatroom_status,
                #     small_head_imgurl=small_head_imgurl,
                #     description=description)
            else:
                await cache.friend.update(username)
        return
        

class ChatroomModify(ModContact):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.decreased_members: list[ChatroomMember] = []
        self.increased_members: list[ChatroomMember] = []
        
    async def parse(self, past_chatroom: Chatroom, cur_chatroom: Chatroom) -> "ChatroomModify":
        """检查群聊变动"""
        # 检查群名称变更
        if past_chatroom.nickname != cur_chatroom.nickname:
            self.modcontact_type = ModContactType.NICKNAME_CHANGED
        # 检查群备注变更
        elif past_chatroom.remark != cur_chatroom.remark:
            self.modcontact_type = ModContactType.REMARK_CHANGED
        # 检查群主变更
        elif past_chatroom.chatroom_owner != cur_chatroom.chatroom_owner:
            self.modcontact_type = ModContactType.OWNER_CHANGED
        else:
            # 检查成员变动
            past_member_ids = {member.wxid for member in past_chatroom.member_list}
            cur_member_ids = {member.wxid for member in cur_chatroom.member_list}
            
            if decreased_ids := (past_member_ids - cur_member_ids):
                self.modcontact_type = ModContactType.MEMBER_DECREASED
                self.decreased_members = [member for member in past_chatroom.member_list 
                                        if member.wxid in decreased_ids]
            elif increased_ids := (cur_member_ids - past_member_ids):
                self.modcontact_type = ModContactType.MEMBER_INCREASED
                self.increased_members = [member for member in cur_chatroom.member_list 
                                        if member.wxid in increased_ids]
            else:
                return None
        
        return self

        
        
        
class FriendModify(ModContact):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)