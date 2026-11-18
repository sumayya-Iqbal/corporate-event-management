
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession
)

from sqlalchemy import text
from app.config import settings

# Create an asynchronous database engine
engine = create_async_engine(
    settings.DATABASE_URL,
    connect_args={"ssl": "require"},
    pool_pre_ping=True,
    echo=False
)

# Create a session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


# Provide database sessions to API endpoints
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


# Test database connection
async def test_database_connection():
    async with AsyncSessionLocal() as session:
        result = await session.execute(text("SELECT 1"))
        return result.scalar()



from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text

from app.config import settings


# Parent class for all database models
class Base(DeclarativeBase):
    pass


# Create asynchronous database engine
engine = create_async_engine(
    settings.DATABASE_URL,
    connect_args={"ssl": "require"},
    pool_pre_ping=True,
    echo=False
)


# Create database sessions
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


# Provide a database session to API endpoints
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


# Test database connection
async def test_database_connection():
    async with AsyncSessionLocal() as session:
        result = await session.execute(text("SELECT 1"))
        return result.scalar()
