# ENDPOINTS DE ALUNOS
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ... import schemas
from ...database import get_db
from ...services import alunos_services

router = APIRouter(prefix="/alunos", tags=["Internal"])


@router.get("/")
def get_alunos(db: Session = Depends(get_db)):
    return alunos_services.listar_aluno(db)


@router.post("/")
def post_aluno(aluno: schemas.AlunosCreate, db: Session = Depends(get_db)):
    return alunos_services.criar_aluno(db, aluno)


@router.delete("/{aluno_id}")
def delete_aluno(aluno_id: int, db: Session = Depends(get_db)):
    return alunos_services.deletar_aluno(db, aluno_id)

@router.get("/{aluno_id}")
def get_aluno(aluno_id: int, db: Session = Depends(get_db)):
    return alunos_services.get_aluno(db, aluno_id)

@router.patch("/{aluno_id}")
def patch_aluno(aluno_id: int, aluno: schemas.AlunosUpdate, db: Session = Depends(get_db)):
    return alunos_services.atualizar_aluno(db, aluno_id, aluno)
