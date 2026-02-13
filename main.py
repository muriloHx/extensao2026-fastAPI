from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session as SessionType
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.sql.roles import JoinTargetRole

# --------------------
# Configuração do banco
# --------------------

DATABASE_URL = "sqlite:///./db.sqlite3"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # necessário para SQLite
)

SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()

# --------------------
# Modelo do banco (ORM)
# --------------------


class TurmasModel(Base):
    __tablename__ = "turmas"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False, unique=True)


class JogosModel(Base):
    __tablename__ = "jogos"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(
        String,
    )


# Cria as tabelas
Base.metadata.create_all(bind=engine)

# --------------------
# Modelo da API (Pydantic)
# --------------------


class TurmasCreate(BaseModel):
    nome: str


class JogosCreate(BaseModel):
    nome: str


# --------------------
# Dependency da sessão
# --------------------


def get_db():
    with SessionLocal() as session:
        yield session


# --------------------
# App
# --------------------

app = FastAPI()


@app.post("/turma")
def add_turma(turma: TurmasCreate, db: SessionType = Depends(get_db)):
    novo = TurmasModel(nome=turma.nome)
    db.add(novo)
    try:
        db.commit()
        db.refresh(novo)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Turma '{turma.nome}' já existe")

    return novo


@app.delete("/turma/{turma_id}")
def delete_turma(turma_id: int, db: SessionType = Depends(get_db)):
    turma = db.query(JogosModel).filter(JogosModel.id == turma_id).first()
    if not turma:
        raise HTTPException(status_code=400, detail=f"Turma não encontrada")


@app.post("/jogo")
def add_jogo(jogo: JogosCreate, db: SessionType = Depends(get_db)):
    novo = JogosModel(nome=jogo.nome)
    db.add(novo)
    try:
        db.commit()
        db.refresh(novo)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Jogo '{jogo.nome}' já existe")

    return novo


@app.delete("/jogo/{jogo_id}")
def delete_jogo(jogo_id: int, db: SessionType = Depends(get_db)):
    jogo = db.query(JogosModel).filter(JogosModel.id == jogo_id).first()
    if not jogo:
        raise HTTPException(status_code=404, detail="Jogo não encontrado")

    # Remove do banco
    db.delete(jogo)
    db.commit()
    return {"detail": f"Jogo {jogo.nome} deletado com sucesso"}
