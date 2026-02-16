from pydantic import BaseModel


class TurmasCreate(BaseModel):
    ano: int
    turma: str


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
