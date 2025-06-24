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
        self.dashboard = Dashboard(self.linkhub, initiator=self)
        # 保存任务引用
        self.linkhub_task = None
        self.dashboard_task = None
        # 用于控制重启流程的事件
        self.restart_event = asyncio.Event()
    
    
    async def run(self) -> None:
        """启动 Linkhub 和 Dashboard 服务"""
        try:
            await self.linkhub.preload()
        except Exception as e:
            return logger.critical(f"Linkhub初始化遇到未知错误: {str(e)}")
        
        # 启动Dashboard，会一直运行
        self.dashboard_task = asyncio.create_task(self.dashboard.start())
        
        # Linkhub的主循环，支持重启
        while True:
            try:
                self.linkhub_task = asyncio.create_task(self.linkhub.start())
                
                # 等待Linkhub终止或收到重启信号
                restart_task = asyncio.create_task(self.restart_event.wait())
                done, pending = await asyncio.wait(
                    [self.linkhub_task, restart_task, self.dashboard_task],
                    return_when=asyncio.FIRST_COMPLETED
                )
                
                # 取消未完成的任务
                for task in pending:
                    if task == self.dashboard_task:
                        continue
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
                
                # 如果是收到重启信号
                if restart_task in done and restart_task.result() is True:
                    logger.info("收到Linkhub重启信号...")
                    # 停止当前的Linkhub
                    await self.linkhub.stop()
                    # 创建新的Linkhub实例
                    self.linkhub = Linkhub()
                    # 更新Dashboard中的引用
                    self.dashboard.app.state.linkhub = self.linkhub
                    # 预加载新的Linkhub
                    await self.linkhub.preload()
                    # 重置重启事件
                    self.restart_event.clear()
                    logger.success("Linkhub已重新创建，准备重新启动")
                    continue
                
                # 如果是Dashboard终止或发生异常，就退出循环
                else:
                    break
                
            except Exception as e:
                logger.critical(f"Weelink 遇到未知异常: {str(e)}")
                print_exc(type(e), e, e.__traceback__)
                break
        
        logger.info("正在关闭 Weelink...")
        try:
            await self.linkhub.stop()
            await self.dashboard.stop()
            logger.success("Weelink退出成功！")
        except Exception as e:
            import sys
            logger.critical(f"Weelink退出遇到未知错误: {str(e)}")
            sys.exit()
                
    async def restart_linkhub(self) -> None:
        """触发Linkhub重启"""
        logger.info("触发Linkhub重启...")
        self.restart_event.set()
        while self.restart_event.is_set():
            await asyncio.sleep(0.1)
        logger.success("Linkhub重启已完成")