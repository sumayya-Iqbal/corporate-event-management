
# Import Pydantic Settings tools.
#
# BaseSettings automatically reads configuration values
# from environment variables and the .env file.
#
# SettingsConfigDict allows us to configure how settings are loaded.
from pydantic_settings import BaseSettings, SettingsConfigDict


# Create a Settings class to manage application configuration.
#
# BaseSettings automatically loads values based on the field names
# defined inside this class.
class Settings(BaseSettings):

    """
    Application configuration.

    Reads settings from the .env file.
    """

    # Database connection URL for Neon PostgreSQL.
    #
    # This is required because no default value is provided.
    # The actual connection URL is stored in the .env file.
    DATABASE_URL: str

    # ==================================
    # JWT SETTINGS
    # ==================================

    # Secret key used to sign and verify JWT access tokens.
    #
    # Keep this value private.
    # Never upload your actual secret key to GitHub.
    SECRET_KEY: str

    # Algorithm used to sign JWT tokens.
    # HS256 is a symmetric signing algorithm.
    # The same secret key is used to sign and verify tokens.
    ALGORITHM: str = "HS256"

    # Access token lifetime in minutes.
    # Here, a token expires after 30 minutes.
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # ==================================
    # ENVIRONMENT FILE CONFIGURATION
    # ==================================

    # Configure how Pydantic loads application settings.
    model_config = SettingsConfigDict(

        # Read configuration values from a file named .env.
        env_file=".env",

        # Read the .env file using UTF-8 encoding.
        env_file_encoding="utf-8",

        # Ignore additional variables in .env
        # that are not defined in this Settings class.
        extra="ignore"
    )


# Create one Settings object for the application.
#
# Other files can import this object to access configuration values.
# Example: settings.DATABASE_URL
settings = Settings()
