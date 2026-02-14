from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from models import TurmasModel, JogosModel, SessoesModel


def listar_turmas(db: Session):
    return db.query(TurmasModel).all()


def criar_turma(db: Session, nome: str):
    nova = TurmasModel(nome=nome)
    db.add(nova)
    try:
        db.commit()
        db.refresh(nova)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Turma já existe")
    return nova


def deletar_turma(db: Session, turma_id: int):
    turma = db.get(TurmasModel, turma_id)
    if not turma:
        raise HTTPException(status_code=404, detail="Turma não encontrada")

    db.delete(turma)
    db.commit()
    return {"detail": f"Turma deletada [{turma.nome}] com sucesso."}


def criar_jogo(db: Session, nome: str):
    novo = JogosModel(nome=nome)
    db.add(novo)
    try:
        db.commit()
        db.refresh(novo)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Jogo já existe")
    return novo


def deletar_jogo(db: Session, jogo_id: int):
    jogo = db.get(JogosModel, jogo_id)
    if not jogo:
        raise HTTPException(status_code=404, detail="Jogo não encontrado")

    db.delete(jogo)
    db.commit()
    return {"detail": f"Jogo {jogo.nome} deletado com sucesso"}


def criar_sessao(db: Session, dados):
    nova = SessoesModel(
        turma_id=dados.turma_id,
        jogo_id=dados.jogo_id,
        palavra=dados.palavra,
        dificuldade=dados.dificuldade,
        tempo_total=dados.tempo_total,
        acertos=dados.acertos,
        erros=dados.erros,
    )
    db.add(nova)
    db.commit()
    db.refresh(nova)
    return nova
