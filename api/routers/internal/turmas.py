# ENDPOINTS DE TURMAS
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ... import schemas
from ...database import get_db
from ...services import turmas_services

router = APIRouter(prefix="/turmas", tags=["Internal"])


@router.get("/")
def get_turmas(db: Session = Depends(get_db)):
    return turmas_services.listar_turmas(db)


@router.post("/")
def post_turmas(turma: schemas.TurmasCreate, db: Session = Depends(get_db)):
    return turmas_services.criar_turma(db, turma.turma, turma.ano)


@router.delete("/{turma_id}")
def delete_turma(turma_id: int, db: Session = Depends(get_db)):
    return turmas_services.deletar_turma(db, turma_id)

@router.patch("/{turma_id}")
def patch_turma(turma_id:int, dados: schemas.TurmasUpdate, db: Session = Depends(get_db)):
    return turmas_services.atualizar_turma(db, turma_id, dados)
