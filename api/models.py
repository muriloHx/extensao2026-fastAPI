import os
from datetime import datetime
from typing import List

from dotenv import load_dotenv
from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, create_engine, func, UniqueConstraint
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)



class Base(DeclarativeBase):
    pass


class TurmasModel(Base):
    __tablename__ = "turmas"

    __table_args__ = (
        UniqueConstraint("ano", "turma", name="uq_ano_turma"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    ano: Mapped[int] = mapped_column(Integer, nullable=True)
    turma: Mapped[str] = mapped_column(String, nullable=True)

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
