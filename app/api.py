from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.config import load_config
from app.guardrails import GuardrailViolation, validate_input
from app.llm_service import create_client, generate_response


app = FastAPI(
    title="Production GenAI API",
    description="A production-style Generative AI API with Guardrails.",
    version="1.0.0",
)


class GenerateRequest(BaseModel):
    prompt: str


class GenerateResponse(BaseModel):
    response: str


@app.post("/generate", response_model=GenerateResponse)
def generate(request: GenerateRequest):
    try:
        api_key = load_config()

        validated_prompt = validate_input(request.prompt)

        client = create_client(api_key)

        answer = generate_response(client, validated_prompt)

        return GenerateResponse(response=answer)

    except GuardrailViolation as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except ValueError as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        )

    except Exception:
        raise HTTPException(
            status_code=503,
            detail="AI service is currently unavailable.", 
        )
    