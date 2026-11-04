from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.atleta import Atleta
from app.models.entrenador import Entrenador
from app.models.usuario import RolUsuario, Usuario
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate

EMAIL_DUPLICADO = "Ya existe un usuario con ese email"


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


def _tiene_perfil(db: Session, usuario_id: int) -> bool:
    es_atleta = db.scalar(select(Atleta.id).where(Atleta.usuario_id == usuario_id)) is not None
    es_entrenador = (
        db.scalar(select(Entrenador.id).where(Entrenador.usuario_id == usuario_id)) is not None
    )
    return es_atleta or es_entrenador


def crear_usuario(db: Session, datos: UsuarioCreate) -> Usuario:
    usuario = Usuario(**datos.model_dump())
    db.add(usuario)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=EMAIL_DUPLICADO)
    db.refresh(usuario)
    return usuario


def actualizar_usuario(db: Session, usuario_id: int, datos: UsuarioUpdate) -> Usuario:
    usuario = obtener_usuario(db, usuario_id)
    cambios = datos.model_dump(exclude_unset=True)
    if "rol" in cambios and cambios["rol"] != usuario.rol and _tiene_perfil(db, usuario.id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se puede cambiar el rol de un usuario con perfil de atleta o entrenador",
        )
    for campo, valor in cambios.items():
        setattr(usuario, campo, valor)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=EMAIL_DUPLICADO)
    db.refresh(usuario)
    return usuario


def eliminar_usuario(db: Session, usuario_id: int) -> None:
    usuario = obtener_usuario(db, usuario_id)
    db.delete(usuario)
    try:
        db.commit()
    except IntegrityError:
        # Un entrenador con atletas asignados no puede borrarse (RESTRICT).
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El usuario tiene datos asociados que impiden borrarlo",
        )
