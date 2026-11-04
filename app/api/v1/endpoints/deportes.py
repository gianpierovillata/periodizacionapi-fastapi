from typing import Annotated

from fastapi import APIRouter, Query, Response, status

from app.db.session import DbSession
from app.schemas.deporte import DeporteCreate, DeporteRead, DeporteUpdate
from app.services import deporte as servicio

router = APIRouter(prefix="/deportes", tags=["deportes"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=DeporteRead)
def crear_deporte(datos: DeporteCreate, db: DbSession):
    return servicio.crear_deporte(db, datos)


@router.get("", response_model=list[DeporteRead])
def listar_deportes(
    db: DbSession,
    tipo: str | None = None,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    return servicio.listar_deportes(db, tipo, skip, limit)


@router.get("/{deporte_id}", response_model=DeporteRead)
def obtener_deporte(deporte_id: int, db: DbSession):
    return servicio.obtener_deporte(db, deporte_id)


@router.patch("/{deporte_id}", response_model=DeporteRead)
def actualizar_deporte(deporte_id: int, datos: DeporteUpdate, db: DbSession):
    return servicio.actualizar_deporte(db, deporte_id, datos)


@router.delete("/{deporte_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_deporte(deporte_id: int, db: DbSession):
    servicio.eliminar_deporte(db, deporte_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
