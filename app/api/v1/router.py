from fastapi import APIRouter

from app.api.v1.endpoints import atletas, deportes, entrenadores, health, planes, usuarios

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(usuarios.router)
api_router.include_router(atletas.router)
api_router.include_router(entrenadores.router)
api_router.include_router(deportes.router)
api_router.include_router(planes.router)
