from src.error import HttpError
from loguru import logger
from urllib.parse import urlencode
import aiohttp

async def post(url, *, json=True, body={}, query={}, headers={}) -> dict:
    if query:
        url += '?' + urlencode(query)
    try:
        async with aiohttp.ClientSession() as session:
            response = await session.post(url, headers=headers, json=body)
            return await response.json() if json else response
    except Exception as e:
        logger.error(f"http请求失败, 地址为{url}, 错误提示{e}")
        raise e


async def get(url, *, json=True, query={}, headers={}):
    if query:
        url += '?' + urlencode(query)
    try:
        async with aiohttp.ClientSession() as session:
            response = await session.get(url, headers=headers)
            return await response.json() if json else response
    except Exception as e:
        logger.error(f"http请求失败, 地址为{url}, 错误提示{e}")
        raise HttpError(e)