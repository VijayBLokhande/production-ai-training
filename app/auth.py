import os

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer


security = HTTPBearer()


def get_expected_token() -> str:
    """Get the API authentication token from environment variables."""

    token = os.getenv("API_AUTH_TOKEN")

    if not token:
        raise RuntimeError(
            "API_AUTH_TOKEN is not configured."
        )

    return token


def authenticate(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """Authenticate the incoming request using a bearer token."""

    expected_token = get_expected_token()

    if credentials.credentials != expected_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials.",
        )

    return "user"


def require_admin(user: str = Depends(authenticate)) -> str:
    """Require an authenticated admin user."""

    if user != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required.",
        )

    return user
