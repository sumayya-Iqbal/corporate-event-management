
import asyncio

from app.db import engine, Base
from app import models


async def create_tables():
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    print("Database tables created successfully!")

    await engine.dispose()


asyncio.run(create_tables())
