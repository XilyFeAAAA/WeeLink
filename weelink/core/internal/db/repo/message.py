# local library
from weelink.core.internal.db.model import MessageDocument

class MessageRepository:
    
    @staticmethod
    async def add_message(
        *,
        adapter_name: str,
        msg_id: str, 
        new_msg_id: str, 
        data: dict
    ):
        """添加消息记录"""
        if await MessageDocument.find_one({"msg_id": msg_id}):
            raise Exception(f"创建消息失败：msg_id={msg_id} 已存在")
        
        try:
            await MessageDocument(
                adapter_name=adapter_name,
                msg_id=msg_id,
                new_msg_id=new_msg_id,
                data=data
            ).insert()
        except Exception as e:
            raise Exception(f"创建消息失败：{str(e)}")
        
        
        
    @staticmethod
    async def get_message(value: str, key: str = "msg_id") -> dict:
        """读取消息记录"""
        message = await MessageDocument.find_one({key: value})
        return message if message is None else message.data