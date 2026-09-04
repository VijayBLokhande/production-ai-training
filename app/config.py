import os

from dotenv import load_dotenv

from app.exceptions import ConfigurationError           # initially there is no line for importing ConfigurationError, but I added it to match the custom exception defined in app/exceptions.py


def load_config():
    """Load and validate application configuration."""

    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ConfigurationError(                                           # initially insted of ConfigurationError, it was ValueError, but I changed it to ConfigurationError to match the custom exception defined in app/exceptions.py            "OPENAI_API_KEY is not set in the environment variables."
        )
    
    return api_key
