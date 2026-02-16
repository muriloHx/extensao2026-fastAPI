#ENDPOINTS DE TURMAS
from fastapi import APIRouter
from ...services import turmas_services
from ... import schemas
from ...database import get_db, Session

router = APIRouter(
    prefix="/client/turmas",
    tags=["Client Turmas"]
)
