from src.utils import logger
from .base import BaseMixIn
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.base import BaseJobStore
import asyncio 



class ScheduleMixin(BaseMixIn):
    
    def __init__(self) -> None:
        super().__init__()
        self._schedule = AsyncIOScheduler()
    
    
    def run_schedule(self):
        """启动 APScheduler"""
        self._schedule.start()
        logger.info("任务调度器启动")
    
    def pause_schedule(self):
        """暂停 APScheduler"""
        self._schedule.pause()
        logger.info("任务调度器已暂停")

    def stop_schedule(self):
        """停止 APScheduler"""
        self._schedule.shutdown()
        logger.info("任务调度器已停止")
    
    
    def add_store(self, job_store: BaseJobStore) -> None:
        """添加 Job Store"""
        if not isinstance(job_store, BaseJobStore):
            raise Exception("添加的 Job Store 错误")
        self._schedule.add_jobstore(job_store)
        
        
    def add_task(self, handle: callable, task_id: str, **kwargs) -> None:
        """添加任务"""
        if not asyncio.iscoroutinefunction(handle):
            raise Exception("响应函数必须是异步函数")
        self._schedule.add_job(func=handle, id=task_id, **kwargs)
        
    
    def cancel_task(self, task_id: str) -> None:
        """取消任务"""
        try:
            self._schedule.remove_job(task_id)
        except Exception as e:
            logger.error(f"取消任务失败: {task_id}")
        
    
    @property
    def state(self) -> int:
        """获取 APScheduler 状态"""
        return self._schedule.state
    
