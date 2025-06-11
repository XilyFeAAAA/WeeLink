# standard library
import asyncio

# local library
from weelink.core import Linkhub
from weelink.core.utils import logger, print_exc, ensure_directories
from weelink.dashboard import Dashboard

class Initiator:
    
    def __init__(self) -> None:
        # 确保所有必要的目录都存在
        ensure_directories()
        
        self.linkhub = Linkhub()
        self.dashboard = Dashboard()
    
    
    async def run(self) -> None:
        """启动 Linkhub 和 Dashboard 服务"""
        try:
            await self.linkhub.preload()
        except Exception as e:
            return logger.critical(f"Linkhub初始化遇到未知错误: {str(e)}")
        
        linkhub_coro = asyncio.create_task(self.linkhub.start())
        # dashboard_coro = self.dashboard.start()

        try:
            await asyncio.gather(
                linkhub_coro
            )
        except Exception as e:
            logger.critical(f"Weelink 遇到未知异常: {str(e)}")
            print_exc(type(e), e, e.__traceback__)
        finally:
            logger.info("正在关闭 Weelink...")
            try:
                await self.linkhub.stop()
                # await self.dashboard.stop()
                logger.success("Weelink退出成功！")
            except Exception as e:
                import sys
                logger.critical(f"Weelink退出遇到未知错误: {str(e)}")
                sys.exit()