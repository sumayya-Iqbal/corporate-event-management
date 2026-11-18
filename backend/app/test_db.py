import asyncio
from sqlalchemy import text
from app.db import engine


async def test_connection():
    try:
        async with engine.connect() as connection:
            result = await connection.execute(text("SELECT 1"))

            print("SUCCESS! Database connected.")
            print("Test result:", result.scalar())

    except Exception as error:
        print("DATABASE CONNECTION FAILED")
        print("Error:", repr(error))

    finally:
        await engine.dispose()


asyncio.run(test_connection())