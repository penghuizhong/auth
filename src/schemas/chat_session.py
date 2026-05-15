from typing import Optional

from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime


class ChatSessionCreateResponse(BaseModel):
    id: UUID
    thread_id: UUID
    title: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ChatSessionResponse(BaseModel):
    id: UUID
    thread_id: UUID
    title: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ChatSessionUpdateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)
