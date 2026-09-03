from fastapi import APIRouter
from app.api.v1 import program
from app.api.v1 import college

api_router = APIRouter()

api_router.include_router(program.router, prefix="/programs", tags=["programs"])
api_router.include_router(college.router, prefix="/colleges", tags=["colleges"])