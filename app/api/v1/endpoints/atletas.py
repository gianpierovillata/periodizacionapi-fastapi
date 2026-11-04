from typing import Annotated

from fastapi import APIRouter, Query, Response, status

from app.db.session import DbSession
from app.models.atleta import NivelAtleta
from app.schemas.atleta import AtletaCreate, AtletaRead, AtletaUpdate
from app.schemas.plan import PlanRead
from app.services import atleta as servicio
from app.services import plan as servicio_plan

router = APIRouter(prefix="/atletas", tags=["atletas"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=AtletaRead)
def crear_atleta(datos: AtletaCreate, db: DbSession):
    return servicio.crear_atleta(db, datos)


@router.get("", response_model=list[AtletaRead])
def listar_atletas(
    db: DbSession,
    nivel: NivelAtleta | None = None,
    deporte_id: int | None = None,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    return servicio.listar_atletas(db, nivel, deporte_id, skip, limit)


@router.get("/{atleta_id}", response_model=AtletaRead)
def obtener_atleta(atleta_id: int, db: DbSession):
    return servicio.obtener_atleta(db, atleta_id)


@router.patch("/{atleta_id}", response_model=AtletaRead)
def actualizar_atleta(atleta_id: int, datos: AtletaUpdate, db: DbSession):
    return servicio.actualizar_atleta(db, atleta_id, datos)


@router.get("/{atleta_id}/planes", response_model=list[PlanRead])
def listar_planes_de_atleta(
    atleta_id: int,
    db: DbSession,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    return servicio_plan.planes_de_atleta(db, atleta_id, skip, limit)


@router.get("/{atleta_id}/plan-activo", response_model=PlanRead)
def obtener_plan_activo_de_atleta(atleta_id: int, db: DbSession):
    return servicio_plan.plan_activo_de_atleta(db, atleta_id)


@router.delete("/{atleta_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_atleta(atleta_id: int, db: DbSession):
    servicio.eliminar_atleta(db, atleta_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
