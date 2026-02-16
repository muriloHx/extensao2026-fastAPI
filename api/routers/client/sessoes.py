#ENDPOINTS DE SESSOES
from fastapi import APIRouter
from ..services import sessoes_services
from ... import schemas
from ...database import get_db, Session

router = APIRouter(
    prefix="/client/sessoes",
    tags=["Client Sessoes"]
)
