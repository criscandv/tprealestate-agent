import secrets
import string
import uuid
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader

API_KEY_LENGTH = 32
API_KEY_HEADER = "X-API-Key"

# Inicializo el header
api_key_header = APIKeyHeader(name=API_KEY_HEADER, auto_error=False)


def generate_api_key() -> str:
    alphabet = string.ascii_letters + string.digits
    api_key = "".join(secrets.choice(alphabet) for _ in range(API_KEY_LENGTH))
    return f"pk-{api_key}"


def generate_uuid() -> str:
    return str(uuid.uuid4())


def calculate_expiration_date(days: Optional[int] = None) -> Optional[datetime]:
    if days is None:
        return None

    return datetime.now() + timedelta(days=days)


async def get_api_key(api_key: str = Depends(api_key_header)) -> str:
    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key is required",
            headers={"WWW-Authenticate": API_KEY_HEADER},
        )

    return api_key


def is_valid_uuid(val: str) -> bool:
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False
