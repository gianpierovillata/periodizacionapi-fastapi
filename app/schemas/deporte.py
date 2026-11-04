from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class DeporteCreate(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    descripcion: str | None = Field(default=None, max_length=1000)
    tipo: str = Field(min_length=1, max_length=50)
    imagen_url: str | None = Field(default=None, max_length=500)


class DeporteUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=1, max_length=100)
    descripcion: str | None = Field(default=None, max_length=1000)
    tipo: str | None = Field(default=None, min_length=1, max_length=50)
    imagen_url: str | None = Field(default=None, max_length=500)

    @field_validator("nombre", "tipo", mode="before")
    @classmethod
    def no_nulo(cls, valor):
        if valor is None:
            raise ValueError("no puede ser nulo")
        return valor


class DeporteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    descripcion: str | None
    tipo: str
    imagen_url: str | None
    created_at: datetime
    updated_at: datetime
