from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from ..models import SessoesModel


def listar_sessoes(db: Session):
    return db.query(SessoesModel).all()


def criar_sessao(db: Session, dados):
    nova = SessoesModel(
        turma_id=dados.turma_id,
        jogo_id=dados.jogo_id,
        palavra=dados.palavra,
        aluno_ra=dados.aluno_ra,
        dificuldade=dados.dificuldade,
        tempo_total=dados.tempo_total,
        acertos=dados.acertos,
        erros=dados.erros,
    )
    db.add(nova)
    try:
        db.commit()
        db.refresh(nova)
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(400, detail=str(e.orig))

    return nova


def deletar_sessao(db: Session, sessao_id: int):
    sessao = db.get(SessoesModel, sessao_id)

    if not sessao:
        raise HTTPException(status_code=404, detail="Sessao não encontrada")
    db.delete(sessao)
    db.commit()
    return {"detail": f"Sessao {[sessao_id]} deletada com sucesso"}
