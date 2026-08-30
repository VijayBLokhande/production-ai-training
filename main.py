import logging
import os

from dotenv import load_dotenv
from openai import OpenAI

def load_config():
    """ Load and validate application configuration."""     # Docstring

    load_dotenv()


    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY is not set in the environment variables."
        )

    return api_key


def create_client(api_key):
    """Create and configure the OpenAI client."""

    return OpenAI(
        api_key=api_key, # Set the API key for authentication
        timeout=30.0,  # Set a timeout for API requests (in seconds)
        max_retries=2,  # Set the maximum number of retries for failed requests
    )


def generate_response(client, prompt):
    """Send a prompt to the OpenAI model and return the response."""

    logger.info("Sending request to OpenAI.")

    response = client.responses.create(
        model="gpt-5-mini",
        input=prompt,
    )

    logger.info("Received response successfully from OpenAI.")

    return response.output_text

def main():
    """Application entry point."""

    try:
        api_key = load_config()

        client = create_client(api_key)

        prompt = "Explain what is generative AI in two simple sentences."

        answer = generate_response(client, prompt)

        print("\nAI Response:")
        print(answer)

    except ValueError as error:
        logger.error("Configuration error: %s", error)
        print("Application configuration is invalid.")

    except Exception:
        logger.exception("OpenAI API request failed.")
        print("Sorry, The AI service is currently unavailable. Please try again later.")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


if __name__ == "__main__":
    main()
    