from src.db.model import Account
from src.db.engine import db


class AccountRepository:
    
    @staticmethod
    async def add_account(wxid: str, uuid: str, nickname: str, alias: str, 
                      phone: str, device_name: str, device_id: str) -> None:
        """添加账户"""
        if await Account.find_one(Account.wxid == wxid):
            raise Exception(f"创建账户失败：wxid={wxid} 已存在")
        
        account = Account(
            uuid=uuid,
            wxid=wxid,
            nickname=nickname,
            alias=alias,
            phone=phone,
            device_id=device_id,
            device_name=device_name
        )
        try:
            await account.insert()
        except Exception as e:
            raise Exception(f"创建账户失败：{str(e)}")
        
        
    @staticmethod
    async def update_account(wxid: str, update) -> None:
        """更新账户信息"""
        account = await Account.find_one(Account.wxid == wxid)
        if not account:
            raise Exception(f"更新账户失败：wxid={wxid} 不存在")
        
        try:
            account = await account.update({"$set": update})
            await account.save()
        except Exception as e:
            raise Exception(f"更新账户失败：{str(e)}")

        
    @staticmethod
    async def delete_account(wxid: str) -> None:
        """删除账户"""
        account = await Account.find_one(Account.wxid == wxid)
        if not account:
            raise Exception(f"删除账户失败：wxid={wxid} 不存在")
        
        try:
            await account.delete()
        except Exception as e:
            raise Exception(f"删除账户失败：{str(e)}")


    @staticmethod
    async def get_all_accounts() -> list[Account]:
        """获取所有账户"""
        return await Account.find_all().to_list()



