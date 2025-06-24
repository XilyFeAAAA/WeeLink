# standard library
import hashlib
from dataclasses import dataclass, field
from typing import Literal, Optional, Union

# local library
from .adapter import Adapter

@dataclass
class ConfigField:
    """适配器配置字段"""
    label: str
    key: str
    type: Literal["string", "boolean"]
    required: bool = False
    placeholder: str = ""
    description: str = ""
    default: Optional[any] = None

    def to_dict(self) -> dict:
        return {
            "label": self.label,
            "key": self.key,
            "type": self.type,
            "required": self.required,
            "placeholder": self.placeholder,
            "description": self.description,
            "default": self.default,
            "options": self.options
        }


@dataclass
class AdapterMetaData:
    
    """适配器名"""
    name: str
    
    """适配器介绍"""
    desc: str
    
    """微信版本"""
    wechat_version: str
    
    """微信平台"""
    wechat_platform: str
    
    """适配器配置字段"""
    fields: list[Union[dict, ConfigField]]
    
    """适配器对象"""
    cls: type[Adapter]
    
    """适配器ID"""
    id: str = field(default_factory=str)
    
    def __post_init__(self):
        unique_str = f"{self.name}_{self.cls.__name__}"
        self.id = hashlib.md5(unique_str.encode()).hexdigest()
    
    def __repr__(self):
        return (f"<AdapterMetaData name={self.name!r}, desc={self.desc!r}, "
                f"id={self.id!r}>")
    
    def get_fields(self) -> list[dict]:
        """获取字段的字典表示"""
        if not self.fields:
            return []
        
        result = []
        for field in self.fields:
            if isinstance(field, ConfigField):
                result.append(field.to_dict())
            elif isinstance(field, dict):
                result.append(field)
            else:
                raise Exception("错误的适配器配置项类型")
        return result