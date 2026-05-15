from typing import Optional

from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime


class UserResponse(BaseModel):
    id: UUID
    email: str
    nickname: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserUpdateRequest(BaseModel):
    nickname: Optional[str] = Field(default=None, max_length=100)
