from src.mixin.base import BaseMixIn
from src.utils import logger
import functools
import questionary
import toml
import os

class StatusMixIn(BaseMixIn):
    
    # 白名单字段
    STATUS_FIELDS = [
        'uuid', 'wxid', 'nickname', 'alias', 'phone', 'is_logged', 'device_name', 'device_id'
    ]
    
    def __init__(self):
        self.uuid: str = ""
        self.wxid: str = ""
        self.nickname: str = ""
        self.alias: str = ""
        self.phone: str = ""
        self.is_logged: bool = False
        self.device_name: str = ""
        self.device_id: str = ""
        
    
    async def load_status(self):

        NEW_ACCOUNT_OPTION = "登录新账户"
        
        if not os.path.exists("status.toml"):
            logger.info("状态文件 status.toml 不存在，正在创建...")
            with open("status.toml", 'w', encoding='utf-8') as f:
                pass
        try:
            with open("status.toml", 'r', encoding='utf-8') as f:
                accounts = toml.load(f).get("accounts",[])
        except FileNotFoundError:
            return logger.error(f"状态文件 status.toml 未找到。")
        except toml.TomlDecodeError:
            logger.error(f"状态文件 status.toml 格式错误。")
            raise
        
        
        if not accounts:
            return

        choices = [acc['nickname'] for acc in accounts] + [NEW_ACCOUNT_OPTION]
        
        selected_username = await questionary.select(
            "请选择要登录的账号：",
            choices=choices
        ).ask_async()

        if selected_username is None:
            raise SystemExit("用户取消选择账号，程序退出。") 

        if selected_username == NEW_ACCOUNT_OPTION:
            return

        # 使用 next 查找选定的账户
        selected_account = next((acc for acc in accounts if acc['nickname'] == selected_username), None)

        if selected_account:
            for key, value in selected_account.items():
                setattr(self, key, value)
            logger.info(f"已加载账户 {selected_username} 的状态。")
        else:
            raise ValueError(f"选择的账户 {selected_username} 数据异常。")

    def save_status(self):
        # TODO 太简陋了，后面修改
        current_account_data = {}
        for field_name in self.STATUS_FIELDS:
            if hasattr(self, field_name):
                current_account_data[field_name] = getattr(self, field_name)
            else:
                logger.warning(f"尝试保存状态时，self 对象缺少 STATUS_FIELDS 中的字段: {field_name}")

        if not current_account_data.get("nickname"): # 再次确认 nickname 在提取的数据中
            current_account_data["nickname"] =  "unknown"
            return

       
        all_data = {"accounts": []}
        try:
            with open("status.toml", 'r', encoding='utf-8') as f:
                all_data = toml.load(f)
                if not isinstance(all_data.get('accounts'), list):
                    logger.warning(f"status.toml 中 'accounts' 不是列表或不存在，将重置。")
                    all_data['accounts'] = []
        except FileNotFoundError:
            return logger.info(f"status.toml 未找到，将创建新文件。")
        except toml.TomlDecodeError:
            return logger.error(f"解析 status.toml 失败，请检查文件格式。状态未保存。")

        accounts_list = all_data.get('accounts', [])
        

        account_found_and_updated = False
        for i, acc in enumerate(accounts_list):
            if acc.get('wxid') == self.wxid:
                accounts_list[i] = current_account_data
                account_found_and_updated = True
                logger.info(f"账户 {self.wxid} 的状态已更新。")
                break
        
        if not account_found_and_updated:
            accounts_list.append(current_account_data) 
            logger.info(f"新账户 {self.username} 的状态已添加。")

        all_data['accounts'] = accounts_list

        
        try:
            with open("status.toml", 'w', encoding='utf-8') as f:
                toml.dump(all_data, f)
            logger.info(f"状态已成功保存到 status.toml。")
        except Exception as e:
            logger.error(f"保存状态到 status.toml 失败: {e}")
    
    

    async def is_logged_in(self):
        try:
            await self.get_profile()
            self.is_logged = True
            return True
        except:
            return False