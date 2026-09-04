import uuid

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.config import load_config
from app.exceptions import (
    ConfigurationError,
    GuardrailError,
    LLMServiceError,
)
from app.guardrails import validate_input
from app.llm_service import create_client, generate_response
from app.logging_config import configure_logging


configure_logging()


app = FastAPI(
    title="Production GenAI API",
    description="A production-style Generative AI API with Guardrails.",
    version="1.0.0",
)


@app.exception_handler(GuardrailError)
async def handle_guardrail_error(
    request: Request,
    exc: GuardrailError,
):
    return JSONResponse(
        status_code=400,
        content={
            "detail": str(exc),
        },
    )


@app.exception_handler(ConfigurationError)
async def handle_configuration_error(
    request: Request,
    exc: ConfigurationError,
):
    return JSONResponse(
        status_code=500,
        content={
            "detail": str(exc),
        },
    )


@app.exception_handler(LLMServiceError)
async def handle_llm_service_error(
    request: Request,
    exc: LLMServiceError,
):
    return JSONResponse(
        status_code=503,
        content={
            "detail": "AI service is currently unavailable.",
        },
    )


@app.middleware("http")
async def request_id_middleware(
    request: Request,
    call_next,
):
    request_id = (
        request.headers.get("X-Request-ID")
        or str(uuid.uuid4())
    )

    request.state.request_id = request_id

    response = await call_next(request)

    response.headers["X-Request-ID"] = request_id

    return response


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


class GenerateRequest(BaseModel):
    prompt: str


class GenerateResponse(BaseModel):
    response: str


@app.post("/generate", response_model=GenerateResponse)
def generate(
    request: Request,
    generate_request: GenerateRequest,
):
    api_key = load_config()

    validated_prompt = validate_input(
        generate_request.prompt
    )

    client = create_client(api_key)

    request_id = request.state.request_id

    answer = generate_response(
        client,
        validated_prompt,
        request_id,
    )

    return GenerateResponse(
        response=answer
    )
