from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.atleta import Atleta, NivelAtleta
from app.models.usuario import RolUsuario
from app.schemas.atleta import AtletaCreate, AtletaUpdate
from app.services.usuario import obtener_usuario


def obtener_atleta(db: Session, atleta_id: int) -> Atleta:
    atleta = db.get(Atleta, atleta_id)
    if atleta is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Atleta no encontrado")
    return atleta


def listar_atletas(
    db: Session, nivel: NivelAtleta | None, skip: int, limit: int
) -> list[Atleta]:
    consulta = select(Atleta).order_by(Atleta.id).offset(skip).limit(limit)
    if nivel is not None:
        consulta = consulta.where(Atleta.nivel == nivel)
    return list(db.scalars(consulta))


def crear_atleta(db: Session, datos: AtletaCreate) -> Atleta:
    usuario = obtener_usuario(db, datos.usuario_id)
    if usuario.rol != RolUsuario.atleta:
        raise HTTPException(
            status_code=422,
            detail="El usuario debe tener rol atleta",
        )
    atleta = Atleta(**datos.model_dump())
    db.add(atleta)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un atleta para ese usuario",
        )
    db.refresh(atleta)
    return atleta


def actualizar_atleta(db: Session, atleta_id: int, datos: AtletaUpdate) -> Atleta:
    atleta = obtener_atleta(db, atleta_id)
    for campo, valor in datos.model_dump(exclude_unset=True).items():
        setattr(atleta, campo, valor)
    db.commit()
    db.refresh(atleta)
    return atleta


def eliminar_atleta(db: Session, atleta_id: int) -> None:
    atleta = obtener_atleta(db, atleta_id)
    db.delete(atleta)
    db.commit()
