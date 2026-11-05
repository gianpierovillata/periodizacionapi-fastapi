from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.plan import Competencia
from app.schemas.competencia import CompetenciaCreate, CompetenciaUpdate
from app.services.plan import obtener_plan


def obtener_competencia(db: Session, competencia_id: int) -> Competencia:
    competencia = db.get(Competencia, competencia_id)
    if competencia is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Competencia no encontrada"
        )
    return competencia


def listar_competencias(
    db: Session, plan_id: int | None, skip: int, limit: int
) -> list[Competencia]:
    consulta = select(Competencia).order_by(Competencia.fecha, Competencia.id).offset(skip).limit(limit)
    if plan_id is not None:
        consulta = consulta.where(Competencia.plan_id == plan_id)
    return list(db.scalars(consulta))


def crear_competencia(db: Session, datos: CompetenciaCreate) -> Competencia:
    obtener_plan(db, datos.plan_id)
    competencia = Competencia(**datos.model_dump())
    db.add(competencia)
    db.commit()
    db.refresh(competencia)
    return competencia


def actualizar_competencia(
    db: Session, competencia_id: int, datos: CompetenciaUpdate
) -> Competencia:
    competencia = obtener_competencia(db, competencia_id)
    for campo, valor in datos.model_dump(exclude_unset=True).items():
        setattr(competencia, campo, valor)
    db.commit()
    db.refresh(competencia)
    return competencia


def eliminar_competencia(db: Session, competencia_id: int) -> None:
    competencia = obtener_competencia(db, competencia_id)
    db.delete(competencia)
    db.commit()
