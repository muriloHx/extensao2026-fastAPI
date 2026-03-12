from datetime import datetime
from typing import List

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    Index,
    func,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)


class Base(DeclarativeBase):
    pass


# =========================================================
# TURMAS
# =========================================================

class TurmasModel(Base):
    __tablename__ = "turmas"

    __table_args__ = (
        UniqueConstraint("ano", "turma", name="uq_ano_turma"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    ano: Mapped[int] = mapped_column(Integer, nullable=False)
    turma: Mapped[str] = mapped_column(String(10), nullable=False)

    alunos: Mapped[List["AlunosModel"]] = relationship(
        back_populates="turma",
        cascade="all, delete-orphan",
    )

    sessoes: Mapped[List["SessoesModel"]] = relationship(
        back_populates="turma",
        cascade="all, delete-orphan",
    )


# =========================================================
# ALUNOS
# =========================================================

class AlunosModel(Base):
    __tablename__ = "alunos"

    __table_args__ = (
        Index("ix_alunos_ra", "ra"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    ra: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
    )

    nome: Mapped[str] = mapped_column(String(120), nullable=False)

    turma_id: Mapped[int] = mapped_column(
        ForeignKey("turmas.id", ondelete="CASCADE"),
        nullable=False,
    )

    turma: Mapped["TurmasModel"] = relationship(
        back_populates="alunos"
    )

    sessoes: Mapped[List["SessoesModel"]] = relationship(
        back_populates="aluno",
        cascade="all, delete-orphan",
    )


# =========================================================
# JOGOS
# =========================================================

class JogosModel(Base):
    __tablename__ = "jogos"

    id: Mapped[int] = mapped_column(primary_key=True)

    nome: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )

    sessoes: Mapped[List["SessoesModel"]] = relationship(
        back_populates="jogo",
        cascade="all, delete-orphan",
    )


# =========================================================
# SESSÕES
# =========================================================

class SessoesModel(Base):
    __tablename__ = "sessoes"

    __table_args__ = (
        Index("ix_sessoes_data", "data_execucao"),
        Index("ix_sessoes_aluno", "aluno_ra"),
        Index("ix_sessoes_jogo", "jogo_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    turma_id: Mapped[int] = mapped_column(
        ForeignKey("turmas.id", ondelete="CASCADE"),
        nullable=False,
    )

    jogo_id: Mapped[int] = mapped_column(
        ForeignKey("jogos.id", ondelete="CASCADE"),
        nullable=False,
    )

    aluno_ra: Mapped[str] = mapped_column(
        ForeignKey("alunos.ra", ondelete="CASCADE"),
        nullable=False,
    )

    palavra: Mapped[str | None] = mapped_column(String(120))
    dificuldade: Mapped[str | None] = mapped_column(String(20))

    tempo_total: Mapped[float | None] = mapped_column(Float)

    acertos: Mapped[int | None] = mapped_column(Integer)
    erros: Mapped[int | None] = mapped_column(Integer)

    data_execucao: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    aluno: Mapped["AlunosModel"] = relationship(
        back_populates="sessoes"
    )

    turma: Mapped["TurmasModel"] = relationship(
        back_populates="sessoes"
    )

    jogo: Mapped["JogosModel"] = relationship(
        back_populates="sessoes"
    )
