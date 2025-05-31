from src import config
from src.utils import get, logger
from src.mixin.base import BaseMixIn
from .constants import URL
import asyncio

class ProtocolMixIn(BaseMixIn):
    
    async def check_protocol(self) -> None:
        """验证 Protocol 是否启动"""
        max_retries = 3
        cnt_retry = 0
        while True:
            logger.warning(f"正在连接协议: {cnt_retry}/{max_retries}")
            try:
                resp = await get(URL, json=False)
                if resp.status in [200, 201, 401, 404]:
                    return logger.info("协议连接成功")
            except Exception as e:
                logger.warning(f"协议连接失败: {e}")
            await asyncio.sleep(5)
            if cnt_retry >= max_retries:
                raise Exception("协议连接超时")
            cnt_retry += 1