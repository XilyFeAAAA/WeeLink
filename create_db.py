from src.db import init_models
from src.db.create import close_db_connection
import asyncio


async def setup_db():
    await init_models()
    await close_db_connection()

if __name__ == "__main__":
    asyncio.run(setup_db())