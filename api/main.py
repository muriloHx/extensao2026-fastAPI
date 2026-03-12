from fastapi import APIRouter, Depends, FastAPI, Header, HTTPException

from .config import CLIENT_API_KEY, INTERNAL_API_KEY
from .database import Base, engine

# ROUTERS CLIENTS
from .routers.client.jogos import router as client_jogos
from .routers.client.sessoes import router as client_sessoes
from .routers.client.turmas import router as client_turmas
from .routers.internal.alunos import router as internal_alunos

# ROUTERS INTERNOS
from .routers.internal.jogos import router as internal_jogos
from .routers.internal.sessoes import router as internal_sessoes
from .routers.internal.turmas import router as internal_turmas

Base.metadata.create_all(bind=engine)
app = FastAPI()


def validar_client(x_api_key: str = Header(alias="X-API-Key")):
    if x_api_key != CLIENT_API_KEY:
        raise HTTPException(status_code=401)


def validar_internal(x_api_key: str = Header(alias="X-API-Key")):
    if x_api_key != INTERNAL_API_KEY:
        raise HTTPException(status_code=401)


# --------------------------
# Routers Internos
# --------------------------
internal_router = APIRouter(
    prefix="/api/internal", dependencies=[Depends(validar_internal)]
)


@internal_router.get("/health", tags=["Internal"])
def health():
    return {"ok": True}


internal_router.include_router(internal_jogos)
internal_router.include_router(internal_turmas)
internal_router.include_router(internal_sessoes)
internal_router.include_router(internal_alunos)
app.include_router(internal_router)

# --------------------------
# Routers Clients
# --------------------------
client_router = APIRouter(prefix="/api/client", dependencies=[Depends(validar_client)])
client_router.include_router(client_jogos)
client_router.include_router(client_turmas)
client_router.include_router(client_sessoes)
app.include_router(client_router)
