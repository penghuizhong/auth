from fastapi import APIRouter, Depends
from sqlmodel import Session

from core.database import get_session
from api.deps import CurrentUser
from schemas.user import UserUpdateRequest, UserResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: CurrentUser):
    return current_user


@router.patch("/me", response_model=UserResponse)
def update_current_user(
    request: UserUpdateRequest,
    current_user: CurrentUser,
    session: Session = Depends(get_session),
):
    if request.nickname is not None:
        current_user.nickname = request.nickname
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    return current_user
