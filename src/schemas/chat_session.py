from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ChatSessionCreateResponse(BaseModel):
    id: UUID
    thread_id: UUID
    title: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ChatSessionResponse(BaseModel):
    id: UUID
    thread_id: UUID
    title: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ChatSessionUpdateRequest(BaseModel):
    title: str | None = Field(default=None, max_length=255)
