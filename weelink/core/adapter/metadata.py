# standard library
import uuid
from dataclasses import dataclass

# local library
from .adapter import Adapter

@dataclass
class AdapterMetaData:
    
    """适配器名"""
    name: str
    
    """适配器介绍"""
    desc: str
    
    """适配器对象"""
    cls: type[Adapter]
    
    """适配器ID"""
    id: str = str(uuid.uuid4())
    
    
    def __repr__(self):
        return (f"<AdapterMetaData name={self.name!r}, desc={self.desc!r}, "
                f"id={self.id!r}>")