from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CompetenciaCreate(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    fecha: date
    lugar: str | None = Field(default=None, max_length=150)


class CompetenciaRead(CompetenciaCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int


class PlanCreate(BaseModel):
    codigo: str = Field(min_length=1, max_length=30)
    nombre: str = Field(min_length=1, max_length=100)
    descripcion: str | None = None
    ano: int = Field(ge=2000, le=2100)
    fecha_inicio: date
    fecha_final: date
    objetivos: str | None = None
    atleta_id: int = Field(gt=0)
    entrenador_id: int = Field(gt=0)
    deporte_id: int = Field(gt=0)
    activo: bool = False
    competencias: list[CompetenciaCreate] = []


class PlanUpdate(BaseModel):
    codigo: str | None = Field(default=None, min_length=1, max_length=30)
    nombre: str | None = Field(default=None, min_length=1, max_length=100)
    descripcion: str | None = None
    ano: int | None = Field(default=None, ge=2000, le=2100)
    fecha_inicio: date | None = None
    fecha_final: date | None = None
    objetivos: str | None = None
    entrenador_id: int | None = Field(default=None, gt=0)
    deporte_id: int | None = Field(default=None, gt=0)
    # Si se envia, reemplaza la lista completa de competencias.
    competencias: list[CompetenciaCreate] | None = None

    @field_validator(
        "codigo", "nombre", "ano", "fecha_inicio", "fecha_final",
        "entrenador_id", "deporte_id", "competencias", mode="before",
    )
    @classmethod
    def no_nulo(cls, valor):
        if valor is None:
            raise ValueError("no puede ser nulo")
        return valor


class PlanRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    codigo: str
    nombre: str
    descripcion: str | None
    ano: int
    fecha_inicio: date
    fecha_final: date
    objetivos: str | None
    activo: bool
    atleta_id: int
    entrenador_id: int
    deporte_id: int
    competencias: list[CompetenciaRead]
    created_at: datetime
    updated_at: datetime
