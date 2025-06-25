# local library
from weelink.core.internal.db.model import BotDocument


class BotRepository:
    
    @staticmethod
    async def add_bot(bot_config) -> None:
        """添加BOT"""
        if await BotDocument.find_one({"alias": bot_config.alias}):
            raise Exception(f"创建BotDocument失败 {bot_config.alias}已存在")
        bot_doc = BotDocument(
            alias=bot_config.alias,
            desc=bot_config.desc,
            auto_start=bot_config.auto_start,
            adapter_id=bot_config.adapter_id,
            adapter_name=bot_config.adapter_name,
            adapter_config=bot_config.adapter_config
        )
        try:
            await bot_doc.insert()
        except Exception as e:
            raise Exception(f"创建BotDocument失败：{str(e)}")
        
        
    @staticmethod
    async def update_bot(bot: "Bot") -> None:
        """更新信息"""
        bot_doc = await BotDocument.find_one({"alias": bot.alias})
        if not bot_doc:
            raise Exception(f"更新BotDocument失败 {bot.alias}不存在")
        
        update = {
            "desc": bot.desc,
            "auto_start": bot.auto_start,
            "adapter_name": bot.adapter_metadata.name,
            "adapter_config": bot.adapter_config
        }
        try:
            await bot_doc.update({"$set": update})
        except Exception as e:
            raise Exception(f"更新BotDocument失败：{str(e)}")

        
    @staticmethod
    async def delete_bot(bot) -> None:
        """删除BOT"""
        bot_doc = await BotDocument.find_one({"alias": bot.alias})
        if not bot_doc:
            raise Exception(f"删除BotDocument失败 {bot.alias}不存在")
        
        try:
            await bot_doc.delete()
        except Exception as e:
            raise Exception(f"删除BotDocument失败：{str(e)}")


    @staticmethod
    async def get_all_bots() -> list[BotDocument]:
        """获取所有账户"""
        return await BotDocument.find_all().to_list()