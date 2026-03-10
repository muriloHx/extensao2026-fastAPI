from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from ..models import AlunosModel


def listar_aluno(db:Session):
    return db.query(AlunosModel).all()

def criar_aluno(db:Session, dados):
    nova = AlunosModel(
        turma_id=dados.turma_id,
        ra=dados.ra,
        nome=dados.nome,
    )
    db.add(nova)
    db.commit()
    db.refresh(nova)
    return nova

def deletar_aluno(db:Session, aluno_id:int):
    aluno = db.get(AlunosModel, aluno_id)
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")
    db.delete(aluno)
    db.commit()
    return {"detail": f"Aluno ID[{aluno_id}] deletado com sucesso"}
