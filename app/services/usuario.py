from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.usuario import RolUsuario, Usuario
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate

EMAIL_DUPLICADO = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Ya existe un usuario con ese email",
)


def obtener_usuario(db: Session, usuario_id: int) -> Usuario:
    usuario = db.get(Usuario, usuario_id)
    if usuario is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    return usuario


def listar_usuarios(
    db: Session, rol: RolUsuario | None, skip: int, limit: int
) -> list[Usuario]:
    consulta = select(Usuario).order_by(Usuario.id).offset(skip).limit(limit)
    if rol is not None:
        consulta = consulta.where(Usuario.rol == rol)
    return list(db.scalars(consulta))


def crear_usuario(db: Session, datos: UsuarioCreate) -> Usuario:
    usuario = Usuario(**datos.model_dump())
    db.add(usuario)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise EMAIL_DUPLICADO
    db.refresh(usuario)
    return usuario


def actualizar_usuario(db: Session, usuario_id: int, datos: UsuarioUpdate) -> Usuario:
    usuario = obtener_usuario(db, usuario_id)
    for campo, valor in datos.model_dump(exclude_unset=True).items():
        setattr(usuario, campo, valor)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise EMAIL_DUPLICADO
    db.refresh(usuario)
    return usuario


def eliminar_usuario(db: Session, usuario_id: int) -> None:
    usuario = obtener_usuario(db, usuario_id)
    db.delete(usuario)
    db.commit()
