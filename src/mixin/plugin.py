from src.utils import logger
from src.plugin import PluginBase
import os
import inspect
import importlib




class PluginMixin:


    async def load_plugin_from_dictionary(self):
        for dirname in os.listdir("plugins"):
            if os.path.isdir(f"plugins/{dirname}") and os.path.exists(f"plugins/{dirname}/main.py"):
                try:
                    module = importlib.import_module(f"plugins.{dirname}.main")
                    for _, obj in inspect.getmembers(module):
                        if inspect.isclass(obj) and issubclass(obj, PluginBase) and obj != PluginBase:
                            await self.load_plugin(obj)

                except Exception as e:
                    logger.error(f"加载 {dirname} 时发生错误: {e}")
                    raise
    
    
    async def load_plugin(self, plugin_class: PluginBase) -> None:
        from src.bot import Bot
        plugin_name = plugin_class.__name__
        plugin_author = plugin_class.__author__
        plugin_version = plugin_class.__version__
        plugin_enabled = plugin_class.__enabled__
        
        if not plugin_enabled: 
            return logger.warning(f"插件 - {plugin_name} 处于禁用状态")
        
        plugin = plugin_class()
        plugin.register_matchers()
        await plugin.async_init(await Bot.get_instance())
        logger.success(f"插件 {plugin_name} 已成功安装，作者:{plugin_author} 版本:{plugin_version}")