from typing import Annotated

from fastapi import APIRouter, Query, Response, status

from app.db.session import DbSession
from app.schemas.atleta import AtletaRead
from app.schemas.entrenador import EntrenadorCreate, EntrenadorRead, EntrenadorUpdate
from app.services import entrenador as servicio

router = APIRouter(prefix="/entrenadores", tags=["entrenadores"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=EntrenadorRead)
def crear_entrenador(datos: EntrenadorCreate, db: DbSession):
    return servicio.crear_entrenador(db, datos)


@router.get("", response_model=list[EntrenadorRead])
def listar_entrenadores(
    db: DbSession,
    deporte_id: int | None = None,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    return servicio.listar_entrenadores(db, deporte_id, skip, limit)


@router.get("/{entrenador_id}", response_model=EntrenadorRead)
def obtener_entrenador(entrenador_id: int, db: DbSession):
    return servicio.obtener_entrenador(db, entrenador_id)


@router.get("/{entrenador_id}/atletas", response_model=list[AtletaRead])
def listar_atletas_de_entrenador(
    entrenador_id: int,
    db: DbSession,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    return servicio.listar_atletas_de_entrenador(db, entrenador_id, skip, limit)


@router.patch("/{entrenador_id}", response_model=EntrenadorRead)
def actualizar_entrenador(entrenador_id: int, datos: EntrenadorUpdate, db: DbSession):
    return servicio.actualizar_entrenador(db, entrenador_id, datos)


@router.delete("/{entrenador_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_entrenador(entrenador_id: int, db: DbSession):
    servicio.eliminar_entrenador(db, entrenador_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
