import logging
import time

from openai import OpenAI

from app.exceptions import LLMServiceError
from app.metrics import (
    LLM_INPUT_TOKENS,
    LLM_LATENCY,
    LLM_OUTPUT_TOKENS,
    LLM_REQUEST_COUNT,
)


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

        LLM_REQUEST_COUNT.labels(
            status="success",
        ).inc()

        LLM_LATENCY.observe(latency)

        LLM_INPUT_TOKENS.inc(
            usage.input_tokens
        )

        LLM_OUTPUT_TOKENS.inc(
            usage.output_tokens
        )

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

        LLM_REQUEST_COUNT.labels(
            status="error",
        ).inc()

        LLM_LATENCY.observe(latency)

        logger.exception(
            "OpenAI request failed | request_id=%s | latency=%.3fs",
            request_id,
            latency,
        )

        raise LLMServiceError(
            "LLM service request failed."
        ) from error
    