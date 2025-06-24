# standard library
import abc

# local library

class Plugin(abc.ABC):
    

    async def on_load(self):
        """启动时异步回调"""
        raise NotImplementedError


    async def on_terminate(self) -> None:
        """关闭or重启时异步回调"""
        raise NotImplementedError