class DocsMixin:
    
    @staticmethod
    def docs() -> str:
        return """# WechatPad855 适配器 API 文档

## 目录

- [登录相关](#登录相关)
- [消息相关](#消息相关)
- [工具相关](#工具相关)
- [账户相关](#账户相关)
- [好友相关](#好友相关)
- [群聊相关](#群聊相关)
- [二次API](#二次api)

## 登录相关

### api_login
执行登录流程，尝试多种登录方式。

```python
async def api_login(self)
```

登录流程：
1. 尝试获取个人资料
2. 若失败，尝试获取缓存信息
3. 若有缓存，尝试二次登录
4. 若二次登录失败，尝试唤醒登录
5. 若唤醒失败，尝试二维码登录
6. 若无缓存，直接尝试二维码登录

### api_get_cached_info
获取缓存的登录信息。

```python
async def api_get_cached_info(self)
```

**参数**：无需额外参数

**返回值**：缓存的登录信息或None

### api_twice_login
尝试二次自动登录。

```python
async def api_twice_login(self)
```

**参数**：无需额外参数

**返回值**：登录结果数据或错误日志

### api_revoke_login
唤醒登录。

```python
async def api_revoke_login(self, device_name: str)
```

**参数**：
- `device_name`: 设备名称

**返回值**：登录成功返回True，失败返回False

### api_qrcode_login
二维码登录。

```python
async def api_qrcode_login(self, device_name: str, device_id: str)
```

**参数**：
- `device_name`: 设备名称
- `device_id`: 设备ID

**返回值**：无直接返回值，登录成功会设置wxid等属性

### api_check_login
检查登录状态。

```python
async def api_check_login(self, uuid: str)
```

**参数**：
- `uuid`: 登录二维码UUID

**返回值**：
- 登录成功：(True, 账号信息)
- 等待扫码：(False, 过期时间)

### api_start_auto_heartbeat
开启自动心跳。

```python
async def api_start_auto_heartbeat(self)
```

**参数**：无需额外参数

**返回值**：无直接返回值，成功会记录日志

### api_heartbeat
发送心跳包。

```python
async def api_heartbeat(self)
```

**参数**：无需额外参数

**返回值**：心跳成功返回True，否则返回False

## 消息相关

### api_sync_message
同步消息。

```python
@require_login
async def api_sync_message(self)
```

**参数**：无需额外参数

**返回值**：
- 成功：(True, 消息数据)
- 失败：(False, 错误信息)

### api_send_text
发送文本消息。

```python
@require_login
async def api_send_text(self, to_wxid: str, content: str, at: str = "", type: int = 1)
```

**参数**：
- `to_wxid`: 接收者wxid
- `content`: 消息内容
- `at`: @的用户wxid，多个用逗号分隔
- `type`: 消息类型，默认为1（文本）

**返回值**：发送结果数据

### api_send_image
发送图片消息。

```python
@require_login
async def api_send_image(self, to_wxid: str, base64: str)
```

**参数**：
- `to_wxid`: 接收者wxid
- `base64`: 图片的base64编码

**返回值**：发送结果数据

### api_send_voice
发送语音消息。

```python
@require_login
async def api_send_voice(self, to_wxid: str, base64: str, type: int, voice_time: int)
```

**参数**：
- `to_wxid`: 接收者wxid
- `base64`: 语音的base64编码
- `type`: 音频类型
- `voice_time`: 语音时长（毫秒）

**返回值**：发送结果数据

### api_send_video
发送视频消息。

```python
@require_login
async def api_send_video(self, to_wxid: str, base64: str, image_base64: str, play_length: int)
```

**参数**：
- `to_wxid`: 接收者wxid
- `base64`: 视频的base64编码
- `image_base64`: 视频封面的base64编码
- `play_length`: 视频时长（秒）

**返回值**：发送结果数据

### api_share_card
分享名片。

```python
@require_login
async def api_share_card(self, to_wxid: str, card_wxid: str, card_nickname: str, card_alias: str)
```

**参数**：
- `to_wxid`: 接收者wxid
- `card_wxid`: 名片用户的wxid
- `card_nickname`: 名片用户的昵称
- `card_alias`: 名片用户的别名

**返回值**：发送结果数据

### api_send_link
发送分享链接消息。

```python
@require_login
async def api_send_link(self, to_wxid: str, title: str, desc: str, url: str, thumb_url: str)
```

**参数**：
- `to_wxid`: 接收者wxid
- `title`: 链接标题
- `desc`: 链接描述
- `url`: 链接URL
- `thumb_url`: 缩略图URL

**返回值**：发送结果数据

### api_revoke_message
撤回消息。

```python
@require_login
async def api_revoke_message(self, client_msg_id: int, create_time: int, new_msg_id: int, to_user_name: str)
```

**参数**：
- `client_msg_id`: 客户端消息ID
- `create_time`: 消息创建时间
- `new_msg_id`: 新消息ID
- `to_user_name`: 接收者用户名

**返回值**：撤回结果数据

### api_send_app
发送APP消息。

```python
@require_login
async def api_send_app(self, to_wxid: str, xml: str, type: int) -> tuple[int, int, int]
```

**参数**：
- `to_wxid`: 接收者wxid
- `xml`: XML内容
- `type`: 消息类型

**返回值**：(client_msg_id, create_time, new_msg_id)

## 工具相关

### api_download_chunk_image
分段下载图片。

```python
@require_login
async def api_download_chunk_image(self, msg_id: str, to_wxid: str, data_len: int, sta_pos: int, download_size: int) -> bytes
```

**参数**：
- `msg_id`: 消息ID
- `to_wxid`: 接收者wxid
- `data_len`: 数据总长度
- `sta_pos`: 起始位置
- `download_size`: 下载大小

**返回值**：图片数据（bytes）或None

### api_download_cdn_image
从CDN下载图片。

```python
@require_login
async def api_download_cdn_image(self, aeskey: str, cdnmidimgurl: str) -> str
```

**参数**：
- `aeskey`: 文件AES密钥
- `cdnmidimgurl`: CDN图片URL

**返回值**：图片数据

### api_download_voice
下载语音文件。

```python
@require_login
async def api_download_voice(self, msg_id: str, voiceurl: str, length: int) -> str
```

**参数**：
- `msg_id`: 消息ID
- `voiceurl`: 语音URL
- `length`: 语音长度

**返回值**：语音数据

### api_download_file
下载附件。

```python
@require_login
async def api_download_file(self, attach_id: str) -> dict
```

**参数**：
- `attach_id`: 附件ID

**返回值**：附件数据

### api_download_chunk_video
下载视频。

```python
@require_login
async def api_download_chunk_video(self, msg_id: str, to_wxid: str, data_len: int, sta_pos: int, download_size: int) -> str
```

**参数**：
- `msg_id`: 消息ID
- `to_wxid`: 接收者wxid
- `data_len`: 数据总长度
- `sta_pos`: 起始位置
- `download_size`: 下载大小

**返回值**：视频数据或None

### api_set_step
设置步数。

```python
@require_login
async def api_set_step(self, count: int) -> bool
```

**参数**：
- `count`: 步数

**返回值**：设置成功返回True

## 账户相关

### api_get_profile
获取个人资料。

```python
async def api_get_profile(self) -> dict
```

**参数**：无需额外参数

**返回值**：个人资料数据或None

## 好友相关

### api_get_range_friends
获取指定范围的好友列表。

```python
@require_login
async def api_get_range_friends(self, wx_seq: int, chatroom_seq: int)
```

**参数**：
- `wx_seq`: 微信联系人序列号
- `chatroom_seq`: 群聊联系人序列号

**返回值**：好友列表数据

### api_get_friends
获取所有好友列表。

```python
@require_login
async def api_get_friends(self) -> list[str]
```

**参数**：无需额外参数

**返回值**：好友wxid列表

### api_get_friend_info
获取好友详细信息。

```python
@require_login
async def api_get_friend_info(self, to_wxid: str) -> list[dict]
```

**参数**：
- `to_wxid`: 好友wxid

**返回值**：好友详细信息列表

## 群聊相关

### api_get_chatroom_info
获取群聊详情（不含公告）。

```python
@require_login
async def api_get_chatroom_info(self, chatroom_id: str)
```

**参数**：
- `chatroom_id`: 群聊ID

**返回值**：群聊详情或None

### api_get_chatroom_member
获取群成员列表。

```python
@require_login
async def api_get_chatroom_member(self, chatroom_id: str)
```

**参数**：
- `chatroom_id`: 群聊ID

**返回值**：群成员列表或空列表

## 二次API

### get_chatroom
获取群聊信息（带缓存）。

```python
async def get_chatroom(self, chatroom_id: str) -> Chatroom
```

**参数**：
- `chatroom_id`: 群聊ID

**返回值**：Chatroom对象

### get_chatroom_member
获取群成员信息。

```python
async def get_chatroom_member(self, chatroom_id: str, wxid: str) -> ChatroomMember
```

**参数**：
- `chatroom_id`: 群聊ID
- `wxid`: 成员wxid

**返回值**：ChatroomMember对象或None

### get_friend
获取好友信息（带缓存）。

```python
async def get_friend(self, wxid: str) -> Friend
```

**参数**：
- `wxid`: 好友wxid

**返回值**：Friend对象 """