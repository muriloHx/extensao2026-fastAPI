#ENDPOINTS DE JOGOS
from fastapi import APIRouter, Depends, Header, HTTPException, Request


router = APIRouter(
    prefix="/internal/turmas",
    tags=["Turmas Internas"]
)
