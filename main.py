from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.router import api_router
from core.config import settings
from models.site import Site
from models.observation import Observation
from models.plant import Plant
from models.area import Area, AreaCoordinate

from db import base  # noqa: F401
from db.session import engine
import time

# cria todas as tabelas (útil para desenvolvimento; para produção prefira Alembic)
time.sleep(5)
base.Base.metadata.create_all(bind=engine)
from utils.convertData import run_conversion as convert_data
#
# try:
#    # convert_data()
#     print("✅ Dados convertidos com sucesso.")
# except Exception as e:
#     print(f"⚠️ Erro ao converter dados: {e}")

app = FastAPI(title="Backend FastAPI + Postgres")

# Configurar CORS para o frontend acessar
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especifique o domínio do frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
