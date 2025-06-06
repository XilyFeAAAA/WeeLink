import aiohttp
import asyncio



class Client:
    
    _sessions: dict[str, "Client"] = {}
    _locks: dict[str, asyncio.Lock] = {}
    
    @classmethod
    async def get_instance(cls, session_id: str) -> "Client":
        if session_id not in cls._locks:
            cls._locks[session_id] = asyncio.Lock()
            
        async with cls._locks[session_id]:
            if session_id not in cls._sessions:
                cls._sessions[session_id] = cls()
            return cls._sessions[session_id]

    def __init__(self, key: str) -> None:
        self.conversation_id: str = None
        self.section_id: str = None
        self.key = key
        
    
    def clear_messages(self) -> None:
        """清空聊天记录"""
        self.conversation_id = None
        self.section_id = None

        
    async def post(self, url: str, params=None, payload=None, data=None, headers=None) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, params=params, json=payload, data=data, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"请求失败，状态码: {response.status}: {error_text}")

    async def generate_text(self, text: str):
        raise NotImplementedError
    

    async def generate_video(self):
        raise NotImplementedError
    
    
    async def generate_image(self):
        raise NotImplementedError
    
    
    async def read_document(self):
        raise NotImplementedError
    
    
    async def read_image(self):
        raise NotImplementedError
    
    
    async def check_refresh(self):
        raise NotImplementedError
    
    
class GLMClient(Client):
    
    def __init__(self) -> None:
        super().__init__(key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3MzJhYmMwYTM2OWU0MTkzYWVmMGY3MDZmYWY3YjdmYSIsImV4cCI6MTc2NDM5Nzc0MSwibmJmIjoxNzQ4ODQ1NzQxLCJpYXQiOjE3NDg4NDU3NDEsImp0aSI6IjE5Y2YyNzg5MDgzMjRkNjZiNzI3YWM4Y2JhNDlkNDlhIiwidWlkIjoiNjgzZDQ0NzkzZTFiNGQ5YTAzYzUxYWE2IiwidHlwZSI6InJlZnJlc2gifQ.fdJPz0RPnCi5ZAQG1sNwqOmIn5gy9llU0vkitO37IAw")
        self.baseurl = "http://121.41.2.180:8000"
    
    async def generate_text(self, text: str):
        payload = {
            "model": "glm-4-plus",
            "conversation_id": "683d563d088446cf55d78d92",
            "messages": [
                {
                    "role": "user",
                    "content": text
                }
            ],
            "stream": False
        }
        if self.conversation_id is not None:
            payload["conversation_id"] = self.conversation_id
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.key}"
        }
        resp = await self.post(f"{self.baseurl}/v1/chat/completions", payload=payload, headers=headers)
        if self.conversation_id is None:
            self.conversation_id = resp.get("id")
        
        choices = resp.get("choices", [])
        return choices[0].get("message", {}).get("content") if choices else None
    
    

class DoubaoClient(Client):
    
    
    def __init__(self) -> None:
        super().__init__(key="")
        self.baseurl = "http://192.168.31.195:8000"
        
    async def chat(self, text: str, attachment: dict=None):
        payload = {
            "prompt": text,            
        }
        if self.conversation_id and self.section_id:
            payload["conversation_id"] = self.conversation_id
            payload["section_id"] = self.section_id
        if attachment:
            payload["attachments"] = [attachment]
        
        resp = await self.post(f"{self.baseurl}/api/chat/completions", payload=payload)
        self.conversation_id = resp.get("conversation_id")
        self.section_id = resp.get("section_id")
        
        return resp
    
    
    async def upload_file(self, ftype: int, fname: str, fdata: bytes):
        """上传文件"""
        params = {
            "file_type": ftype,
            "file_name": fname,
        }
        headers = {'Content-Type': 'application/octet-stream'}
        return await self.post(url=f"{self.baseurl}/api/file/upload", params=params, data=fdata, headers=headers)
    
    
    async def del_conversation(self):
        """清理聊天室"""
        resp = await self.post(f"{self.baseurl}/api/chat/delete?conversation_id={self.conversation_id}", payload=None)
        if not resp.get("ok"):
            raise Exception(f"删除失败: {resp.get('msg', '未知错误')}")
    
    
    @classmethod
    async def cleanup(cls):
        for client in cls._sessions.values():
            await client.del_conversation()