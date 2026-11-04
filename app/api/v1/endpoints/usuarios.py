from typing import Annotated

from fastapi import APIRouter, Query, Response, status

from app.db.session import DbSession
from app.models.usuario import RolUsuario
from app.schemas.usuario import UsuarioCreate, UsuarioRead, UsuarioUpdate
from app.services import usuario as servicio

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=UsuarioRead)
def crear_usuario(datos: UsuarioCreate, db: DbSession):
    return servicio.crear_usuario(db, datos)


@router.get("", response_model=list[UsuarioRead])
def listar_usuarios(
    db: DbSession,
    rol: RolUsuario | None = None,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    return servicio.listar_usuarios(db, rol, skip, limit)


@router.get("/{usuario_id}", response_model=UsuarioRead)
def obtener_usuario(usuario_id: int, db: DbSession):
    return servicio.obtener_usuario(db, usuario_id)


@router.patch("/{usuario_id}", response_model=UsuarioRead)
def actualizar_usuario(usuario_id: int, datos: UsuarioUpdate, db: DbSession):
    return servicio.actualizar_usuario(db, usuario_id, datos)


@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_usuario(usuario_id: int, db: DbSession):
    servicio.eliminar_usuario(db, usuario_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
