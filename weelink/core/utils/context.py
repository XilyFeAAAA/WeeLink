class Context:
    """上下文，用于传递数据"""
    
    def __init__(self):
        self._data: dict[str, any] = {}
    
    def set(self, key: str, value: any) -> None:
        """设置上下文数据"""
        self._data[key] = value
    
    def get(self, key: str, default: any = None) -> any:
        """获取上下文数据"""
        return self._data.get(key, default)
    
    def has(self, key: str) -> bool:
        """检查是否存在指定键"""
        return key in self._data
    
    def delete(self, key: str) -> None:
        """删除指定键"""
        self._data.pop(key, None)
    
    def clear(self) -> None:
        """清空上下文"""
        self._data.clear()
    
    def copy_from(self, other: 'Context') -> None:
        """从另一个上下文复制数据"""
        self._data.update(other._data)