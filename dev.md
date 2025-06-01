# WeeLink 插件开发者文档

## 目录

1. [插件开发基础](#插件开发基础)
2. [数据类型与消息类型](#数据类型与消息类型)
3. [匹配规则 (on_响应机制)](#匹配规则-on_响应机制)
4. [Bot API 参考](#bot-api-参考)
5. [文件存储访问](#文件存储访问)
6. [Redis 使用](#redis-使用)
7. [定时任务](#定时任务)
8. [插件开发范例](#插件开发范例)

## 插件开发基础

### 创建插件

插件应放在`plugins`目录下，每个插件应创建独立目录，并包含`main.py`文件：

```
plugins/
  ├── my_plugin/
  │     ├── main.py
  │     └── other_files.py
```

### 插件基本结构

```python
from src.plugin import PluginBase
from src.matcher.rule import to_me, from_chatroom

class MyPlugin(PluginBase):
    # 插件元数据（必填）
    __description__ = "插件描述"
    __author__ = "作者名"
    __version__ = "1.0.0"
    __enabled__ = True  # 是否默认启用
    
    # 异步初始化方法（可选）
    async def async_init(self, bot):
        # 在这里进行插件初始化
        pass
```

## 数据类型与消息类型

### DataType 枚举

系统定义了以下主要数据类型：

```python
class DataType(Enum):
    TEST = auto()
    ADDMSG = auto()        # 新消息
    MODCONTACTS = auto()   # 联系人变动
    DELCONTACTS = auto()   # 联系人删除
    OFFLINE = auto()       # 离线
```

### AddMsgType 枚举

消息类型包括：

```python
class AddMsgType(int, Enum):
    UNKNOWN = 0
    TEXT = 1               # 文本消息
    IMAGE = 3              # 图片消息
    VOICE = 34             # 语音消息
    FRIENDADD = 37         # 好友添加
    POSSIBLE_FRIEND_MSG = 40  # 可能的好友消息
    NAMECARD = 42          # 名片
    VIDEO = 43             # 视频
    EMOJI = 47             # 表情
    LOCATION = 48          # 位置
    APPMSG = 49            # XML消息：公众号/文件/小程序/引用/转账/红包等
    SYNC = 51              # 状态同步
    GROUPOP = 10000        # 群操作：被踢出/更换群主/修改群名称
    SYSTEMMSG = 10002      # 系统消息：撤回/拍一拍/成员被移出群聊等
```

### SystemMsgType 枚举

系统消息类型：

```python
class SystemMsgType(str, Enum):
    REVOKE = "revokemsg"                       # 撤回消息
    PAT = "pat"                                # 拍一拍
    KICKOUT = "kickout"                        # 踢出群聊
    DISMISS = "dismiss"                        # 解散群聊
    ANNOUNCEMENT = "mmchatroombarannouncememt" # 群公告
    TODO = "roomtoolstips"                     # 群待办
    EXTINFO = "ClientCheckGetExtInfo"          # 扩展信息
    FUNCTION = "functionmsg"                   # 功能消息
    TEMPLATE = "sysmsgtemplate"                # 系统模板消息
```

### ModContactType 枚举

联系人变动类型：

```python
class ModContactType(Enum):
    NICKNAME_CHANGED = auto()     # 昵称变更
    REMARK_CHANGED = auto()       # 备注变更
    OWNER_CHANGED = auto()        # 群主变更
    MEMBER_DECREASED = auto()     # 成员减少
    MEMBER_INCREASED = auto()     # 成员增加
    UNKNOWN = auto()              # 未知变动
```

### 消息类型详解

#### 通用消息属性

所有消息类型都包含以下属性：

```python
msg.from_wxid    # 发送人wxid
msg.to_wxid      # 接收人wxid
msg.msg_type     # 消息类型 (AddMsgType枚举)
msg.content      # 原始消息内容
msg.create_time  # 发送时间 (时间戳)
msg.source       # 消息来源 (CHATROOM/FRIEND/OTHER)
msg.sender       # 发送者对象 (群聊消息为ChatroomMember，私聊为Friend)
msg.chatroom     # 群聊对象 (仅群聊消息)
msg.type         # 数据类型 (DataType枚举)
```

#### 文本消息 (TextMessage)

```python
# 文本消息特有属性
msg.text         # 消息文本内容
msg.ats          # @的用户列表 (ChatroomMember对象列表)
msg.at_me        # 是否@了机器人 (布尔值)

# 使用示例
@PluginBase.on_text()
async def handle_text(self, bot, msg):
    print(f"收到文本: {msg.text}")
    print(f"是否@我: {msg.at_me}")
    for at in msg.ats:
        print(f"@了: {at.name}")
```

#### 图片消息 (ImageMessage)

```python
# 图片消息特有属性
msg.filepath     # 图片保存路径 (格式为md5+后缀，存储在tmp目录)
msg.md5          # 图片MD5值

# 使用示例
@PluginBase.on_image()
async def handle_image(self, bot, msg):
    print(f"收到图片，保存在: {msg.filepath}")
    # 可以使用PIL等库处理图片
    from PIL import Image
    img = Image.open(msg.filepath)
```

#### 语音消息 (VoiceMessage)

```python
# 语音消息特有属性
msg.filepath     # 语音文件保存路径 (格式为md5+后缀，存储在tmp目录)
msg.duration     # 语音时长(秒)

# 使用示例
@PluginBase.on_voice()
async def handle_voice(self, bot, msg):
    print(f"收到语音，时长: {msg.duration}秒")
    print(f"文件路径: {msg.filepath}")
```

#### 视频消息 (VideoMessage)

```python
# 视频消息特有属性
msg.filepath     # 视频文件保存路径 (格式为md5+后缀，存储在tmp目录)
msg.thumb_path   # 视频缩略图路径

# 使用示例
@PluginBase.on_video()
async def handle_video(self, bot, msg):
    print(f"收到视频: {msg.filepath}")
    print(f"缩略图: {msg.thumb_path}")
```

#### XML消息 (XmlMessage)

XML消息包括引用、文件、链接等多种类型，需要通过解析XML内容获取详细信息。

```python
# 引用消息示例
@PluginBase.on_text(addmsg_type=AddMsgType.APPMSG)
async def handle_xml(self, bot, msg):
    if isinstance(msg, XmlMessage):
        # 处理引用消息、文件、链接等
        pass
```

#### 系统消息 (SystemMessage)

系统消息包括撤回、拍一拍、群公告等多种类型。

```python
# 拍一拍消息示例
@PluginBase.on_pat()
async def handle_pat(self, bot, msg):
    print(f"{msg.sender.name} 拍了拍 {msg.patted_member.name}")
```

### ModContact 消息类型

ModContact消息用于处理联系人变动事件，如群成员增减、群名称变更等。

```python
# 群成员减少示例
@PluginBase.on_chatroom_decrease()
async def handle_decrease(self, bot, msg):
    print(f"{msg.decreased_members[0].name} 退出了群聊 {msg.chatroom.name}")
    
# 群成员增加示例
@PluginBase.on_chatroom_increase()
async def handle_increase(self, bot, msg):
    print(f"{msg.increased_members[0].name} 加入了群聊 {msg.chatroom.name}")
```

## 匹配规则 (on_响应机制)

### 基本匹配装饰器

系统提供多种消息匹配装饰器，用于定义处理函数触发条件：

#### 1. 消息类型匹配

```python
# 匹配任何文本消息
@PluginBase.on_text()

# 匹配图片消息
@PluginBase.on_image()

# 匹配语音消息
@PluginBase.on_voice()

# 匹配视频消息
@PluginBase.on_video()

# 匹配系统消息
@PluginBase.on_system()

# 匹配拍一拍消息
@PluginBase.on_pat()

# 匹配群公告消息
@PluginBase.on_announcement()

# 匹配群待办消息
@PluginBase.on_todo()
```

#### 2. 联系人变动匹配

```python
# 群成员减少事件
@PluginBase.on_chatroom_decrease()

# 群成员增加事件
@PluginBase.on_chatroom_increase()
```

#### 3. 文本内容匹配

```python
# 前缀匹配
@PluginBase.on_startswith(
    text="查询",              # 匹配前缀
    rules=[to_me()],         # 附加规则
    ignorecase=True          # 是否忽略大小写
)

# 后缀匹配
@PluginBase.on_endswith(
    text="吗",
    ignorecase=False
)

# 完全匹配
@PluginBase.on_fullmatch(
    text="你好机器人",
    ignorecase=True
)

# 关键词匹配
@PluginBase.on_keyword(
    keywords={"天气", "查询", "预报"},
    rules=[from_chatroom()]
)

# 正则表达式匹配
@PluginBase.on_regex(
    patterns=[r"天气\s*(.+)"],
    flags=0,  # 正则标志，如re.I
    rules=[to_me()]
)
```

### 规则组合

规则可以组合使用，通过`rules`参数传入列表：

```python
@PluginBase.on_keyword(
    keywords={"帮助"},
    rules=[to_me(), from_chatroom()]  # 同时满足多个规则
)
```

### 可用规则列表

```python
from src.matcher.rule import (
    keyword,         # 关键词匹配
    regex,           # 正则匹配
    startswith,      # 前缀匹配
    endswith,        # 后缀匹配
    fullmatch,       # 完全匹配
    to_me,           # 是否@机器人
    from_chatroom,   # 来自群聊
    from_friend      # 来自好友
)
```

## Bot API 参考

插件开发中常用的Bot API：

### 消息发送(目前仅实现文本发送)

```python
# 发送文本消息
await bot.send_text(msg.from_wxid, "回复内容")

# 发送图片
await bot.send_image(msg.from_wxid, "/path/to/image.jpg")

# 发送语音
await bot.send_voice(msg.from_wxid, "/path/to/voice.silk")

# 发送视频
await bot.send_video(msg.from_wxid, "/path/to/video.mp4")

# 发送表情
await bot.send_emoji(msg.from_wxid, "/path/to/emoji.gif")

# 发送文件
await bot.send_file(msg.from_wxid, "/path/to/file.zip")

# 回复消息（引用）
await bot.reply_message(msg, "这是回复内容")
```

### 群聊操作

```python
# 获取群成员列表
members = await bot.get_chatroom_members(chatroom_id)

# 获取群信息
chatroom = await bot.get_chatroom_info(chatroom_id)

# 邀请用户入群
await bot.invite_chatroom(chatroom_id, wxid)

# 踢出群成员
await bot.remove_chatroom_member(chatroom_id, wxid)

# 修改群名称
await bot.rename_chatroom(chatroom_id, "新群名")
```

### 好友操作

```python
# 获取好友列表
friends = await bot.get_friends()

# 获取好友信息
friend = await bot.get_friend_info(wxid)

# 设置好友备注
await bot.set_friend_remark(wxid, "新备注")
```


## 文件存储访问

插件可以使用临时文件夹存储数据，下载的媒体文件以MD5+后缀形式存储在tmp文件夹：

```python
import os

# 获取临时文件夹路径
tmp_dir = "tmp"
plugin_tmp_dir = os.path.join(tmp_dir, "my_plugin")

# 确保目录存在
os.makedirs(plugin_tmp_dir, exist_ok=True)

# 写入文件
file_path = os.path.join(plugin_tmp_dir, "data.txt")
with open(file_path, "w") as f:
    f.write("数据内容")

# 读取文件
with open(file_path, "r") as f:
    content = f.read()
```

## Redis 使用

插件可以使用Redis存储数据：

```python
# 获取Redis实例
redis = bot.redis

# Redis是单例模式，也可以通过utils获得
from src.utils import Redis
redis = Redis()

# 设置值
await redis.set(f"plugin:my_plugin:key", "value")

# 设置带过期时间的值（秒）
await redis.set(f"plugin:my_plugin:temp", "value", ex=3600)

# 获取值
value = await redis.get(f"plugin:my_plugin:key")

# 删除值
await redis.delete(f"plugin:my_plugin:key")

# 检查键是否存在
exists = await redis.exists(f"plugin:my_plugin:key")
```

## 定时任务

WeeLink使用APScheduler进行定时任务管理，通过ScheduleMixin提供定时功能：

```python
# 添加定时任务
bot.add_task(
    handle=self.my_task,       # 异步函数
    task_id="my-task-id",      # 任务ID
    trigger="interval",        # 触发器类型：'interval'、'cron'、'date'
    minutes=5                  # 时间间隔
)

# 添加cron定时任务
bot.add_task(
    handle=self.daily_task,
    task_id="daily-task",
    trigger="cron",
    hour=8,                    # 每天8点执行
    minute=0
)

# 取消任务
bot.cancel_task("my-task-id")
```

定时任务处理函数必须是异步函数：

```python
async def my_task(self):
    # 定时执行的代码
    print("这是一个定时任务")
```

## 插件开发范例

### 1. Echo插件示例

Echo插件演示了基本的消息处理：

```python
from src.message import TextMessage, VoiceMessage, ImageMessage
from src.bot import Bot
from src.plugin import PluginBase
from src.schema import MessageSource
from src.utils import logger


class Echo(PluginBase):
    
    __description__ = "消息提示"
    __author__ = "xilyfe"
    __version__ = "1.0.0"


    @PluginBase.on_text()
    async def echo_message(self, bot: Bot, msg: TextMessage):
        if msg.source == MessageSource.FRIEND:
            source_ = '私聊' 
            from_ = msg.sender.name
            
        else:
            source_ = '群聊'
            from_ = msg.chatroom.name
            
        logger.info(f"接受到{source_}{msg.from_wxid}文字消息,来自{from_},内容为{msg.text}")
    
    
    @PluginBase.on_voice()
    async def echo_voice(self, bot: Bot, msg: ImageMessage):
        if msg.source == MessageSource.FRIEND:
            source_ = '私聊' 
            from_ = msg.sender.name
            
        else:
            source_ = '群聊'
            from_ = msg.chatroom.name
            
        logger.info(f"接受到{source_}{msg.from_wxid}语音消息,来自{from_},文件位置:{msg.path}")
```

### 2. 群聊变动检测插件

GroupDetect插件演示了如何处理群成员变动：

```python
from src.message import ChatroomModify
from src.bot import Bot
from src.plugin import PluginBase


class GroupDetect(PluginBase):
    
    __description__ = "群聊变动提示"
    __author__ = "xilyfe"
    __version__ = "1.0.0"


    @PluginBase.on_chatroom_decrease()
    async def decrease_notice(self, bot: Bot, msg: ChatroomModify):
        """退群提示"""
        await bot.send_text(
            msg.chatroom.chatroom_id,
            f"👋 {', '.join([m.name for m in msg.decreased_members])} 已退出群聊"
        )
        
    @PluginBase.on_chatroom_increase()
    async def increase_notice(self, bot: Bot, msg: ChatroomModify):
        """入群提示"""
        await bot.send_text(
            msg.chatroom.chatroom_id,
            f"🎉 欢迎 {', '.join([m.name for m in msg.increased_members])} 加入群聊"
        )
```

### 3. 自动清理插件

AutoCleaner插件演示了如何使用定时任务清理临时文件：

```python
from src.bot import Bot
from src.plugin import PluginBase
from src.utils import logger, Redis
import os


class AutoCleaner(PluginBase):
    
    __description__ = "缓存文件自动清理"
    __author__ = "xilyfe"
    __version__ = "1.0.0"


    async def async_init(self, bot: Bot) -> None:
        """初始化"""
        bot.add_task(
            handle=self.cleaner,
            task_id="auto-cleaner",
            trigger="interval",
            minutes=60
        )
    
    
    async def cleaner(self) -> None:
        """清理tmp"""
        tmp_dir = os.path.join(os.getcwd(), "tmp")
        if not os.path.exists(tmp_dir):
            logger.info("tmp目录不存在，无需清理")
            return
        
        redis = Redis()
        to_del = []
        for fname in os.listdir(tmp_dir):
            if not await redis.exists(key=fname):
                to_del.append(fname)
        try:
            for file_name in to_del:
                file_path = os.path.join(tmp_dir, file_name)
                os.remove(file_path)
                logger.info(f"已删除过期缓存: {file_name}")
        except Exception as e:
            logger.error(f"删除缓存图片文件失败, 错误: {e}")
```

### 注意事项

1. 所有响应函数必须是异步函数，使用`async def`定义
2. 响应函数不可以重名，每个函数名必须唯一
3. 下载的媒体文件以MD5+后缀存储在tmp文件夹，可以通过auto_cleaner插件定时清理
4. 定时任务的处理函数必须是异步函数
