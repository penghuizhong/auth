
from pydantic import BaseModel, EmailStr, Field, field_validator


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    nickname: str | None = Field(default=None, max_length=100)

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("密码至少 8 位")
        if not any(c.isupper() for c in v):
            raise ValueError("密码需包含大写字母")
        if not any(c.islower() for c in v):
            raise ValueError("密码需包含小写字母")
        if not any(c.isdigit() for c in v):
            raise ValueError("密码需包含数字")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class ErrorResponse(BaseModel):
    code: str
    message: str
    details: str | None = None
