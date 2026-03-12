# ENDPOINTS DE SESSOES
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ...database import get_db
from ...services import sessoes_services

router = APIRouter(prefix="/sessoes", tags=["Internal"])


@router.get("/")
def get_sessoes(db: Session = Depends(get_db)):
    return sessoes_services.listar_sessoes(db)


@router.delete("/{sessao_id}")
def delete_sessoes(sessao_id: int, db: Session = Depends(get_db)):
    return sessoes_services.deletar_sessao(db, sessao_id)
