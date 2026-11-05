from typing import Annotated

from fastapi import APIRouter, Query, Response, status

from app.db.session import DbSession
from app.schemas.competencia import CompetenciaCreate, CompetenciaRegistro, CompetenciaUpdate
from app.services import competencia as servicio

router = APIRouter(prefix="/competencias", tags=["competencias"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=CompetenciaRegistro)
def crear_competencia(datos: CompetenciaCreate, db: DbSession):
    return servicio.crear_competencia(db, datos)


@router.get("", response_model=list[CompetenciaRegistro])
def listar_competencias(
    db: DbSession,
    plan_id: int | None = None,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    return servicio.listar_competencias(db, plan_id, skip, limit)


@router.get("/{competencia_id}", response_model=CompetenciaRegistro)
def obtener_competencia(competencia_id: int, db: DbSession):
    return servicio.obtener_competencia(db, competencia_id)


@router.patch("/{competencia_id}", response_model=CompetenciaRegistro)
def actualizar_competencia(competencia_id: int, datos: CompetenciaUpdate, db: DbSession):
    return servicio.actualizar_competencia(db, competencia_id, datos)


@router.delete("/{competencia_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_competencia(competencia_id: int, db: DbSession):
    servicio.eliminar_competencia(db, competencia_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
