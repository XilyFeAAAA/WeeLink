# standard library
import sys
import time
import asyncio
from pathlib import Path
from typing import Awaitable
from watchdog.observers import Observer
from watchdog.events import DirModifiedEvent, FileModifiedEvent, FileSystemEventHandler

# local library
from .plugin import Plugin
from .metadata import PluginMetaData
from weelink.core.utils import logger
from weelink.core.adapter import Adapter


""" id - PluginMetaData """
plugins: dict[str, PluginMetaData] = {}
plugin_dir = Path.cwd() / "data" / "plugins"


def registry_plugin(
    name: str,
    desc: str,
    author: str,
    version: str,
    repo: str = None,
    enable: bool = True,
    adapter: Adapter = None
) -> type[Plugin]:
    def decorator(cls: type[Plugin]) -> None:
        metadata = PluginMetaData(
            enable=enable,
            name=name,
            author=author,
            version=version,
            desc=desc,
            repo=repo,
            adapter=adapter,
            module=None,
            obj=None,
            cls=cls,
        )
        plugins[metadata.id] = metadata
    return decorator


class PluginManager:
    
    def __init__(self) -> None:
        self.observe = Observer()
    
    
    async def run(self) -> None:
        """启动插件系统"""
        try:
            loop = asyncio.get_running_loop()
            
            if not plugin_dir.exists():
                plugin_dir.mkdir(parents=True)
            self.observe.schedule(PluginHandler(
                loop=loop,
                callback=self.hot_reload
            ), plugin_dir, recursive=True)
            self.observe.start()
            logger.success("插件热重载已启动")
            await self.load_all_plugins()
        except Exception as e:
            logger.critical(f"插件管理启动失败: {str(e)}")
    
    async def terminate(self) -> None:
        """终止插件系统"""
        try:
            self.observe.stop()
            await self.unload_all_plugins()
        except Exception as e:
            logger.critical(f"插件管理终止失败: {str(e)}")
    
    async def hot_reload(self, src_path) -> None:
        """TODO"""
        pass
    
    
    async def load_plugin(self) -> None:
        pass
    
    
    async def load_all_plugins(self) -> None:
        pass
    
    
    async def unload_plugin(self) -> None:
        pass
    
    
    async def unload_all_plugins(self) -> None:
        pass
    
    
    async def reload_plugin(self) -> None:
        pass
    
    
    async def update_plugin(self) -> None:
        pass


class PluginHandler(FileSystemEventHandler):

    def __init__(self, 
            loop: asyncio.BaseEventLoop, 
            callback: Awaitable, 
            debounce_time=1
        ) -> None:
        super().__init__()
        self.loop = loop
        self.debounce_time = debounce_time
        self.last_modified_time = 0
        self.callback = callback
        
        
    def on_modified(self, event: DirModifiedEvent | FileModifiedEvent) -> None:
        """文件/目录修改回调"""
        if event.is_directory:
            return
        
        cnt_time = time.time()
        if cnt_time - self.last_modified_time < self.debounce_time:
            return
        self.last_modified_time = cnt_time
        self.loop.create_task(self.callback(event.src_path))