from pydantic import BaseModel, field_validator, model_validator
from typing import Self


DIFICULDADES_VALIDAS = {"facil", "medio", "dificil"}


class TurmasCreate(BaseModel):
    ano: int
    turma: str

    @field_validator("ano")
    @classmethod
    def ano_valido(cls, v: int) -> int:
        if v < 1 or v > 9:
            raise ValueError("ano deve ser entre 1 e 9")
        return v

    @field_validator("turma")
    @classmethod
    def turma_valida(cls, v: str) -> str:
        v = v.strip().upper()
        if not v or len(v) > 2:
            raise ValueError("turma deve ter 1 ou 2 caracteres")
        return v


class JogosCreate(BaseModel):
    nome: str

    @field_validator("nome")
    @classmethod
    def nome_valido(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("nome não pode ser vazio")
        if len(v) > 100:
            raise ValueError("nome deve ter no máximo 100 caracteres")
        return v


class SessoesCreate(BaseModel):
    turma_id: int
    jogo_id: int
    aluno_ra: str
    palavra: str | None = None
    dificuldade: str | None = None
    tempo_total: float | None = None
    acertos: int | None = None
    erros: int | None = None

    @field_validator("turma_id", "jogo_id")
    @classmethod
    def ids_positivos(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("id deve ser positivo")
        return v

    @field_validator("aluno_ra")
    @classmethod
    def ra_valido(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("aluno_ra não pode ser vazio")
        return v

    @field_validator("dificuldade")
    @classmethod
    def dificuldade_valida(cls, v: str | None) -> str | None:
        if v is not None and v not in DIFICULDADES_VALIDAS:
            raise ValueError(f"dificuldade deve ser uma de: {DIFICULDADES_VALIDAS}")
        return v

    @field_validator("tempo_total")
    @classmethod
    def tempo_valido(cls, v: float | None) -> float | None:
        if v is not None and v < 0:
            raise ValueError("tempo_total não pode ser negativo")
        return v

    @field_validator("acertos", "erros")
    @classmethod
    def contagens_validas(cls, v: int | None) -> int | None:
        if v is not None and v < 0:
            raise ValueError("acertos/erros não podem ser negativos")
        return v

    @model_validator(mode="after")
    def acertos_erros_coerentes(self) -> Self:
        if self.acertos is not None and self.erros is not None:
            if self.acertos + self.erros == 0:
                raise ValueError("acertos + erros não pode ser zero")
        return self


class AlunosCreate(BaseModel):
    turma_id: int | None = None
    ra: str
    nome: str

    @field_validator("turma_id")
    @classmethod
    def turma_id_valido(cls, v: int | None) -> int | None:
        if v is not None and v <= 0:
            raise ValueError("turma_id deve ser positivo")
        return v

    @field_validator("ra")
    @classmethod
    def ra_valido(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("ra não pode ser vazio")
        if len(v) > 20:
            raise ValueError("ra deve ter no máximo 20 caracteres")
        return v

    @field_validator("nome")
    @classmethod
    def nome_valido(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("nome não pode ser vazio")
        if len(v) > 150:
            raise ValueError("nome deve ter no máximo 150 caracteres")
        return v.title()


class TurmasUpdate(BaseModel):
    ano: int | None = None
    turma: str | None = None

    @field_validator("ano")
    @classmethod
    def ano_valido(cls, v: int | None) -> int | None:
        if v is not None and (v < 1 or v > 9):
            raise ValueError("ano deve ser entre 1 e 9")
        return v

    @field_validator("turma")
    @classmethod
    def turma_valida(cls, v: str | None) -> str | None:
        if v is not None:
            v = v.strip().upper()
            if not v or len(v) > 2:
                raise ValueError("turma deve ter 1 ou 2 caracteres")
        return v.upper()

class AlunosUpdate(BaseModel):
    turma_id: int | None = None
    ra: str | None = None
    nome: str | None = None

    @field_validator("turma_id")
    @classmethod
    def turma_id_valido(cls, v: int | None) -> int | None:
        if v is not None and v <= 0:
            raise ValueError("turma_id deve ser positivo")
        return v

    @field_validator("ra")
    @classmethod
    def ra_valido(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("ra não pode ser vazio")
        if len(v) > 20:
            raise ValueError("ra deve ter no máximo 20 caracteres")
        return v

    @field_validator("nome")
    @classmethod
    def nome_valido(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("nome não pode ser vazio")
        if len(v) > 150:
            raise ValueError("nome deve ter no máximo 150 caracteres")
        return v.title()
