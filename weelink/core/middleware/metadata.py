# standard library
from dataclasses import dataclass

# local libray
from .base import Middleware

@dataclass
class MiddlewareMetaData:
    
    """中间件名"""
    name: str
    
    """中间件描述"""
    desc: str
    
    """中间件实例"""
    obj: Middleware
    
    """中间件类"""
    cls: type[Middleware]