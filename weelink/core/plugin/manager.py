# standard library
import sys
import time
import shutil
import asyncio
import functools
import importlib
from pathlib import Path
from typing import Awaitable
from watchdog.observers import Observer
from watchdog.events import DirModifiedEvent, FileModifiedEvent, FileSystemEventHandler

# local library
from .base import Plugin
from .config import PluginConfig
from .metadata import PluginMetaData
from weelink.core.adapter import Adapter
from weelink.core.utils import logger, PLUGIN_DIR, print_exc
from weelink.core.internal.config import conf
from weelink.core.on.registry import HandleRegistry

""" module_name - PluginMetaData """
plugins: dict[str, PluginMetaData] = {}


def registry_plugin(
    name: str,
    desc: str,
    author: str,
    version: str,
    repo: str = None,
    adapters: list[type[Adapter]] = []
) -> type[Plugin]:
    def decorator(cls: type[Plugin]) -> None:
        metadata = PluginMetaData(
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
        return cls
    return decorator


class PluginManager:
    
    def __init__(self) -> None:
        self.modules = []
        self.enabled_plugins = {}
        self.observe = Observer()


    async def run(self) -> None:
        """启动插件系统"""
        try:
            loop = asyncio.get_running_loop()
            
            if not PLUGIN_DIR.exists():
                PLUGIN_DIR.mkdir(parents=True)
            
            await self.restart()
            
            self.observe.schedule(PluginHandler(
                loop=loop,
                callback=self.hot_reload
            ), PLUGIN_DIR, recursive=True)
            self.observe.start()
            logger.success("插件热重载已启动")
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
    
    
    async def load_plugin(self, module_str: str) -> None:
        """导入插件所在的模块"""
        
        # 判断是否重复导入模块
        if module_str in sys.modules:
            return logger.warning(f"模块 { module_str } 重复导入")
        
        try:
            importlib.import_module(module_str)
        except ImportError:
            if await self.check_env(module_str):
                importlib.import_module(module_str)
            else:
                raise Exception("依赖错误")
        except ModuleNotFoundError:
            return logger.warning(f"模块 {module_str} 导入失败，请检查目录")
        except Exception as e:
            logger.error(f"目录 {module_str} 导入插件失败：{str(e)}")
            return print_exc(type(e), e, e.__traceback__)
        
        logger.success(f"模块 { module_str } 已导入")
    
    
    async def load_all_plugins(self) -> None:
        """加载全部插件"""
        if not PLUGIN_DIR.exists():
            PLUGIN_DIR.mkdir(parents=True)
        
        for plugin_dir in PLUGIN_DIR.iterdir():
            if not plugin_dir.is_dir():
                continue
            if not (plugin_dir / "__init__.py").exists() or not (plugin_dir / "main.py"):
                logger.warning(f"插件 {plugin_dir.name} 需要对外提供__init__.py以及main.py文件，请通过DashBoard重新加载")
                continue
            try:
                module_str = f"data.plugins.{plugin_dir.name}.main"
                await self.load_plugin(module_str)
            except Exception as e:
                logger.error(f"模块 { module_str} 加载错误: {e}")
    
    
    async def unload_plugin(self, plugin_name: str) -> None:
        """卸载插件"""
        # 如果插件在运行，就先禁用
        if plugin_name in self.enabled_plugins:
            await self.disable_plugin(plugin_name)
        
        # 获取插件元信息
        plugin_md = self.get_one_plugin(plugin_name)
        if plugin_md is None:
            return logger.warning(f"插件 { plugin_name } 卸载失败：未导入插件管理器")
        
        for module_name in sys.modules.copy():
            if module_name.startswith(plugin_md.module):
                del sys.modules[module_name]
        
        logger.success(f"插件 { plugin_name } 卸载成功")
    
    
    async def unload_all_plugins(self) -> None:
        """卸载全部插件"""
        for plugin_md in plugins.values():
            await self.unload_plugin(plugin_md.name)
    
    
    async def enable_plugin(self, plugin_name: str) -> None:
        """启用插件"""
        # 判断插件是否注册元信息
        if (plugin_md := self.get_one_plugin(plugin_name)) is None:
            return logger.warning(f"插件 {plugin_name} 未注册插件元信息")
                
        # 检查插件是否禁用
        if plugin_name in conf.inactive_plugins:
            return logger.warning(f"插件 {plugin_name} 处于禁用状态")
        
        # 判断是否已启用
        if plugin_name in self.enabled_plugins:
            return logger.warning(f"插件 {plugin_name} 重复加载")

        # 获取插件配置
        folder_name = plugin_md.module.split(".")[-2]
        plugin_md.config = PluginConfig(folder_name)
        
        # 实例化插件
        plugin_md.obj = plugin_md.cls(
            config=plugin_md.config
        )
        
        try:
            await plugin_md.obj.on_load()
        except NotImplementedError:
            pass
        except Exception as e:
            logger.error(f"插件 {plugin_name} on_Load回调执行失败: {e}")
        
        handlers = HandleRegistry.get_handlers_from_module(plugin_md.module)
        for handler in handlers:
            # 绑定方法 = 未绑定方法 + self
            handler.callback = functools.partial(
                handler.callback, plugin_md.obj
            )
            handler.plugin = plugin_md
        
        self.enabled_plugins[plugin_name] = plugin_md
        logger.success(f"插件 { plugin_name} 已启用")
    
    
    async def disable_plugin(self, plugin_name: str) -> None:
        """关闭插件"""
        # 判断插件是否启用
        if plugin_name not in self.enabled_plugins:
            return logger.warning(f"插件 { plugin_name } 未启用无法关闭，请检查日志")
        
        # 插件配置保存
        md = self.enabled_plugins[plugin_name]
        md.config.save()
        
        # on_terminate        
        try:
            await md.obj.on_terminate()
        except NotImplementedError:
            pass
        except Exception as e:
            logger.error(f"插件 {plugin_name} on_Load回调执行失败: {e}")
        
        # 解绑处理回调
        handlers = HandleRegistry.get_handlers_from_plugin(plugin_md=md)
        for handler in handlers:
            HandleRegistry.unregister(handler=handler)

        del self.enabled_plugins[plugin_name]
        logger.success(f"插件 { plugin_name} 已禁用")
    
    
    async def reload_plugin(self, plugin_name: str) -> None:
        """重载插件"""
        try:
            if plugin_name in self.enabled_plugins:
                plugin_md = self.enabled_plugins[plugin_name]
                await self.disable_plugin(plugin_name)
                importlib.reload(plugin_md.module)
            else:
                plugin_md = self.get_one_plugin(plugin_name)
                await self.load_plugin(plugin_md.module)
        except Exception as e:
            logger.error(f"插件 { plugin_name } 重载失败: {e}")
    
    
    async def update_plugin(self) -> None:
        pass
    
    
    async def install_plugin(self) -> None:
        pass
    
    
    async def uninstall_plugin(self, plugin_name: str) -> None: 
        """删除插件"""
        
        if (plugin_md := self.get_one_plugin(plugin_name)) is None:
            return logger.error(f"插件 { plugin_name } 卸载失败：插件元信息未注册")
                
        # 卸载插件模块
        await self.unload_plugin(plugin_name)
        
        # 找插件目录名
        dirname = plugin_md.module.split(".")[-2]
        plugin_path = PLUGIN_DIR / dirname
        if not plugin_path.exists():
            return
        
        try:
            await asyncio.to_thread(shutil.rmtree, plugin_path)
            del plugins[plugin_md.module]
        except Exception as e:
            logger.error(f"删除插件 { plugin_name } 失败: {e}")
    
    
    async def check_env(self, plugin_dir: Path) -> bool:
        """检查插件环境"""
        return True
    
    
    async def restart(self) -> None:
        """重启插件管理器"""

        try:
            # 卸载全部插件
            await self.unload_all_plugins()
            # 清空注册的插件
            plugins.clear()
            # 加载全部插件
            await self.load_all_plugins()
            # 启用全部插件
            for plugin_md in plugins.values():
                await self.enable_plugin(plugin_md.name)
        except Exception as e:
            logger.error(f"重启插件管理器失败: {e}")
    
    
    def get_all_plugins(self) -> list[PluginMetaData]:
        return plugins.values()
    
    
    def get_one_plugin(self, plugin_name: str) -> PluginMetaData:
        """根据插件名返回插件元信息"""
        return next((md for md in plugins.values() if md.name == plugin_name), None)
    

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