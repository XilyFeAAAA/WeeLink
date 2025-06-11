# stardard libaray
import asyncio

# local library
from weelink import Initiator
from weelink.core.utils import logger


WEELINK = r"""
____    __    ____  _______  _______  __       __  .__   __.  __  ___ 
\   \  /  \  /   / |   ____||   ____||  |     |  | |  \ |  | |  |/  / 
 \   \/    \/   /  |  |__   |  |__   |  |     |  | |   \|  | |  '  /  
  \            /   |   __|  |   __|  |  |     |  | |  . `  | |    <   
   \    /\    /    |  |____ |  |____ |  `----.|  | |  |\   | |  .  \  
    \__/  \__/     |_______||_______||_______||__| |__| \__| |__|\__\ 
"""



if __name__ == "__main__":
    try:
        logger.debug(WEELINK)
        initiator = Initiator()
        asyncio.run(initiator.run())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logger.error("未知错误，WeeLink提前结束，请查阅日志文件...")