# stardard libaray
import asyncio

# local library
from weelink.core.utils import logger
from weelink import Initiator


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
        print(WEELINK)
        initiator = Initiator()
        asyncio.run(initiator.run())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(e)
        logger.error("未知错误，WeeLink提前结束，请查阅日志文件...")