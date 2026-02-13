from datetime import datetime
from typing import List

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from pydantic_core.core_schema import no_info_before_validator_function
from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, create_engine, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    mapped_column,
    relationship,
    sessionmaker,
)

# --------------------
# Configuração do banco
# --------------------

DATABASE_URL = "sqlite:///./db.sqlite3"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


# --------------------
# Modelos ORM
# --------------------


class TurmasModel(Base):
    __tablename__ = "turmas"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    sessoes: Mapped[List["SessoesModel"]] = relationship(
        back_populates="turma",
        cascade="all, delete",
    )


class JogosModel(Base):
    __tablename__ = "jogos"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    sessoes: Mapped[List["SessoesModel"]] = relationship(
        back_populates="jogo",
        cascade="all, delete",
    )


class SessoesModel(Base):
    __tablename__ = "sessoes"

    id: Mapped[int] = mapped_column(primary_key=True)

    turma_id: Mapped[int] = mapped_column(ForeignKey("turmas.id", ondelete="CASCADE"))

    jogo_id: Mapped[int] = mapped_column(ForeignKey("jogos.id", ondelete="CASCADE"))

    palavra: Mapped[str | None] = mapped_column(String, nullable=True)
    dificuldade: Mapped[str | None] = mapped_column(String, nullable=True)
    tempo_total: Mapped[float | None] = mapped_column(Float, nullable=True)
    acertos: Mapped[int | None] = mapped_column(Integer, nullable=True)
    erros: Mapped[int | None] = mapped_column(Integer, nullable=True)

    data_execucao: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )

    turma: Mapped["TurmasModel"] = relationship(back_populates="sessoes")
    jogo: Mapped["JogosModel"] = relationship(back_populates="sessoes")


Base.metadata.create_all(bind=engine)

# --------------------
# Pydantic
# --------------------


class TurmasCreate(BaseModel):
    nome: str


class JogosCreate(BaseModel):
    nome: str


class SessoesCreate(BaseModel):
    turma_id: int
    jogo_id: int
    palavra: str | None = None
    dificuldade: str | None = None
    tempo_total: float | None = None
    acertos: int | None = None
    erros: int | None = None
    # campos completamente omitiveis no request, devido as particularidades que cada jogo pode ter. Ex: nem todo jogo terá campo "dificuldade"


# --------------------
# Dependency
# --------------------


def get_db():
    with SessionLocal() as session:
        yield session


# --------------------
# App
# --------------------

app = FastAPI()


@app.post("/turma")
def add_turma(turma: TurmasCreate, db: Session = Depends(get_db)):
    nova = TurmasModel(nome=turma.nome)
    db.add(nova)
    try:
        db.commit()
        db.refresh(nova)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Turma já existe")

    return nova


@app.delete("/turma/{turma_id}")
def delete_turma(turma_id: int, db: Session = Depends(get_db)):
    turma = db.get(TurmasModel, turma_id)
    if not turma:
        raise HTTPException(status_code=404, detail="Turma não encontrada")

    db.delete(turma)
    db.commit()
    return {"detail": f"Turma deletada [{turma.nome}] com sucesso."}


@app.post("/jogo")
def add_jogo(jogo: JogosCreate, db: Session = Depends(get_db)):
    novo = JogosModel(nome=jogo.nome)
    db.add(novo)
    try:
        db.commit()
        db.refresh(novo)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Jogo já existe")

    return novo


@app.delete("/jogo/{jogo_id}")
def delete_jogo(jogo_id: int, db: Session = Depends(get_db)):
    jogo = db.get(JogosModel, jogo_id)
    if not jogo:
        raise HTTPException(status_code=404, detail="Jogo não encontrado")

    db.delete(jogo)
    db.commit()
    return {"detail": f"Jogo {jogo.nome} deletado com sucesso"}


@app.post("/sessao")
def add_sessao(sessao: SessoesCreate, db: Session = Depends(get_db)):
    novo = SessoesModel(
        turma_id=sessao.turma_id,
        jogo_id=sessao.jogo_id,
        palavra=sessao.palavra,
        dificuldade=sessao.dificuldade,
        tempo_total=sessao.tempo_total,
        acertos=sessao.acertos,
        erros=sessao.erros,
    )
    db.add(novo)
    db.commit()
    db.refresh(novo)

    return novo
