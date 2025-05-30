from src.db import update_account, add_account, get_all_accounts
from src.utils import logger
import questionary

class StatusManager:
    
    def __init__(self) -> None:
        self.uuid: str = ""
        self.wxid: str = ""
        self.nickname: str = ""
        self.alias: str = ""
        self.phone: str = ""
        self.device_name: str = ""
        self.device_id: str = ""


    async def save(self):
        """保存账户信息"""
        update = {
            "uuid": self.uuid,
            "nickname": self.nickname,
            "alias": self.alias,
            "phone": self.phone,
            "device_name": self.device_name,
            "device_id": self.device_id
        }
        try:
            if (await update_account(wxid=self.wxid, **update)) is None:
                await add_account(wxid=self.wxid, **update)
        except Exception as e:
            logger.error(f"保存账户信息错误：{e}")
            raise
        

    async def load(self):
        NEW_ACCOUNT_OPTION = "登录新账户"
        
        try:
            accounts = await get_all_accounts()
            if not accounts:
                return
        except Exception as e:
            logger.error(f"读取账户信息错误：{e}")
            raise
        

        choices = [acc.nickname for acc in accounts] + [NEW_ACCOUNT_OPTION]
        
        selected_username = await questionary.select(
            "请选择要登录的账号：",
            choices=choices
        ).ask_async()

        if selected_username == NEW_ACCOUNT_OPTION:
            return

        selected_acc= next((acc for acc in accounts if acc.nickname == selected_username), None)

        if selected_acc:
            self.wxid = selected_acc.wxid
            self.uuid = selected_acc.uuid
            self.nickname = selected_acc.nickname
            self.alias = selected_acc.alias
            self.phone = selected_acc.phone
            self.device_name = selected_acc.device_name
            self.device_id = selected_acc.device_id
            logger.info(f"已加载账户 {selected_username} 的状态。")
        else:
            raise ValueError(f"选择的账户 {selected_username} 数据异常。")