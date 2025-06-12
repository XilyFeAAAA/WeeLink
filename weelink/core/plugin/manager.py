# standard library
import time
import asyncio
import functools
from pathlib import Path
from typing import Awaitable
from watchdog.observers import Observer
from watchdog.events import DirModifiedEvent, FileModifiedEvent, FileSystemEventHandler

# local library
from .base import Plugin
from .context import PluginContext
from .metadata import PluginMetaData
from weelink.core.adapter import Adapter
from weelink.core.utils import logger, PLUGIN_DIR, print_exc
from weelink.core.flow.registry import HandleRegistry

""" module - PluginMetaData """
plugins: dict[str, PluginMetaData] = {}


def registry_plugin(
    name: str,
    desc: str,
    author: str,
    version: str,
    repo: str = None,
    enable: bool = True,
    adapters: list[Adapter] = []
) -> type[Plugin]:
    def decorator(cls: type[Plugin]) -> None:
        metadata = PluginMetaData(
            enable=enable,
            name=name,
            author=author,
            version=version,
            desc=desc,
            repo=repo,
            adapters=adapters,
            module=cls.__module__,
            cls=cls,
            obj=None
        )
        plugins[metadata.module] = metadata
    return decorator


class PluginManager:
    
    def __init__(self) -> None:
        self.modules = []
        self.observe = Observer()


    async def run(self) -> None:
        """启动插件系统"""
        try:
            loop = asyncio.get_running_loop()
            
            if not PLUGIN_DIR.exists():
                PLUGIN_DIR.mkdir(parents=True)
            self.observe.schedule(PluginHandler(
                loop=loop,
                callback=self.hot_reload
            ), PLUGIN_DIR, recursive=True)
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


    async def load_plugin(self, module_path: Path) -> None:
        """加载指定插件"""
        module_name = module_path.name
        logger.info(f"正在载入插件 {module_name}")
        try:
            module = __import__(module_path)
        except (ModuleNotFoundError, ImportError):
            await self.check_env(module_path)
            module = __import__(module_path)
        except Exception as e:
            logger.error(f"插件 {module_name} 导入失败：{str(e)}")
            return print_exc(type(e), e, e.__traceback__)
            
        plugin_metadate = plugins.get(module)
        if plugin_metadate is None:
            return logger.warning(f"插件 {module_name} 未注册元信息")
        
        if not plugin_metadate.enable:
            return logger.warning(f"插件 {module_name} 处于禁用状态")
        
        # 实例化插件
        plugin_metadate.obj = plugin_metadate.cls(
            context=PluginContext()
        )
        
        if hasattr(plugin_metadate.obj, "on_load"):
            await plugin_metadate.obj.on_load()
        
        handlers = HandleRegistry.get_handlers_from_module(module)
        for handler in handlers:
            # 绑定方法 = 未绑定方法 + self
            handler.callback = functools.partial(
                handler.handler, plugin_metadate.obj
            )
            handler.plugin = plugin_metadate

    
    async def load_all_plugins(self) -> None:
        """加载全部插件"""
        if not PLUGIN_DIR.exists():
            PLUGIN_DIR.mkdir(parents=True)
        
        for module in PLUGIN_DIR.iterdir():
            if not module.is_dir():
                continue
            if not (module / "__init__.py").exists():
                logger.warning(f"插件 {module.name} 需要对外提供__init__.py文件，请通过DashBoard重新加载")
                continue
            await self.load_plugin(module)
    
    
    async def unload_plugin(self) -> None:
        pass
    
    
    async def unload_all_plugins(self) -> None:
        pass
    
    
    async def reload_plugin(self) -> None:
        pass
    
    
    async def update_plugin(self) -> None:
        pass
    
    
    async def install_plugin(self) -> None:
        pass
    
    
    async def uninstall_plugin(self) -> None:
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