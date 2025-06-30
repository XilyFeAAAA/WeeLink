# local library
from weelink.core.internal.db.model import MessageDocument

class MessageRepository:
    
    @staticmethod
    async def add_message(
        *,
        adapter_name: str,
        source: str,
        content: str,
        fromname: str,
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
                source=source,
                content=content,
                fromname=fromname,
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
    
    @staticmethod
    async def find_messages(
        page: int = 1,
        limit: int = 20,
        adapter_name: str = None,
        source: str = None,
        content: str = None
    ) -> dict:
        query = {}

        if adapter_name:
            query["adapter_name"] = adapter_name
        if source:
            query["source"] = source
        if content:
            # 假设data字段中有msg键
            query["content"] = {"$regex": content}

        skip = (page - 1) * limit
        cursor = MessageDocument.find(query)
        total = await MessageDocument.find(query).count()
        items = await cursor.skip(skip).limit(limit).to_list()

        return {
            "total": total,
            "page": page,
            "limit": limit,
            "items": [{
                "msg_id": item.msg_id,
                "adapter_name": item.adapter_name,
                "source": item.source,
                "content": item.content,
                "fromname": item.fromname,
                "create_time": item.data["CreateTime"]
                } for item in items]
        }