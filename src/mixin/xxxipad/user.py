from src.utils import post, logger
from src.mixin.base import BaseMixIn
from .constants import URL

class UserMixIn(BaseMixIn):
    
    
    async def get_profile(self) -> dict:
        param = {
             "wxid": self.status.wxid
        }
        resp = await post(f'{URL}/User/GetContractProfile', query=param)        
        logger.debug(resp)
        return resp.get("Data").get("userInfo") if resp.get("Success") else None