from fastapi import APIRouter, Depends, FastAPI, Header, HTTPException, Request

from .database import Base, engine, get_db
from .config import API_KEY

#ROUTERS INTERNOS
from .routers.internal.jogos import router as internal_jogos
from .routers.internal.turmas import router as internal_turmas
from .routers.internal.sessoes import router as internal_sessoes
#ROUTERS CLIENTS
from .routers.client.jogos import router as client_jogos
from .routers.client.turmas import router as client_turmas
from .routers.client.sessoes import router as client_sessoes

Base.metadata.create_all(bind=engine)
app = FastAPI()


def validar_api_key(x_api_key: str = Header(alias="X-API-Key")):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401)


def validar_internal(request: Request):
    if request.client is None:
        raise HTTPException(status_code=401)

    ip = request.client.host

    if ip != "127.0.0.1":
        raise HTTPException(status_code=401)

# -- ROUTERS --

# --------------------------
# Routers Internos (Internal)
# --------------------------
internal_router = APIRouter(prefix="/api/internal", dependencies=[Depends(validar_internal)])

internal_router.include_router(internal_jogos)
internal_router.include_router(internal_turmas)
internal_router.include_router(internal_sessoes)

app.include_router(internal_router)

# --------------------------
# Routers Clients (Client)
# --------------------------
client_router = APIRouter(prefix="/api/client", dependencies=[Depends(validar_api_key)])  # não precisa de dependência de API Key

client_router.include_router(client_jogos)
client_router.include_router(client_turmas)
client_router.include_router(client_sessoes)

@app.get("/api/internal/health", tags=["Internal"])
def health(_: None = Depends(validar_internal)):
    return {"ok": True}


app.include_router(client_router)
