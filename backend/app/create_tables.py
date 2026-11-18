
# Import asyncio to run asynchronous Python functions.
import asyncio

# Import the database engine and Base class.
#
# engine manages the connection to PostgreSQL.
# Base contains the metadata for all SQLAlchemy models.
from app.db import engine, Base

# Import models so SQLAlchemy knows about the User, Event,
# and Registration classes.
#
# This import is important because SQLAlchemy must know which
# models exist before it can create their database tables.
from app import models


# Define an asynchronous function to create database tables.
async def create_tables():

    # Open a database connection and begin a transaction.
    # engine.begin() manages the connection and transaction.
    async with engine.begin() as connection:

        # Run the synchronous SQLAlchemy metadata operation
        # through the asynchronous database connection.
        #
        # Base.metadata contains information about all registered models.
        #
        # create_all() creates tables that do not already exist.
        # It does not automatically modify existing tables.
        await connection.run_sync(Base.metadata.create_all)

    # Display a success message after the table creation operation.
    print("Database tables created successfully!")

    # Close the engine's database connection pool.
    # This is useful because this script is a standalone task.
    await engine.dispose()


# Start the asynchronous create_tables() function.
#
# asyncio.run() creates and manages an event loop,
# runs the asynchronous function, and finishes when it completes.
asyncio.run(create_tables())
