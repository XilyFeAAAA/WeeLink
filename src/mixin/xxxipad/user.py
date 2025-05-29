from src.utils import post, logger
from src.mixin.base import BaseMixIn
from .constants import URL

class UserMixIn(BaseMixIn):
    
    
    async def get_profile(self) -> dict:
        param = {
             "wxid": self.wxid
        }
        resp = await post(f'{URL}/User/GetContractProfile', query=param)        
        logger.debug(resp)
        if resp.get("Success"):
            return resp.get("Data").get("userInfo")
        else:
            self.error_handler(resp)

    