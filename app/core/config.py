import os
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    github_token: str = ""
    github_api_timeout: int = 30
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/portfolio_db"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
