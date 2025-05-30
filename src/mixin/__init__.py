# 导入通用 MixIn
from .plugin import PluginMixin
from .schedule import ScheduleMixin
from .protocol import ProtocolMixIn

import questionary
import os

# 获取当前脚本所在目录，即 mixin 文件夹
mixin_dir = os.path.dirname(__file__)

# 获取 mixin 文件夹下所有的子文件夹名称作为协议列表
# 排除 __pycache__ 等非协议文件夹
available_protocols = [
    d for d in os.listdir(mixin_dir)
    if os.path.isdir(os.path.join(mixin_dir, d)) and not d.startswith("__")
]

if not available_protocols:
    raise Exception("在 mixin 文件夹中没有找到可用的协议。")

# 让用户选择协议
selected_protocol = questionary.select(
    "请选择一个协议:",
    choices=available_protocols,
).ask()

if selected_protocol is None:
    # 用户可能按了 Ctrl+C 等取消了选择
    raise Exception("用户未选择协议。")

# 根据用户选择导入对应的 mixin
if selected_protocol == "xxxipad":
    from .xxxipad import (
        LoginMixIn,
        MessageMixIn,
        UserMixIn,
        ChatroomMixIn,
        FriendMixIn,
        ToolMixIn
    )
else:
    # 理论上不会到这里，因为选项是动态生成的
    raise Exception(f"未知协议: {selected_protocol}")

__all__ = [
    "PluginMixin",
    "ScheduleMixin",
    "LoginMixIn",
    "MessageMixIn",
    "UserMixIn",
    "ChatroomMixIn",
    "FriendMixIn",
    "ToolMixIn",
    "ProtocolMixIn"
]