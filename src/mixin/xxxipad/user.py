from src.utils import post, logger
from .constants import URL

class UserMixIn:
    
    
    async def get_profile(self) -> dict:
        param = {
             "wxid": self.status.wxid
        }
        resp = await post(f'{URL}/User/GetContractProfile', query=param)
        return resp.get("Data").get("userInfo") if resp.get("Success") else None