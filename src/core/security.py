from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID, uuid4

import bcrypt
import jwt

from core.config import settings

_blacklisted_jtis: set[str] = set()


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


# 💡 修改点 1：参数 email 改成了 username
def create_access_token(subject: UUID, username: str) -> str:
    expire = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload: dict[str, Any] = {
        "sub": str(subject),
        # 💡 修改点 2：Token 负载里的键值对也改成了 username
        "username": username, 
        "exp": expire,
        "iat": datetime.now(UTC),
        "type": "access",
        "jti": str(uuid4()),
    }
    return jwt.encode(payload, settings.AUTH_SECRET.get_secret_value(), algorithm="HS256")


def create_refresh_token(subject: UUID) -> str:
    expire = datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload: dict[str, Any] = {
        "sub": str(subject),
        "exp": expire,
        "iat": datetime.now(UTC),
        "type": "refresh",
        "jti": str(uuid4()),
    }
    return jwt.encode(payload, settings.AUTH_SECRET.get_secret_value(), algorithm="HS256")


def decode_token(token: str) -> dict[str, Any]:
    return jwt.decode(
        token,
        settings.AUTH_SECRET.get_secret_value(),
        algorithms=["HS256"],
    )


def blacklist_token(jti: str) -> None:
    _blacklisted_jtis.add(jti)


def is_token_blacklisted(jti: str) -> bool:
    return jti in _blacklisted_jtis


def cleanup_blacklist() -> None:
    _blacklisted_jtis.clear()