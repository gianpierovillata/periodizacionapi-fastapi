from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator

from app.models.atleta import NivelAtleta


def calcular_edad(fecha_nacimiento: date, hoy: date | None = None) -> int:
    hoy = hoy or date.today()
    cumpleanos_pasado = (hoy.month, hoy.day) >= (fecha_nacimiento.month, fecha_nacimiento.day)
    return hoy.year - fecha_nacimiento.year - (0 if cumpleanos_pasado else 1)


def _no_futura(valor: date) -> date:
    if valor > date.today():
        raise ValueError("La fecha de nacimiento no puede ser futura")
    return valor


class AtletaCreate(BaseModel):
    usuario_id: int = Field(gt=0)
    nombre: str = Field(min_length=1, max_length=100)
    apellido: str = Field(min_length=1, max_length=100)
    fecha_nacimiento: date
    direccion: str | None = Field(default=None, max_length=255)
    nivel: NivelAtleta
    categoria: str = Field(min_length=1, max_length=50)

    @field_validator("fecha_nacimiento")
    @classmethod
    def fecha_no_futura(cls, valor: date) -> date:
        return _no_futura(valor)


class AtletaUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=1, max_length=100)
    apellido: str | None = Field(default=None, min_length=1, max_length=100)
    fecha_nacimiento: date | None = None
    direccion: str | None = Field(default=None, max_length=255)
    nivel: NivelAtleta | None = None
    categoria: str | None = Field(default=None, min_length=1, max_length=50)

    @field_validator("nombre", "apellido", "fecha_nacimiento", "nivel", "categoria", mode="before")
    @classmethod
    def no_nulo(cls, valor):
        if valor is None:
            raise ValueError("no puede ser nulo")
        return valor

    @field_validator("fecha_nacimiento")
    @classmethod
    def fecha_no_futura(cls, valor: date) -> date:
        return _no_futura(valor)


class AtletaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    usuario_id: int
    nombre: str
    apellido: str
    fecha_nacimiento: date
    direccion: str | None
    nivel: NivelAtleta
    categoria: str
    created_at: datetime
    updated_at: datetime

    @computed_field
    @property
    def edad(self) -> int:
        return calcular_edad(self.fecha_nacimiento)
