import logging
import time

from openai import OpenAI

logger = logging.getLogger(__name__)


def create_client(api_key: str) -> OpenAI:
    """Create and configure the OpenAI client."""

    return OpenAI(
        api_key=api_key,
        timeout=30,
        max_retries=2,
    )


def generate_response(client: OpenAI, prompt: str) -> str:
    """Send a prompt to the OpenAI model and return the response."""

    start_time = time.perf_counter()

    logger.info("Sending request to OpenAI.")

    try:
        response = client.responses.create(
            model="gpt-5-mini",
            input=prompt,
        )

        latency = time.perf_counter() - start_time

        usage = response.usage

        logger.info(
            "OpenAI request successful | latency=%.3fs | input_tokens=%s | "
            "output_tokens=%s | total_tokens=%s",
            latency,
            usage.input_tokens,
            usage.output_tokens,
            usage.total_tokens,
        )

        return response.output_text

    except Exception:
        latency = time.perf_counter() - start_time

        logger.exception(
            "OpenAI request failed | latency=%.3fs",
            latency,
        )

        raise
