from fastapi import APIRouter
from app.api.v1 import program

api_router = APIRouter()

api_router.include_router(program.router, prefix="/programs", tags=["programs"])