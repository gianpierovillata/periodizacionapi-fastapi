from datetime import date

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CompetenciaCreate(BaseModel):
    plan_id: int = Field(gt=0)
    nombre: str = Field(min_length=1, max_length=100)
    fecha: date
    lugar: str | None = Field(default=None, max_length=150)


class CompetenciaUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=1, max_length=100)
    fecha: date | None = None
    lugar: str | None = Field(default=None, max_length=150)

    @field_validator("nombre", "fecha", mode="before")
    @classmethod
    def no_nulo(cls, valor):
        if valor is None:
            raise ValueError("no puede ser nulo")
        return valor


class CompetenciaRegistro(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    plan_id: int
    nombre: str
    fecha: date
    lugar: str | None
