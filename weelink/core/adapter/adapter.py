# standard library
import abc

# local library


class Adapter(abc.ABC):

    # 默认配置字段
    CONFIG_FIELDS = []

    @classmethod
    def get_config_fields(cls) -> list[dict]:
        return cls.CONFIG_FIELDS

    
    @abc.abstractmethod
    def __init__(self, adapter_config: dict):
        raise NotImplementedError


    @abc.abstractmethod
    async def run(self) -> None:
        raise NotImplementedError


    @abc.abstractmethod
    async def terminate(self):
        raise NotImplementedError


    @abc.abstractmethod
    async def convert_component(self):
        raise NotImplementedError


    @abc.abstractmethod
    async def alive(self) -> bool:
        raise NotImplementedError


