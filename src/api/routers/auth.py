from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session, select

from api.deps import CurrentUser
from core.database import get_session
from core.security import (
    blacklist_token,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    is_token_blacklisted,
    verify_password,
)
from models.user import User
from schemas.auth import LoginRequest, RefreshRequest, RegisterRequest, TokenResponse
from schemas.user import UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])
bearer_scheme = HTTPBearer()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(request: RegisterRequest, session: Session = Depends(get_session)):
    # 改用 username 查重
    statement = select(User).where(User.username == request.username)
    existing = session.exec(statement).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="该用户名已注册")

    # 创建用户时使用 username
    user = User(
        username=request.username,
        hashed_password=hash_password(request.password),
        nickname=request.nickname,
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    # 签发 token 时把 username 塞进去
    access_token = create_access_token(user.id, user.username)
    refresh_token = create_refresh_token(user.id)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, session: Session = Depends(get_session)):
    # 改用 username 登录
    statement = select(User).where(User.username == request.username)
    user = session.exec(statement).first()
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="账户已禁用")

    access_token = create_access_token(user.id, user.username)
    refresh_token = create_refresh_token(user.id)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenResponse)
def refresh(request: RefreshRequest, session: Session = Depends(get_session)):
    try:
        payload = decode_token(request.refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="无效的刷新令牌")
        if is_token_blacklisted(payload.get("jti")):
            raise HTTPException(status_code=401, detail="无效的刷新令牌")
        user_id = payload.get("sub")
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=401, detail="无效的刷新令牌")

    statement = select(User).where(User.id == user_id)
    user = session.exec(statement).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="用户不存在或已禁用")

    # 刷新 token 也保持一致使用 username
    access_token = create_access_token(user.id, user.username)
    new_refresh_token = create_refresh_token(user.id)
    return TokenResponse(access_token=access_token, refresh_token=new_refresh_token)


@router.get("/me", response_model=UserResponse)
def get_me(current_user: CurrentUser):
    return current_user


@router.post("/logout")
def logout(
    current_user: CurrentUser,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
):
    try:
        payload = decode_token(credentials.credentials)
        blacklist_token(payload.get("jti"))
    except Exception:
        pass
    return {"message": "已登出"}


@router.get("/verify")
def verify(current_user: CurrentUser):
    # 验证接口返回 username 而不是 email
    return {"valid": True, "user_id": str(current_user.id), "username": current_user.username}