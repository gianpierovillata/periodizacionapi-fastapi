from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.atleta import NivelAtleta


class Entrenador(Base):
    __tablename__ = "entrenadores"

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id", ondelete="CASCADE"), unique=True
    )
    nombre: Mapped[str] = mapped_column(String(100))
    apellido: Mapped[str] = mapped_column(String(100))
    nivel: Mapped[NivelAtleta] = mapped_column(
        Enum(NivelAtleta, name="nivel_entrenador", values_callable=lambda e: [m.value for m in e])
    )
    deporte_id: Mapped[int] = mapped_column(ForeignKey("deportes.id", ondelete="RESTRICT"))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
