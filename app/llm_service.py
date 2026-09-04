import logging
import time

from openai import OpenAI

from app.exceptions import LLMServiceError


logger = logging.getLogger(__name__)


def create_client(api_key: str) -> OpenAI:
    """Create and configure the OpenAI client."""

    return OpenAI(
        api_key=api_key,
        timeout=30,
        max_retries=2,
    )


def generate_response(
    client: OpenAI,
    prompt: str,
    request_id: str,
) -> str:
    """Send a prompt to the OpenAI model and return the response."""

    start_time = time.perf_counter()

    logger.info(
        "Sending request to OpenAI | request_id=%s",
        request_id,
    )

    try:
        response = client.responses.create(
            model="gpt-5-mini",
            input=prompt,
        )

        latency = time.perf_counter() - start_time

        usage = response.usage

        logger.info(
            "OpenAI request successful | request_id=%s | "
            "latency=%.3fs | input_tokens=%s | "
            "output_tokens=%s | total_tokens=%s",
            request_id,
            latency,
            usage.input_tokens,
            usage.output_tokens,
            usage.total_tokens,
        )

        return response.output_text

    except Exception as error:
        latency = time.perf_counter() - start_time

        logger.exception(
            "OpenAI request failed | request_id=%s | latency=%.3fs",
            request_id,
            latency,
        )

        raise LLMServiceError(
            "LLM service request failed."
        ) from error
