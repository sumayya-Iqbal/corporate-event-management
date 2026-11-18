
# Import asyncio to run asynchronous Python functions.
import asyncio

# Import text() to execute a raw SQL query.
from sqlalchemy import text

# Import the database engine from db.py.
# The engine manages our connection to Neon PostgreSQL.
from app.db import engine


# Define an asynchronous function to test the database connection.
async def test_connection():

    # try is used to execute code that might produce an error.
    try:

        # Open a connection to the database.
        #
        # The async with block automatically closes the connection
        # after the operations inside it finish.
        async with engine.connect() as connection:

            # Execute a simple SQL query.
            #
            # SELECT 1 does not insert, update, or delete anything.
            # It simply asks the database to return the number 1.
            result = await connection.execute(text("SELECT 1"))

            # If execution reaches this point, the database connection worked.
            print("SUCCESS! Database connected.")

            # scalar() extracts the first column of the first result row.
            # For SELECT 1, the returned value should be 1.
            print("Test result:", result.scalar())

    # If an error occurs while connecting or executing the query,
    # Python moves into this except block.
    except Exception as error:

        # Display a message indicating that the test failed.
        print("DATABASE CONNECTION FAILED")

        # repr() displays a detailed representation of the error.
        # This helps when diagnosing connection problems.
        print("Error:", repr(error))

    # finally runs whether the test succeeds or fails.
    finally:

        # Dispose of the engine's connection pool.
        # This is useful because this is a standalone testing script.
        await engine.dispose()


# Start the asynchronous test_connection() function.
# asyncio.run() manages the event loop for this script.
asyncio.run(test_connection())
