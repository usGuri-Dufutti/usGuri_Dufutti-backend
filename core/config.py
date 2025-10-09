import os
from pydantic import BaseSettings, PostgresDsn
from typing import Optional



class Settings(BaseSettings):
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000

    POSTGRES_USER: str = "paster"
    POSTGRES_PASSWORD: str = "wficUV6L3xZTj17g2eSafJLjpyL9UdzN"
    POSTGRES_DB: str = "flower_6tst"
    POSTGRES_HOST: str = "postgres"  # <--- aqui
    POSTGRES_PORT: int = 5432

    DATABASE_URL: Optional[str] = "postgresql://paster:wficUV6L3xZTj17g2eSafJLjpyL9UdzN@dpg-d3k1bgnfte5s73bvgdk0-a.oregon-postgres.render.com/flower_6tst"

    # OpenAI Configuration
    OPENAI_API_KEY: Optional[str] = None
    class Config(BaseSettings.Config):
        env_file = ".env"
        case_sensitive = True

    @property
    def db_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

settings = Settings()
