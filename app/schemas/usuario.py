from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models.usuario import RolUsuario


class UsuarioCreate(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    apellido: str = Field(min_length=1, max_length=100)
    email: EmailStr = Field(max_length=255)
    rol: RolUsuario


class UsuarioUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=1, max_length=100)
    apellido: str | None = Field(default=None, min_length=1, max_length=100)
    email: EmailStr | None = Field(default=None, max_length=255)
    rol: RolUsuario | None = None

    @field_validator("nombre", "apellido", "email", "rol", mode="before")
    @classmethod
    def no_nulo(cls, valor):
        if valor is None:
            raise ValueError("no puede ser nulo")
        return valor


class UsuarioRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    apellido: str
    email: str
    rol: RolUsuario
    created_at: datetime
    updated_at: datetime
