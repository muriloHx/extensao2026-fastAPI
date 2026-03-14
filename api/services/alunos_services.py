from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..models import AlunosModel

def listar_aluno(db: Session):
    return db.query(AlunosModel).all()


def criar_aluno(db: Session, dados):
    nova = AlunosModel(
        turma_id=dados.turma_id,
        ra=dados.ra,
        nome=dados.nome,
    )
    db.add(nova)
    try:
        db.commit()
        db.refresh(nova)
    except IntegrityError:
        db.rollback()
        return HTTPException(status_code=400, detail="Aluno já existe")
    return nova


def deletar_aluno(db: Session, aluno_id: int):
    aluno = db.get(AlunosModel, aluno_id)
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")
    db.delete(aluno)
    db.commit()
    return {"detail": f"Aluno ID[{aluno_id}] deletado com sucesso"}


def get_aluno(db: Session, aluno_id: int):
    aluno = db.get(AlunosModel, aluno_id)
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")
    return aluno

def atualizar_aluno(db: Session, aluno_id: int, dados):
    aluno = db.get(AlunosModel, aluno_id)
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")

    campos = dados.model_dump(exclude_unset=True, exclude_none=True)
    if not campos:
            raise HTTPException(status_code=400, detail="Nenhum campo enviado")

    for campo, valor in campos.items():
            setattr(aluno, campo, valor)

    db.commit()
    db.refresh(aluno)
    return aluno
