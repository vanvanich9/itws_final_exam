"""Authentication-related configuration."""

import re
from datetime import timedelta

from core.config.enums import TokenType
from pydantic import EmailStr, TypeAdapter

EMAIL_ADAPTER = TypeAdapter(EmailStr)

PASSWORD_PATTERN = re.compile(
    r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^a-zA-Z0-9]).{8,20}$'
)

JWT_ALGORITHM = 'HS256'
TOKEN_TTL: dict[TokenType, timedelta] = {
    TokenType.ACCESS: timedelta(minutes=5),
    TokenType.REFRESH: timedelta(minutes=60),
}
