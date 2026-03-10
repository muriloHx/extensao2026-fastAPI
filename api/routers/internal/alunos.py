#ENDPOINTS DE JOGOS
from fastapi import APIRouter, Depends
from ...services import alunos_services
from ... import schemas
from ...database import get_db
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/alunos",
    tags=["Internal"]
)
@router.get("/")
def get_alunos(db:Session = Depends(get_db)):
    return alunos_services.get_alunos(db)

@router.post("/")
def post_aluno(aluno: schemas.AlunosCreate, db:Session = Depends(get_db)):
    return alunos_services.post_aluno(db, aluno)

@router.delete("/{aluno_id}")
def delete_aluno(aluno_id: int, db:Session = Depends(get_db)):
    return alunos.services.delete_aluno(db, aluno_id)
