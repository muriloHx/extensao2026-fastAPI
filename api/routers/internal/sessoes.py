#ENDPOINTS DE SESSOES
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from ...services import sessoes_services
from ... import schemas
from ...database import get_db, Session


router = APIRouter(
    prefix="/sessoes",
    tags=["Sessoes Internas"]
)

@router.get("/")
def get_sessoes(db: Session = Depends(get_db)):
    return jogos_services.listar_sessoes(db)

@router.delete("/{sessao_id}")
def delete_sessoes(sessao_id:int, db: Session = Depends(get_db)):
    return jogos_services.deletar_sessao(db, sessao_id)
