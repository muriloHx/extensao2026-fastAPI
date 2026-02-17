#ENDPOINTS DE TURMAS
from fastapi import APIRouter, Depends
from ...services import turmas_services
from ...database import get_db
from sqlalchemy.orm import Session


router = APIRouter(
    prefix="/turmas",
    tags=["Client"]
)

@router.get("/")
def get_turmas(db: Session = Depends(get_db)):
    return turmas_services.listar_turmas(db)
