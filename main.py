from fastapi import FastAPI
from routes.router import api_router
from core.config import settings
from models.site import Site
from models.observation import Observation
from models.plant import Plant


from db import base  # noqa: F401
from db.session import engine
import time

# cria todas as tabelas (útil para desenvolvimento; para produção prefira Alembic)
time.sleep(5)
base.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Backend FastAPI + Postgres")

app.include_router(api_router)
