# ENDPOINTS DE JOGOS
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ...database import get_db
from ...services import jogos_services

router = APIRouter(prefix="/jogos", tags=["Client"])


@router.get("/")
def get_jogos(db: Session = Depends(get_db)):
    return jogos_services.listar_jogos(db)
