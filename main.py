import os

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, FastAPI, Header, HTTPException, Request
from sqlalchemy.orm import Session

import services
from models import Base, SessionLocal, engine
from schemas import JogosCreate, SessoesCreate, TurmasCreate

load_dotenv()

API_KEY = os.getenv("API_SENHA_GERAL")

Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    with SessionLocal() as session:
        yield session


def validar_api_key(x_api_key: str = Header(alias="X-API-Key")):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401)


def validar_internal(request: Request):
    ip = request.client.host
    if ip != "127.0.0.1":
        raise HTTPException(status_code=401)


client_router = APIRouter(prefix="/api/client", dependencies=[Depends(validar_api_key)])

internal_router = APIRouter(
    prefix="/api/internal", dependencies=[Depends(validar_internal)]
)


@client_router.get("/turmas")
def get_turmas(db: Session = Depends(get_db)):
    return services.listar_turmas(db)


@client_router.post("/sessao")
def add_sessao(sessao: SessoesCreate, db: Session = Depends(get_db)):
    return services.criar_sessao(db, sessao)


@internal_router.post("/turma")
def add_turma(turma: TurmasCreate, db: Session = Depends(get_db)):
    return services.criar_turma(db, turma.nome)


@internal_router.delete("/turma/{turma_id}")
def delete_turma(turma_id: int, db: Session = Depends(get_db)):
    return services.deletar_turma(db, turma_id)


@internal_router.post("/jogo")
def add_jogo(jogo: JogosCreate, db: Session = Depends(get_db)):
    return services.criar_jogo(db, jogo.nome)


@internal_router.delete("/jogo/{jogo_id}")
def delete_jogo(jogo_id: int, db: Session = Depends(get_db)):
    return services.deletar_jogo(db, jogo_id)


app.include_router(client_router)
app.include_router(internal_router)
