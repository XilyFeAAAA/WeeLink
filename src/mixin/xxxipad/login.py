from src.utils.http import post
from src.utils.device import create_device_id, create_device_name
from src.mixin.base import BaseMixIn
from .constants import URL
from loguru import logger
import sys
import qrcode
import asyncio


class LoginMixIn(BaseMixIn):

    
    async def login(self):
        if not await self.is_logged_in():
            if await self.get_cached_info():
                logger.debug("尝试二次登录")
                if not (twice := await self.twice_login()):
                    logger.info("尝试唤醒登录...")
                    if not await self.revoke_login():
                        logger.info("尝试二维码登录...")
                        await self.qrcode_login()
            else:
                await self.qrcode_login()
        else:
            profile = await self.get_profile()
            self.nickname = profile.get("NickName", {}).get("string", "")
            self.alias = profile.get("Alias", "")
            self.phone = profile.get("BindMobile", {}).get("string", "")
        self.is_logged = True
        logger.info("设备登录成功")
        logger.info(f"登录账号信息: wxid: {self.wxid}  昵称: {self.nickname} 微信号: {self.alias}  手机号: {self.phone}")     
        
        
    async def get_cached_info(self):
        param = {
            "wxid": self.wxid
        }
        resp = await post(f"{URL}/Login/GetCacheInfo", query=param)
        return resp.get("Data") if resp.get("Success") else None
        
    async def twice_login(self):
        param = {
            "wxid": self.wxid
        }
        resp = await post(f"{URL}/Login/TwiceAutoAuth", body=param)
        logger.debug(resp)
        if resp.get("Success"):
            return resp.get("Data") 
        else :
            return logger.error(f"二次登录失败: {resp.get('Message', '未知错误')}")
    
    
    async def revoke_login(self):
        param = {
            "OS": self.device_name or "iPad",
            "Proxy": {
                "ProxyIp": "",
                "ProxyPassword": "",
                "ProxyUser": ""
            },
            "Url": "",
            "Wxid": self.wxid
        }
        resp = await post(f"{URL}/Login/Awaken", body=param)
        if resp.get("Success"):
            data = resp.get("Data", {})
            qr_response = data.get("QrCodeResponse", {}) if data else {}
            self.uuid = qr_response.get("Uuid", "") if qr_response else ""
            logger.success(f"唤醒登录成功,获取到登录uuid: {self.wxid}")
        else:
            logger.error(f"唤醒登录失败: {resp.get('Message', '未知错误')}")
            
    async def qrcode_login(self):
        if not self.device_name:
            self.device_name = create_device_name()
        if not self.device_id:
            self.device_id = create_device_id
        param = {
            'DeviceName': self.device_name,
            'DeviceID': self.device_id
        }
        resp = await post(f"{URL}/Login/GetQR", body=param)
        if resp.get("Success"):
            qr = qrcode.QRCode(
                        version=1,
                        error_correction=qrcode.constants.ERROR_CORRECT_L,
                        box_size=10,
                        border=4,
            )
            qr.add_data(f'http://weixin.qq.com/x/{resp.get("Data").get("Uuid")}')
            qr.make(fit=True)
            qr.print_ascii()
            self.uuid, url = resp.get("Data").get("Uuid"), resp.get("Data").get("QrUrl")
            logger.info(f"登录uuid: {self.uuid}, 二维码url: {url}")
        else:
            self.error_handler(resp)
        
        while True:
            stat, data = await self.check_login()
            if stat: break
            logger.info(f"等待登录中，过期倒计时：{data}")
            await asyncio.sleep(5)
        self.wxid = data.get("userName")
        self.nickname = data.get("NickName")
        self.alias = data.get("Alais")
        self.phone = data.get("Mobile")
        
    
    async def check_login(self):
        param = {
            "uuid": self.uuid
        }
        resp = await post(f"{URL}/Login/CheckQR", query=param)
        if resp.get("Success"):
            if resp.get("Data").get("acctSectResp", ""):
                return True, resp.get("Data").get("acctSectResp")
            else:
                return False, resp.get("Data").get("expiredTime")
        else:
            logger.error(resp)
            # self.error_handler(resp)
            
                       
    async def start_auto_heartbeat(self):
        param = {
            "wxid": self.wxid
        }
        resp = await post(f"{URL}/Login/HeartBeatLong", query=param)
        if resp.get("Success"):
            logger.success("已开启自动心跳")
        else:
            logger.error(f"开启自动心跳失败: {resp}")
            sys.exit()
    
    async def stop_auto_heartbeat(self):
        param = {
            "wxid": self.wxid
        }
        resp = await post(f"{URL}/Login/CloseAutoHeartbeat", query=param)
        if resp.get("Success"):
            logger.success("已关闭自动心跳")
        else:
            logger.error(f"关闭自动心跳失败: {resp}")
    
    async def status_auto_heartbeat(self):
        param = {
            "wxid": self.wxid
        }
        resp = await post(f"{URL}/Login/AutoHeartbeatStatus", query=param)
        if resp.get("Success"):
            return resp.get("Running")
        else:
            self.error_handler(resp)