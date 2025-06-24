from loguru import logger
from urllib.parse import urlencode
import aiohttp
import base64

async def post(url, *, json=True, body={}, query={}, headers={}) -> dict:
    if query:
        url += '?' + urlencode(query)
    try:
        async with aiohttp.ClientSession() as session:
            response = await session.post(url, headers=headers, json=body)
            return await response.json() if json else response
    except Exception as e:
        logger.error(f"http请求失败, 地址为{url}, 错误提示{e}")
        raise


async def get(url, *, json=True, query={}, headers={}):
    if query:
        url += '?' + urlencode(query)
    try:
        async with aiohttp.ClientSession() as session:
            response = await session.get(url, headers=headers)
            return await response.json() if json else response
    except Exception as e:
        logger.error(f"http请求失败, 地址为{url}, 错误提示{e}")
        raise
    
    
async def download_image(url: str) ->str:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    image_data = await response.read()
                    return base64.b64encode(image_data).decode('utf-8')
                else:
                    return None
    except Exception as e:
        logger.error(f"下载图片失败: {str(e)}")
        return None