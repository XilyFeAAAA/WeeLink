# WeeLink

WeeLink是一个独立的微信机器人框架，需要自己搭建微信协议层。该框架提供了丰富的功能接口，让开发者可以轻松构建自己的微信机器人应用。

目前项目只完成了最基础的功能，plugin、状态管理和数据存储较为简陋，并且没有后台功能，在后续版本会进行更新。

## 免责声明

本项目仅供技术研究和学习交流，请勿用于非法用途。使用本项目所产生的一切后果由使用者自行承担。本项目不保证与微信官方的兼容性，微信官方可能随时更改其API或封禁使用自动化工具的账号。


## TODO
1. 完善撤回消息，可能改用 MongoDB
2. 发送 语音 文件 视频
3. 后台 web
4. modcontacts 重写


## 主要功能

- **插件系统**：支持通过插件扩展机器人功能
- **多种消息类型**：支持文本、语音、图片、视频等多种消息类型
- **消息缓存**：使用Redis进行消息缓存，提高性能
- **Mixin机制**：通过Mixin机制扩展功能
- **规则匹配**：支持关键词、正则表达式等多种消息匹配方式
- **状态管理**：使用MySQL数据库进行状态管理

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
├── main.py             # 程序入口文件
├── create_db.py        # 数据库初始化脚本
├── pyproject.toml      # 项目依赖配置
├── server/             # 微信协议目录
├── src/                # 源代码目录
│   ├── bot.py          # 机器人核心模块
│   ├── config.py       # 配置模块
│   ├── error.py        # 错误处理
│   ├── schema.py        # 数据模型
│   ├── plugin.py       # 插件系统
│   ├── message/        # 消息处理模块
│   ├── matcher/        # 消息匹配模块
│   ├── mixin/          # 混入功能模块
│   ├── manager/        # 管理模块
│   │   └── status.py   # 状态管理器
│   ├── db/             # 数据库模块
│   │   ├── schema.py    # 数据库模型
│   │   ├── crud.py     # CRUD操作
│   │   ├── create.py   # 数据库创建
│   │   ├── engine.py   # 数据库引擎
│   │   └── base.py     # 数据库基类
│   └── utils/          # 工具函数
└── plugins/            # 插件目录
    ├── echo/           # 示例插件：消息回显
    └── ...             # 其他插件
```

## 协议支持

项目默认适配xxxbot的pad3的855微信协议，可以运行`server/pad3/main.exe`启动协议服务。如果想要接入其他微信协议，可以自己搭建协议，在`src/mixin`文件夹下参照xxxpad编写相应的接口适配即可。

### Mixin开发说明

如果要添加新的协议支持，需要实现以下Mixin接口：

- **LoginMixIn**: 登录相关接口
- **MessageMixIn**: 消息处理接口
- **UserMixIn**: 用户相关接口
- **ChatroomMixIn**: 群聊相关接口
- **FriendMixIn**: 好友相关接口
- **ToolMixIn**: 工具相关接口
- **ProtocolMixIn**: 协议相关接口

所有Mixin必须实现通用接口，并对外提供`loop`生成器，用于获取消息数据。无论使用WebSocket还是轮询方式，都需要确保能返回标准格式的数据。例如：

```python
async def loop(self):
    # 这里实现消息获取逻辑，可以是WebSocket连接或轮询
    while True:
      yield await self.get_message()
```

## 安装与运行

### 环境要求

- Python 3.11+
- Redis
- MySQL

### 安装步骤

1. **安装Redis**

   根据您的操作系统安装Redis:
   - Windows: 下载并安装[Redis for Windows](https://github.com/microsoftarchive/redis/releases)
   - Linux: `sudo apt install redis-server`
   - macOS: `brew install redis`

2. **安装MySQL**

   根据您的操作系统安装MySQL:
   - Windows: 下载并安装[MySQL Installer](https://dev.mysql.com/downloads/installer/)
   - Linux: `sudo apt install mysql-server`
   - macOS: `brew install mysql`

3. **安装Python环境**

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

4. **安装依赖**

   ```bash
   uv pip install -r requirements.txt
   # 或者使用pyproject.toml
   uv pip install -e .
   ```

5. **配置项目**

   编辑`config.json`文件，配置Redis和MySQL连接信息，详见下方配置说明。

6. **初始化数据库**

   ```bash
   uv run create_db.py
   ```

7. **运行项目**

   ```bash
   uv run main.py
   ```

## 配置文件说明


- `DELETE_TMP_INTERVAL`: 临时文件删除间隔（秒）
- `IMG_EXPIRE`: 图片缓存过期时间（秒）
- `VOICE_EXPIRE`: 语音缓存过期时间（秒）
- `MESSAGE_QUEUE`: 消息队列配置
- `BASEURL`: 微信协议API基础URL
- `REDIS_*`: Redis服务器配置
- `MYSQL_*`: MySQL服务器配置 