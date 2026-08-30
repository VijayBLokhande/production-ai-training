import os

from dotenv import load_dotenv

def load_config():
    """Load and validate application configuration."""

    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY is not set in the environment variables."
        )
    
    return api_key
