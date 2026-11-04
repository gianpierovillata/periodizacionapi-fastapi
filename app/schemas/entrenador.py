from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.atleta import NivelAtleta


class EntrenadorCreate(BaseModel):
    usuario_id: int = Field(gt=0)
    nombre: str = Field(min_length=1, max_length=100)
    apellido: str = Field(min_length=1, max_length=100)
    nivel: NivelAtleta
    deporte_id: int = Field(gt=0)


class EntrenadorUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=1, max_length=100)
    apellido: str | None = Field(default=None, min_length=1, max_length=100)
    nivel: NivelAtleta | None = None
    deporte_id: int | None = Field(default=None, gt=0)

    @field_validator("nombre", "apellido", "nivel", "deporte_id", mode="before")
    @classmethod
    def no_nulo(cls, valor):
        if valor is None:
            raise ValueError("no puede ser nulo")
        return valor


class EntrenadorRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    usuario_id: int
    nombre: str
    apellido: str
    nivel: NivelAtleta
    deporte_id: int
    created_at: datetime
    updated_at: datetime
