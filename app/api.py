import uuid
import time

from app.metrics import REQUEST_COUNT, REQUEST_LATENCY
from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.auth import authenticate, require_admin
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


limiter = Limiter(
    key_func=get_remote_address
)


app = FastAPI(
    title="Production GenAI API",
    description="A production-style Generative AI API with Guardrails.",
    version="1.0.0",
)


app.state.limiter = limiter


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


@app.exception_handler(RateLimitExceeded)
async def handle_rate_limit_error(
    request: Request,
    exc: RateLimitExceeded,
):
    return JSONResponse(
        status_code=429,
        content={
            "detail": "Rate limit exceeded. Please try again later.",
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


@app.middleware("http")
async def metrics_middleware(
    request: Request,
    call_next,
):
    start_time = time.perf_counter()

    response = await call_next(request)

    latency = time.perf_counter() - start_time

    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code,
    ).inc()

    REQUEST_LATENCY.labels(
        method=request.method,
        endpoint=request.url.path,
    ).observe(latency)

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

@app.get("/metrics")
def metrics():
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )


@app.post(
    "/generate",
    response_model=GenerateResponse,
)
@limiter.limit("10/minute")
def generate(
    request: Request,
    generate_request: GenerateRequest,
    user: str = Depends(authenticate),
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


@app.get("/admin")
def admin_endpoint(
    user: str = Depends(require_admin),
):
    return {
        "message": "Welcome, admin.",
        "user": user,
    }
