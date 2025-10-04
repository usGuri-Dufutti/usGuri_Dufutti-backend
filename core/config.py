import os
from pydantic import BaseSettings, PostgresDsn
from typing import Optional



class Settings(BaseSettings):
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000

    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "secret"
    POSTGRES_DB: str = "flowerDB"
    POSTGRES_HOST: str = "postgres"  # <--- aqui
    POSTGRES_PORT: int = 5432

    DATABASE_URL: Optional[str] = None
    class Config(BaseSettings.Config):
        env_file = ".env"
        case_sensitive = True

    @property
    def db_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

settings = Settings()
