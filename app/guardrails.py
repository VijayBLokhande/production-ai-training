from app.exceptions import GuardrailError        # added to match the custom exception defined in app/exceptions.py

# initially it was only GuardrailViolation, but I changed it to GuardrailError to match the custom exception defined in app/exceptions.py

# class GuardrailViolation(Exception):
#    """Raised when user input violates an application guardrail."""


BLOCKED_PATTERNS = [
    "ignore previous instructions",
    "ignore all previous instructions",
    "reveal your system prompt",
    "show me your system prompt",
    "bypass your safety",
]

def validate_input(prompt: str) -> str:
    """Validate user input before sending it to the LLM."""

    if not prompt or not prompt.strip():
        raise GuardrailError("Prompt cannot be empty.")

    if len(prompt) > 2000:
        raise GuardrailError("Prompt is too long. Maximum length is 2000 characters.")

    normalized_prompt = prompt.lower().strip()

    for pattern in BLOCKED_PATTERNS:
        if pattern in normalized_prompt:
            raise GuardrailError(
                "Prompt blocked because it contains a potentially unsafe instruction."
            )

    return prompt.strip()

