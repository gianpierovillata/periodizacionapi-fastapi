from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.atleta import Atleta
from app.models.deporte import Deporte
from app.models.entrenador import Entrenador
from app.models.plan import PlanEntrenamiento
from app.schemas.deporte import DeporteCreate, DeporteUpdate

NOMBRE_DUPLICADO = "Ya existe un deporte con ese nombre"


def obtener_deporte(db: Session, deporte_id: int) -> Deporte:
    deporte = db.get(Deporte, deporte_id)
    if deporte is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deporte no encontrado")
    return deporte


def listar_deportes(db: Session, tipo: str | None, skip: int, limit: int) -> list[Deporte]:
    consulta = select(Deporte).order_by(Deporte.id).offset(skip).limit(limit)
    if tipo is not None:
        consulta = consulta.where(Deporte.tipo == tipo)
    return list(db.scalars(consulta))


def crear_deporte(db: Session, datos: DeporteCreate) -> Deporte:
    deporte = Deporte(**datos.model_dump())
    db.add(deporte)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=NOMBRE_DUPLICADO)
    db.refresh(deporte)
    return deporte


def actualizar_deporte(db: Session, deporte_id: int, datos: DeporteUpdate) -> Deporte:
    deporte = obtener_deporte(db, deporte_id)
    for campo, valor in datos.model_dump(exclude_unset=True).items():
        setattr(deporte, campo, valor)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=NOMBRE_DUPLICADO)
    db.refresh(deporte)
    return deporte


def eliminar_deporte(db: Session, deporte_id: int) -> None:
    deporte = obtener_deporte(db, deporte_id)
    en_uso = (
        db.scalar(select(Atleta.id).where(Atleta.deporte_id == deporte_id).limit(1)) is not None
        or db.scalar(select(Entrenador.id).where(Entrenador.deporte_id == deporte_id).limit(1))
        is not None
        or db.scalar(select(PlanEntrenamiento.id).where(PlanEntrenamiento.deporte_id == deporte_id).limit(1))
        is not None
    )
    if en_uso:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El deporte tiene atletas, entrenadores o planes asociados",
        )
    db.delete(deporte)
    db.commit()
