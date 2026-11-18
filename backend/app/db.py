
# Import tools for creating and managing asynchronous database connections.
from sqlalchemy.ext.asyncio import (
    create_async_engine,  # Creates the database engine.
    async_sessionmaker,   # Creates a factory for database sessions.
    AsyncSession          # Represents an asynchronous database session.
)

# Import DeclarativeBase to create the parent class for our models.
from sqlalchemy.orm import DeclarativeBase

# Import text() to execute raw SQL statements.
from sqlalchemy import text

# Import database configuration from config.py.
# This contains the DATABASE_URL loaded from environment settings.
from app.config import settings


# ==================================
# 1. BASE CLASS
# ==================================

# This is the parent class for all database models.
#
# User, Event, and Registration inherit from Base in models.py.
# SQLAlchemy uses this class to identify and manage our database tables.
class Base(DeclarativeBase):
    pass


# ==================================
# 2. DATABASE ENGINE
# ==================================

# Create an asynchronous database engine.
#
# The engine manages connections between our FastAPI application
# and the PostgreSQL database hosted on Neon.
engine = create_async_engine(

    # Connection URL loaded from our application settings.
    # It contains the database connection information.
    settings.DATABASE_URL,

    # Require SSL encryption for the database connection.
    # This is important when connecting to a hosted database such as Neon.
    connect_args={"ssl": "require"},

    # Check database connections before using them.
    # This helps detect connections that have become invalid.
    pool_pre_ping=True,

    # Disable SQL query logging in the terminal.
    # If set to True, SQLAlchemy prints generated SQL statements.
    echo=False
)


# ==================================
# 3. DATABASE SESSION FACTORY
# ==================================

# Create a factory that produces new asynchronous database sessions.
#
# A session is used to perform database operations such as:
# SELECT, INSERT, UPDATE, and DELETE.
AsyncSessionLocal = async_sessionmaker(

    # Use the engine created above for database connections.
    bind=engine,

    # Use SQLAlchemy's asynchronous session class.
    class_=AsyncSession,

    # Keep object attributes available after commit.
    #
    # If this were True, SQLAlchemy could expire object attributes
    # after committing, potentially requiring another database query.
    expire_on_commit=False
)


# ==================================
# 4. DATABASE DEPENDENCY
# ==================================

# This asynchronous generator provides a database session
# to FastAPI endpoints and other functions that need database access.
async def get_db():

    # Open a new database session.
    async with AsyncSessionLocal() as session:

        # yield provides the session to the API endpoint.
        #
        # After the endpoint finishes, the async with block closes
        # the session automatically, including when an error occurs.
        yield session


# ==================================
# 5. TEST DATABASE CONNECTION
# ==================================

# This function checks whether the application can communicate
# with the database successfully.
async def test_database_connection():

    # Open a temporary database session.
    async with AsyncSessionLocal() as session:

        # Execute a simple SQL query.
        # SELECT 1 does not change any database records.
        # It simply checks whether the database responds.
        result = await session.execute(text("SELECT 1"))

        # Extract and return the query result.
        # If the connection works, this returns 1.
        return result.scalar()
