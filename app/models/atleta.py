import enum
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class NivelAtleta(str, enum.Enum):
    principiante = "principiante"
    intermedio = "intermedio"
    avanzado = "avanzado"


class Atleta(Base):
    __tablename__ = "atletas"

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id", ondelete="CASCADE"), unique=True
    )
    nombre: Mapped[str] = mapped_column(String(100))
    apellido: Mapped[str] = mapped_column(String(100))
    fecha_nacimiento: Mapped[date] = mapped_column(Date)
    direccion: Mapped[str | None] = mapped_column(String(255))
    nivel: Mapped[NivelAtleta] = mapped_column(
        Enum(NivelAtleta, name="nivel_atleta", values_callable=lambda e: [m.value for m in e])
    )
    categoria: Mapped[str] = mapped_column(String(50))
    entrenador_id: Mapped[int | None] = mapped_column(
        ForeignKey("entrenadores.id", ondelete="RESTRICT")
    )
    deporte_id: Mapped[int | None] = mapped_column(ForeignKey("deportes.id", ondelete="RESTRICT"))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
