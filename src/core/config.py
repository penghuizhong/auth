from functools import lru_cache

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # 基础配置
    LOG_LEVEL: str = "info"
    MODE: str = "production"
    SHOW_DOCS: bool = True
    GRACEFUL_SHUTDOWN_TIMEOUT: int = 30

    # 数据库配置
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: SecretStr = SecretStr("postgres")
    POSTGRES_DB: str = "fyzj_agent"

    # JWT 配置（与 agent 共享）
    AUTH_SECRET: SecretStr = Field(..., description="JWT 签名密钥，与 agent 服务共享")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS 配置
    CORS_ORIGINS: str = "http://localhost:3000"

    # Admin 配置
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: SecretStr = SecretStr("admin")

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.POSTGRES_USER}:"
            f"{self.POSTGRES_PASSWORD.get_secret_value()}@"
            f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/"
            f"{self.POSTGRES_DB}"
        )

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    def is_dev(self) -> bool:
        return self.MODE.lower() == "dev"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}

@lru_cache
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()

settings = get_settings()
