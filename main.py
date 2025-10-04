from fastapi import FastAPI
from routes.router import api_router
from core.config import settings
from db import base  # noqa: F401
from db.session import engine

# cria todas as tabelas (útil para desenvolvimento; para produção prefira Alembic)
base.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Backend FastAPI + Postgres")

app.include_router(api_router)
