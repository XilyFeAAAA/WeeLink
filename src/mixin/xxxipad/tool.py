from src.mixin.base import BaseMixIn
from src.utils import post, logger
from .constants import URL
import base64


class ToolMixIn(BaseMixIn):
    
    
    async def download_chunk_image(self, msg_id: str, to_wxid: str, 
                                   data_len: int, sta_pos: int, download_size: int) -> bytes:
        """分段下载图片"""
        param = {
            "Wxid": self.status.wxid,
            "ToWxid": to_wxid,
            "MsgId": int(msg_id),
            "DataLen": data_len,
            "CompressType": 0,
            "Section": {
                "StartPos": sta_pos,
                "DataLen": download_size
            }
        }
        resp = await post(f"{URL}/Tools/DownloadImg", body=param)
        if resp.get("Success", False):
            # 尝试从不同的响应格式中获取图片数据
            data = resp.get("Data")

            if isinstance(data, dict):
                # 如果是字典，尝试获取buffer字段
                if "buffer" in data:
                    return base64.b64decode(data["buffer"])
                elif "data" in data and isinstance(data["data"], dict) and "buffer" in data["data"]:
                    return base64.b64decode(data["data"]["buffer"])
                else:
                    # 如果没有buffer字段，尝试直接解码整个data
                    try:
                        return base64.b64decode(str(data))
                    except:
                        logger.error(f"无法解析图片数据字典: {data}")
            elif isinstance(data, str):
                # 如果是字符串，直接解码
                try:
                    return base64.b64decode(data)
                except:
                    logger.error(f"无法解析图片数据字符串: {data[:100]}...")
            else:
                logger.error(f"无法解析图片数据类型: {type(data)}")
        else:
            return None

        
        
    async def download_cdn_image(self, aeskey: str, cdnmidimgurl: str) -> str:
        """CDN下载图片"""
        param = {
            "Wxid": self.status.wxid, 
            "FileAesKey": aeskey, 
            "FileNo": cdnmidimgurl
        }
        resp = await post(f"{URL}/Tools/CdnDownloadImage", body=param)
        if resp.get("Success", False):
            return resp.get("Data")
        else:
            self.error_handler(resp)
                

    async def download_voice(self, msg_id: str, voiceurl: str, length: int) -> str:
        """下载语音文件"""
        param = {
            "Wxid": self.status.wxid, 
            "MsgId": msg_id, 
            "Voiceurl": voiceurl, 
            "Length": length
        }
        resp = await post(f"{URL}/Tools/DownloadVoice", body=param)
        if resp.get("Success", False):
            return resp.get("Data", {}).get("data", {}).get("buffer")
        else:
            self.error_handler(resp)


    async def download_attach(self, attach_id: str) -> dict:
        """下载附件"""
        param = {
            "Wxid": self.status.wxid, 
            "AttachId": attach_id
        }
        resp = await post(f"{URL}/Tools/DownloadAttach", body=param)
        if resp.get("Success", False):
            return resp.get("Data", {}).get("data", {}).get("buffer")
        else:
            self.error_handler(resp)


    async def download_chunk_video(self,msg_id: str, to_wxid: str, 
                                   data_len: int, sta_pos: int, download_size: int) -> str:
        """下载视频"""
        param = {
            "CompressType": 0,
            "DataLen": data_len,
            "MsgId": msg_id,
            "Section": {
                "DataLen": download_size,
                "StartPos": sta_pos
            },
            "ToWxid": to_wxid,
            "Wxid": self.status.wxid
        }
        resp = await post(f"{URL}/Tools/DownloadVideo", body=param)
        if resp.get("Success", False):
            # 尝试从不同的响应格式中获取图片数据
            data = resp.get("Data")

            if isinstance(data, dict):
                # 如果是字典，尝试获取buffer字段
                if "buffer" in data:
                    return base64.b64decode(data["buffer"])
                elif "data" in data and isinstance(data["data"], dict) and "buffer" in data["data"]:
                    return base64.b64decode(data["data"]["buffer"])
                else:
                    # 如果没有buffer字段，尝试直接解码整个data
                    try:
                        return base64.b64decode(str(data))
                    except:
                        logger.error(f"无法解析图片数据字典: {data}")
            elif isinstance(data, str):
                # 如果是字符串，直接解码
                try:
                    return base64.b64decode(data)
                except:
                    logger.error(f"无法解析图片数据字符串: {data[:100]}...")
            else:
                logger.error(f"无法解析图片数据类型: {type(data)}")
        else:
            return None

    async def set_step(self, count: int) -> bool:
        """设置步数"""
        param = {
            "Wxid": self.status.wxid, 
            "StepCount": count
        }
        resp = await post(f"{URL}/Tools/SetStep", body=param)
        if resp.get("Success", False):
            return True
        else:
            self.error_handler(resp)