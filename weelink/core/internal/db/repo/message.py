from weelink.core.internal.db.model import MessageDocument

class MessageRepository:
    
    @staticmethod
    async def add_message(message):
        """添加消息记录"""
        if await MessageDocument.find_one({"msg_id": message.msg_id}):
            raise Exception(f"创建消息失败：msg_id={message.msg_id} 已存在")
        
        msg = MessageDocument(
            msg_id=message.msg_id,
            new_msg_id=message.new_msg_id,
            data=message.data
        )
        try:
            await msg.insert()
        except Exception as e:
            raise Exception(f"创建消息失败：{str(e)}")
        
        
        
    @staticmethod
    async def get_message(value: str, key: str = "msg_id") -> dict:
        """读取消息记录"""
        message = await MessageDocument.find_one({key: value})
        return message if message is None else message.data