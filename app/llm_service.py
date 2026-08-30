from openai import OpenAI

def create_client(api_key: str) -> OpenAI:
    """Create and configure the OpenAI client."""

    return OpenAI(
        api_key=api_key,
        timeout=30,  # Set a timeout for requests (in seconds)
        max_retries=2,  # Set the maximum number of retries for failed requests
    )


def generate_response(client: OpenAI, prompt: str) -> str:
    """Send a prompt to the OpenAI model and return the response."""

    response = client.responses.create(
        model="gpt-5-mini",
        input=prompt,
    )

    return response.output_text
