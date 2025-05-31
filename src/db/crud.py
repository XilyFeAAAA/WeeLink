from .model import Account
from .engine import async_session
from sqlalchemy import select


async def add_account(wxid: str, uuid: str, nickname: str, alias: str, 
                      phone: str, device_name: str, device_id: str) -> None:
    """添加账户"""
    
    acc = Account(wxid=wxid,uuid=uuid,nickname=nickname,alias=alias,phone=phone,device_id=device_id,device_name=device_name)
    print(f"调用add_account {acc}")
    async with async_session.begin() as session:
        # 先检查是否已存在同样的wxid账户
        query = select(Account).where(Account.wxid == wxid)
        existing_acc = await session.execute(query)
        existing_acc = existing_acc.scalars().first()
        
        if existing_acc:
            raise Exception(f"账户已存在: {wxid}")
        session.add(acc)

async def update_account(wxid: str, **kwargs) -> Account:
    """更新账户信息"""
    async with async_session.begin() as session:
        query = select(Account).where(Account.wxid == wxid)
        result = await session.execute(query)
        account = result.scalars().first()
        
        if not account:
            return None
        
        for key, value in kwargs.items():
            if hasattr(account, key):
                setattr(account, key, value)
        return account
        

async def delete_account(wxid: str) -> None:
    """删除账户"""
    async with async_session.begin() as session:
        query = select(Account).where(Account.wxid == wxid)
        result = await session.execute(query)
        account = result.scalars().first()
        
        if not account:
            raise Exception(f"账户不存在: {wxid}")
        
        await session.delete(account)


async def get_account_by_wxid(wxid: str) -> Account:
    """通过wxid查询账户"""
    async with async_session() as session:
        query = select(Account).where(Account.wxid == wxid)
        result = await session.execute(query)
        account = result.scalars().first()
        
        if not account:
            raise Exception(f"账户不存在: {wxid}")
        
        return account


async def get_all_accounts() -> list[Account]:
    """获取所有账户"""
    async with async_session() as session:
        query = select(Account)
        result = await session.execute(query)
        accounts = result.scalars().all()
        
        return accounts



