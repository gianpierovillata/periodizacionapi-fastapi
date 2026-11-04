from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.atleta import Atleta
from app.models.entrenador import Entrenador
from app.models.usuario import RolUsuario
from app.schemas.entrenador import EntrenadorCreate, EntrenadorUpdate
from app.services.deporte import obtener_deporte
from app.services.usuario import obtener_usuario


def obtener_entrenador(db: Session, entrenador_id: int) -> Entrenador:
    entrenador = db.get(Entrenador, entrenador_id)
    if entrenador is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entrenador no encontrado")
    return entrenador


def listar_entrenadores(
    db: Session, deporte_id: int | None, skip: int, limit: int
) -> list[Entrenador]:
    consulta = select(Entrenador).order_by(Entrenador.id).offset(skip).limit(limit)
    if deporte_id is not None:
        consulta = consulta.where(Entrenador.deporte_id == deporte_id)
    return list(db.scalars(consulta))


def crear_entrenador(db: Session, datos: EntrenadorCreate) -> Entrenador:
    usuario = obtener_usuario(db, datos.usuario_id)
    if usuario.rol != RolUsuario.entrenador:
        raise HTTPException(status_code=422, detail="El usuario debe tener rol entrenador")
    obtener_deporte(db, datos.deporte_id)
    entrenador = Entrenador(**datos.model_dump())
    db.add(entrenador)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un entrenador para ese usuario",
        )
    db.refresh(entrenador)
    return entrenador


def actualizar_entrenador(db: Session, entrenador_id: int, datos: EntrenadorUpdate) -> Entrenador:
    entrenador = obtener_entrenador(db, entrenador_id)
    cambios = datos.model_dump(exclude_unset=True)
    if "deporte_id" in cambios:
        obtener_deporte(db, cambios["deporte_id"])
    for campo, valor in cambios.items():
        setattr(entrenador, campo, valor)
    db.commit()
    db.refresh(entrenador)
    return entrenador


def eliminar_entrenador(db: Session, entrenador_id: int) -> None:
    obtener_entrenador(db, entrenador_id)
    tiene_atletas = (
        db.scalar(select(Atleta.id).where(Atleta.entrenador_id == entrenador_id).limit(1))
        is not None
    )
    if tiene_atletas:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El entrenador tiene atletas asignados",
        )
    db.delete(obtener_entrenador(db, entrenador_id))
    db.commit()


def listar_atletas_de_entrenador(
    db: Session, entrenador_id: int, skip: int, limit: int
) -> list[Atleta]:
    obtener_entrenador(db, entrenador_id)
    consulta = (
        select(Atleta)
        .where(Atleta.entrenador_id == entrenador_id)
        .order_by(Atleta.id)
        .offset(skip)
        .limit(limit)
    )
    return list(db.scalars(consulta))
