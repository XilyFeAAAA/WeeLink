# standard library
import json
import asyncio
from typing import AsyncGenerator


# local library
from weelink.core.utils.logger import logger


class SSEManager:
    
    def __init__(self) -> None:
        self.queue = asyncio.Queue()
    
    
    def cleanup(self):
        """清理SSE流"""
        if self.queue is None:
            return
        while not self.queue.empty():
            try:
                self.queue.get_nowait()
            except asyncio.QueueEmpty:
                return
    
    
    def _format_sse_message(self, type: str, data: dict | list | str) -> str:
        """格式化SSE消息"""
        if isinstance(data, (list, dict)):
            data_str = json.dumps(data)
        else:
            data_str = str(data)
        
        return f"event: {type}\ndata: {data_str}\n\n"
    
    
    def send_message(self, type: str, msg: dict | list | str):
        """向SSE流发送消息"""
        try:
            self.queue.put_nowait((type, msg))
        except Exception as e:
            logger.error(f"SSE流发送消息失败: {e}")
            self.cleanup()
    
    
    async def stream(self) -> AsyncGenerator[str, None]:
        """获取客户端的SSE数据流"""
        if self.queue is None:
            return
        
        try:
            yield self._format_sse_message("connected", {
                "message": "SSE流连接成功"
            })
            
            while True:
                try:
                    type, message = await asyncio.wait_for(self.queue.get(), timeout=30.0)
                    sse_msg = self._format_sse_message(type, message)
                    yield sse_msg
                except asyncio.TimeoutError:
                    yield self._format_sse_message("heartbeat", {
                        "timestamp": asyncio.get_event_loop().time()
                    })
                except Exception as e:
                    logger.error(f"SSE流处理错误: {e}")
                    break
            
            yield self._format_sse_message("disconnected", {
                "message": "SSE流结束"
            })
        except Exception as e:
            logger.error(f"SSE流连接错误: {e}")
        finally:
            self.cleanup()


sse_manager = SSEManager()