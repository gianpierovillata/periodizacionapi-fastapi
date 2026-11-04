from datetime import date, datetime

from sqlalchemy import Boolean, Computed, Date, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class PlanEntrenamiento(Base):
    __tablename__ = "planes_entrenamiento"
    __table_args__ = (
        # Solo puede haber un plan activo por atleta: la columna generada vale
        # atleta_id cuando el plan esta activo y NULL cuando no. MySQL permite
        # varios NULL en un indice unico, asi que solo un plan activo cumple.
        UniqueConstraint("atleta_activo_key", name="uq_plan_activo_por_atleta"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(30), unique=True)
    nombre: Mapped[str] = mapped_column(String(100))
    descripcion: Mapped[str | None] = mapped_column(Text)
    ano: Mapped[int] = mapped_column(Integer)
    fecha_inicio: Mapped[date] = mapped_column(Date)
    fecha_final: Mapped[date] = mapped_column(Date)
    objetivos: Mapped[str | None] = mapped_column(Text)
    activo: Mapped[bool] = mapped_column(Boolean, default=False)
    atleta_id: Mapped[int] = mapped_column(ForeignKey("atletas.id", ondelete="RESTRICT"))
    entrenador_id: Mapped[int] = mapped_column(ForeignKey("entrenadores.id", ondelete="RESTRICT"))
    deporte_id: Mapped[int] = mapped_column(ForeignKey("deportes.id", ondelete="RESTRICT"))
    atleta_activo_key: Mapped[int | None] = mapped_column(
        Integer, Computed("CASE WHEN activo THEN atleta_id END", persisted=True)
    )
    competencias: Mapped[list["Competencia"]] = relationship(
        back_populates="plan",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="Competencia.fecha",
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )


class Competencia(Base):
    __tablename__ = "competencias"

    id: Mapped[int] = mapped_column(primary_key=True)
    plan_id: Mapped[int] = mapped_column(
        ForeignKey("planes_entrenamiento.id", ondelete="CASCADE")
    )
    nombre: Mapped[str] = mapped_column(String(100))
    fecha: Mapped[date] = mapped_column(Date)
    lugar: Mapped[str | None] = mapped_column(String(150))

    plan: Mapped[PlanEntrenamiento] = relationship(back_populates="competencias")
