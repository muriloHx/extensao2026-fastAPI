#ENDPOINTS DE SESSOES
from fastapi import APIRouter, Depends
from ...services import sessoes_services
from ... import schemas
from ...database import get_db
from sqlalchemy.orm import Session


router = APIRouter(
    prefix="/sessoes",
    tags=["Client"]
)

@router.post("/")
def post_sessoes(sessao: schemas.SessoesCreate, db: Session = Depends(get_db)):
    return sessoes_services.criar_sessao(db, sessao)
