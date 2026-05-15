from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session, select

from core.database import get_session
from core.security import decode_token
from models.user import User

security = HTTPBearer(auto_error=False)


async def get_current_user(
    http_auth: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
    session: Annotated[Session, Depends(get_session)],
) -> User:
    if http_auth is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未提供认证令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="令牌无效或遭篡改",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(http_auth.credentials)
        if payload.get("type") != "access":
            raise credentials_exception
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        user_id = UUID(user_id)
    except Exception:
        raise credentials_exception

    statement = select(User).where(User.id == user_id)
    user = session.exec(statement).first()
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="账户已禁用")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
