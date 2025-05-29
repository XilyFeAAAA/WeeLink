# WeeLink

WeeLink是一个独立的微信机器人框架，需要自己搭建微信协议层。该框架提供了丰富的功能接口，让开发者可以轻松构建自己的微信机器人应用。

目前项目只完成了最基础的功能，plugin、状态管理和数据存储较为简陋，并且没有后台功能，在后续版本会进行更新。


## 免责声明

本项目仅供技术研究和学习交流，请勿用于非法用途。使用本项目所产生的一切后果由使用者自行承担。本项目不保证与微信官方的兼容性，微信官方可能随时更改其API或封禁使用自动化工具的账号。

## 主要功能

- **插件系统**：支持通过插件扩展机器人功能
- **多种消息类型**：支持文本、语音、图片、视频等多种消息类型
- **消息缓存**：使用Redis进行消息缓存，提高性能
- **Mixin机制**：通过Mixin机制扩展功能
- **规则匹配**：支持关键词、正则表达式等多种消息匹配方式

## 开发文档

如果你想开发自己的插件或者扩展WeeLink的功能，请参考以下开发文档：

- [插件开发指南](dev.md) - 详细介绍了如何创建和开发WeeLink插件
- [API参考文档](dev.md#bot-api-参考) - Bot API的完整参考
- [消息类型与数据模型](dev.md#数据类型与消息类型) - 了解WeeLink支持的消息类型
- [匹配规则系统](dev.md#匹配规则-on_响应机制) - 学习如何使用匹配规则处理消息
- [定时任务开发](dev.md#定时任务) - 如何创建和管理定时任务


## 目录结构

```
WeeLink/
├── config.json         # 主配置文件
├── status.toml         # 账号状态配置
├── main.py             # 程序入口文件
├── pyproject.toml      # 项目依赖配置
├── protocol/           # 微信协议目录
│   └── pad3/           # pad3协议实现
│       └── main.exe    # pad3协议执行文件
├── src/                # 源代码目录
│   ├── bot.py          # 机器人核心模块
│   ├── config.py       # 配置模块
│   ├── error.py        # 错误处理
│   ├── model.py        # 数据模型
│   ├── plugin.py       # 插件系统
│   ├── message/        # 消息处理模块
│   ├── matcher/        # 消息匹配模块
│   ├── mixin/          # 混入功能模块
│   ├── manager/        # 管理模块
│   └── utils/          # 工具函数
└── plugins/            # 插件目录
    ├── echo/           # 示例插件：消息回显
    └── ...             # 其他插件
```

## 协议支持

项目默认适配xxxbot的pad3的855微信协议，可以运行`protocol/pad3/main.exe`启动协议服务。如果想要接入其他微信协议，可以自己搭建协议，在`src/mixin`文件夹下参照xxxpad编写相应的接口适配即可。

## 安装与运行

### 环境要求

- Python 3.11+
- Redis

### 安装步骤

1. **安装Redis**

   根据您的操作系统安装Redis:
   - Windows: 下载并安装[Redis for Windows](https://github.com/microsoftarchive/redis/releases)
   - Linux: `sudo apt install redis-server`
   - macOS: `brew install redis`

2. **安装Python环境**

   推荐使用[uv](https://github.com/astral-sh/uv)来管理Python环境:

   ```bash
   # 安装uv
   pip install uv
   
   # 创建虚拟环境
   uv venv
   
   # 激活虚拟环境
   # Windows
   .venv\Scripts\activate
   # Linux/macOS
   source .venv/bin/activate
   ```

3. **安装依赖**

   ```bash
   uv pip install -r requirements.txt
   # 或者使用pyproject.toml
   uv pip install -e .
   ```

4. **配置项目**

   编辑`config.json`和`status.toml`文件，详见下方配置说明。

5. **运行项目**

   ```bash
   uv run main.py
   ```

## 配置文件说明

### config.json

主要配置项目的运行参数：

```json
{
    "DELETE_TMP_INTERVAL": 120,
    "IMG_EXPIRE": 120,
    "VOICE_EXPIRE": 120,
    "MESSAGE_QUEUE": {
        "enable": true,
        "interval": 2.0
    },
    "WHITELIST": {
        "enable": false,
        "users": [],
        "chatrooms": []
    },
    "BASEURL": "http://127.0.0.1:9000",
    "REDIS_HOST": "127.0.0.1",
    "REDIS_PORT": 6379,
    "REDIS_PASSWORD": "",
    "REDIS_DB": 0
}
```

- `DELETE_TMP_INTERVAL`: 临时文件删除间隔（秒）
- `IMG_EXPIRE`: 图片缓存过期时间（秒）
- `VOICE_EXPIRE`: 语音缓存过期时间（秒）
- `MESSAGE_QUEUE`: 消息队列配置
- `WHITELIST`: 白名单配置
- `BASEURL`: 微信协议API基础URL
- `REDIS_*`: Redis服务器配置

### status.toml

管理微信账号状态信息(由项目自行维护)：

```toml
[[accounts]]
uuid = "账号UUID"
wxid = "微信ID"
nickname = "昵称"
alias = "别名"
phone = "手机号"
is_logged = false
device_name = "设备名称"
device_id = "设备ID"
```

每个账号需要配置上述信息，`is_logged`表示是否已登录。 