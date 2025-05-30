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
        if (profile := await self.get_profile()) is None:
            if await self.get_cached_info():
                logger.debug("尝试二次登录")
                if not await self.twice_login():
                    logger.info("尝试唤醒登录...")
                    if not await self.revoke_login():
                        logger.info("尝试二维码登录...")
                        await self.qrcode_login()
            else:
                await self.qrcode_login()
        else:
            self.status.nickname = profile.get("NickName", {}).get("string", "")
            self.status.alias = profile.get("Alias", "")
            self.status.phone = profile.get("BindMobile", {}).get("string", "")
        logger.info("设备登录成功")
        logger.info(f"登录账号信息: wxid: {self.status.wxid}  昵称: {self.status.nickname} 微信号: {self.status.alias}  手机号: {self.status.phone}")     
        
        
    async def get_cached_info(self):
        param = {
            "wxid": self.status.wxid
        }
        resp = await post(f"{URL}/Login/GetCacheInfo", query=param)
        return resp.get("Data") if resp.get("Success") else None
        
    async def twice_login(self):
        param = {
            "wxid": self.status.wxid
        }
        resp = await post(f"{URL}/Login/TwiceAutoAuth", body=param)
        logger.debug(resp)
        if resp.get("Success"):
            return resp.get("Data") 
        else :
            return logger.error(f"二次登录失败: {resp.get('Message', '未知错误')}")
    
    
    async def revoke_login(self):
        param = {
            "OS": self.status.device_name or "iPad",
            "Proxy": {
                "ProxyIp": "",
                "ProxyPassword": "",
                "ProxyUser": ""
            },
            "Url": "",
            "Wxid": self.status.wxid
        }
        resp = await post(f"{URL}/Login/Awaken", body=param)
        if resp.get("Success"):
            data = resp.get("Data", {})
            qr_response = data.get("QrCodeResponse", {}) if data else {}
            self.status.uuid = qr_response.get("Uuid", "") if qr_response else ""
            logger.success(f"唤醒登录成功,获取到登录uuid: {self.status.wxid}")
        else:
            logger.error(f"唤醒登录失败: {resp.get('Message', '未知错误')}")
            
    async def qrcode_login(self):
        if not self.status.device_name:
            self.status.device_name = create_device_name()
        if not self.status.device_id:
            self.status.device_id = create_device_id()
        param = {
            'DeviceName': self.status.device_name,
            'DeviceID': self.status.device_id
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
            self.status.uuid, url = resp.get("Data").get("Uuid"), resp.get("Data").get("QrUrl")
            logger.info(f"登录uuid: {self.status.uuid}, 二维码url: {url}")
        else:
            self.error_handler(resp)
        
        while True:
            stat, data = await self.check_login()
            if stat: break
            logger.info(f"等待登录中，过期倒计时：{data}")
            await asyncio.sleep(5)
        self.status.wxid = data.get("userName")
        self.status.nickname = data.get("NickName")
        self.status.alias = data.get("Alais")
        self.status.phone = data.get("Mobile")
        
    
    async def check_login(self):
        param = {
            "uuid": self.status.uuid
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
            "wxid": self.status.wxid
        }
        resp = await post(f"{URL}/Login/HeartBeatLong", query=param)
        if resp.get("Success"):
            logger.success("已开启自动心跳")
        else:
            logger.error(f"开启自动心跳失败: {resp}")
            sys.exit()
    
    async def stop_auto_heartbeat(self):
        param = {
            "wxid": self.status.wxid
        }
        resp = await post(f"{URL}/Login/CloseAutoHeartbeat", query=param)
        if resp.get("Success"):
            logger.success("已关闭自动心跳")
        else:
            logger.error(f"关闭自动心跳失败: {resp}")
    
    async def status_auto_heartbeat(self):
        param = {
            "wxid": self.status.wxid
        }
        resp = await post(f"{URL}/Login/AutoHeartbeatStatus", query=param)
        if resp.get("Success"):
            return resp.get("Running")
        else:
            self.error_handler(resp)

