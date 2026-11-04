from typing import Annotated

from fastapi import APIRouter, Query, Response, status

from app.db.session import DbSession
from app.schemas.plan import PlanCreate, PlanRead, PlanUpdate
from app.services import plan as servicio

router = APIRouter(prefix="/planes", tags=["planes"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=PlanRead)
def crear_plan(datos: PlanCreate, db: DbSession):
    return servicio.crear_plan(db, datos)


@router.get("", response_model=list[PlanRead])
def listar_planes(
    db: DbSession,
    atleta_id: int | None = None,
    entrenador_id: int | None = None,
    ano: int | None = None,
    activo: bool | None = None,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    return servicio.listar_planes(db, atleta_id, entrenador_id, ano, activo, skip, limit)


@router.get("/{plan_id}", response_model=PlanRead)
def obtener_plan(plan_id: int, db: DbSession):
    return servicio.obtener_plan(db, plan_id)


@router.patch("/{plan_id}", response_model=PlanRead)
def actualizar_plan(plan_id: int, datos: PlanUpdate, db: DbSession):
    return servicio.actualizar_plan(db, plan_id, datos)


@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_plan(plan_id: int, db: DbSession):
    servicio.eliminar_plan(db, plan_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{plan_id}/activar", response_model=PlanRead)
def activar_plan(plan_id: int, db: DbSession):
    return servicio.activar_plan(db, plan_id)


@router.post("/{plan_id}/desactivar", response_model=PlanRead)
def desactivar_plan(plan_id: int, db: DbSession):
    return servicio.desactivar_plan(db, plan_id)
