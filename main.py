from fastapi import Depends, FastAPI
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import Session as SessionType
from sqlalchemy.orm import declarative_base, sessionmaker

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


class AlunoModel(Base):
    __tablename__ = "alunos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    turma = Column(String, nullable=False)


# Cria as tabelas
Base.metadata.create_all(bind=engine)

# --------------------
# Modelo da API (Pydantic)
# --------------------


class AlunoCreate(BaseModel):
    nome: str
    turma: str


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


@app.post("/aluno")
def add_aluno(aluno: AlunoCreate, db: SessionType = Depends(get_db)):
    novo = AlunoModel(nome=aluno.nome, turma=aluno.turma)

    db.add(novo)
    db.commit()
    db.refresh(novo)

    return novo
