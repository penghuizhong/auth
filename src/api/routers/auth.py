from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from api.deps import CurrentUser
from core.database import get_session
from core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from models.user import User
from schemas.auth import LoginRequest, RefreshRequest, RegisterRequest, TokenResponse
from schemas.user import UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(request: RegisterRequest, session: Session = Depends(get_session)):
    statement = select(User).where(User.email == request.email)
    existing = session.exec(statement).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="该邮箱已注册")

    user = User(
        email=request.email,
        hashed_password=hash_password(request.password),
        nickname=request.nickname,
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    access_token = create_access_token(user.id, user.email)
    refresh_token = create_refresh_token(user.id)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, session: Session = Depends(get_session)):
    statement = select(User).where(User.email == request.email)
    user = session.exec(statement).first()
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="邮箱或密码错误")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="账户已禁用")

    access_token = create_access_token(user.id, user.email)
    refresh_token = create_refresh_token(user.id)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenResponse)
def refresh(request: RefreshRequest, session: Session = Depends(get_session)):
    try:
        payload = decode_token(request.refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="无效的刷新令牌")
        user_id = payload.get("sub")
    except Exception:
        raise HTTPException(status_code=401, detail="无效的刷新令牌")

    statement = select(User).where(User.id == user_id)
    user = session.exec(statement).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="用户不存在或已禁用")

    access_token = create_access_token(user.id, user.email)
    new_refresh_token = create_refresh_token(user.id)
    return TokenResponse(access_token=access_token, refresh_token=new_refresh_token)


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(lambda: None)):
    """占位端点，实际由 deps.get_current_user 提供用户"""
    return current_user


@router.post("/logout")
def logout(current_user: CurrentUser):
    return {"message": "已登出"}


@router.get("/verify")
def verify(current_user: CurrentUser):
    return {"valid": True, "user_id": str(current_user.id), "email": current_user.email}
