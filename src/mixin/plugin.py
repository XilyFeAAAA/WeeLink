from src.utils import logger
from src.plugin import PluginBase
from watchdog.observers import Observer
from watchdog.events import DirModifiedEvent, FileModifiedEvent, FileSystemEventHandler
import os
import time
import asyncio
import inspect
import importlib




class PluginHandler(FileSystemEventHandler):

    def __init__(self, loop, callback, debounce_time=1) -> None:
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


class PluginMixin:

    def __init__(self):
        self.plugins_obj: dict[str, PluginBase] = {}
        self.plugins_cls: dict[str, type[PluginBase]] = {}
        self.plugins_dir: dict[str, str] = {}
        self.plugin_observe = None
        
    
    async def start_plugin(self):
        """启动插件管理"""
        loop = asyncio.get_running_loop()
        handler = PluginHandler(loop=loop, callback=self.modify_callback, debounce_time=10)
        self.plugin_observe = Observer()
        self.plugin_observe.schedule(handler, "plugins", recursive=True)
        self.plugin_observe.start()
        logger.success("插件热重载监视器已启动")
        await self.load_plugin_from_dictionary()

    async def stop_plugin(self):
        """停止插件管理"""
        self.plugin_observe.stop()
        await self.unload_plugins()


    async def modify_callback(self, src_path: str):
        """热加载回调"""
        plugin_folder = os.path.abspath("plugins")
        modified_path = os.path.abspath(src_path)
        rel_path = os.path.relpath(modified_path, plugin_folder)
        if not (parts := rel_path.split(os.sep)):
            return
        dirname = parts[0]
        if plugin_name := next((k for k, v in self.plugins_dir.items() if v == dirname), None):
            await self.reload_plugin(plugin_name)
            logger.success(f"插件 {plugin_name} 已成功热重载")


    async def load_plugin_from_dictionary(self):
        for dirname in os.listdir("plugins"):
            if os.path.isdir(f"plugins/{dirname}") and os.path.exists(f"plugins/{dirname}/main.py"):
                try:
                    module = importlib.import_module(f"plugins.{dirname}.main")
                    for _, cls in inspect.getmembers(module):
                        if inspect.isclass(cls) and issubclass(cls, PluginBase) and cls != PluginBase:
                            await self.load_plugin(cls, dirname)

                except Exception as e:
                    logger.error(f"加载 {dirname} 时发生错误: {e}")
                    raise
    
    
    async def load_plugin(self, plugin_class: PluginBase, dirname: str = None) -> None:
        from src.bot import Bot
        plugin_name = plugin_class.__name__
        plugin_author = plugin_class.__author__
        plugin_version = plugin_class.__version__
        plugin_enabled = plugin_class.__enabled__
        
        if not plugin_enabled: 
            return logger.warning(f"插件 - {plugin_name} 处于禁用状态")
        
        try:
            plugin = plugin_class()
            # 绑定 Matcher
            plugin.register_matchers()
            # 初始化
            await plugin.async_init(await Bot.get_instance())
            self.plugins_obj[plugin_name] = plugin
            self.plugins_cls[plugin_name] = plugin_class
            self.plugins_dir[plugin_name] = dirname
            logger.success(f"插件 {plugin_name} 已成功安装，作者:{plugin_author} 版本:{plugin_version}")
        except Exception as e:
            logger.error(f"插件 {plugin_name} 加载失败，{str(e)}")


    async def unload_plugin(self, plugin_name: str) -> None:
        """卸载单个插件"""
        if plugin_name not in self.plugins_cls:
            return logger.error(f"插件 {plugin_name} 不存在")
        plugin_obj = self.plugins_obj[plugin_name]
        
        from src.bot import Bot
        try:
            # 析构函数
            await plugin_obj.async_cleanup(await Bot.get_instance())
            # 解绑插件 Matcher
            plugin_obj.unbind_matcher()
            # 清理内存
            del self.plugins_dir[plugin_name]
            del self.plugins_obj[plugin_name]
            del self.plugins_cls[plugin_name]
        except Exception as e:
            logger.error(f"插件 {plugin_name} 已卸载失败: {str(e)}")        


    async def unload_plugins(self) -> None:
        """卸载全部插件"""
        for plugin_name in self.plugins_cls.keys():
            await self.unload_plugin(plugin_name)
    
    
    async def reload_plugin(self, plugin_name: str) -> None:
        """重载插件"""
        if plugin_name not in self.plugins_cls:
            return logger.error(f"插件 {plugin_name} 不存在")

        try:
            plugin_cls = self.plugins_cls[plugin_name]
            plugin_dir = self.plugins_dir[plugin_name]
            module_name = plugin_cls.__module__

            await self.unload_plugin(plugin_name)
            module = importlib.import_module(module_name)
            importlib.reload(module)
            for _, cls in inspect.getmembers(module):
                if (
                    inspect.isclass(cls)
                    and issubclass(cls, PluginBase)
                    and cls != PluginBase
                    and cls.__name__ == plugin_name
                ):
                    return await self.load_plugin(cls, plugin_dir)

        except Exception as e:
            logger.error(f"重载插件 {plugin_name} 时发生错误: {e}")
            return False

