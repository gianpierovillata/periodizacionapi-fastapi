from datetime import date

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.plan import Competencia, PlanEntrenamiento
from app.schemas.plan import CompetenciaCreate, PlanCreate, PlanUpdate
from app.services.atleta import obtener_atleta
from app.services.deporte import obtener_deporte
from app.services.entrenador import obtener_entrenador


def obtener_plan(db: Session, plan_id: int) -> PlanEntrenamiento:
    plan = db.get(PlanEntrenamiento, plan_id)
    if plan is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan no encontrado")
    return plan


def listar_planes(
    db: Session,
    atleta_id: int | None,
    entrenador_id: int | None,
    ano: int | None,
    activo: bool | None,
    skip: int,
    limit: int,
) -> list[PlanEntrenamiento]:
    consulta = select(PlanEntrenamiento).order_by(PlanEntrenamiento.id).offset(skip).limit(limit)
    if atleta_id is not None:
        consulta = consulta.where(PlanEntrenamiento.atleta_id == atleta_id)
    if entrenador_id is not None:
        consulta = consulta.where(PlanEntrenamiento.entrenador_id == entrenador_id)
    if ano is not None:
        consulta = consulta.where(PlanEntrenamiento.ano == ano)
    if activo is not None:
        consulta = consulta.where(PlanEntrenamiento.activo.is_(activo))
    return list(db.scalars(consulta))


def planes_de_atleta(db: Session, atleta_id: int, skip: int, limit: int) -> list[PlanEntrenamiento]:
    obtener_atleta(db, atleta_id)
    consulta = (
        select(PlanEntrenamiento)
        .where(PlanEntrenamiento.atleta_id == atleta_id)
        .order_by(PlanEntrenamiento.id)
        .offset(skip)
        .limit(limit)
    )
    return list(db.scalars(consulta))


def plan_activo_de_atleta(db: Session, atleta_id: int) -> PlanEntrenamiento:
    obtener_atleta(db, atleta_id)
    plan = db.scalar(
        select(PlanEntrenamiento).where(
            PlanEntrenamiento.atleta_id == atleta_id,
            PlanEntrenamiento.activo.is_(True),
        )
    )
    if plan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El atleta no tiene un plan activo",
        )
    return plan


def _validar_fechas(inicio: date, final: date) -> None:
    if inicio > final:
        raise HTTPException(
            status_code=422,
            detail="La fecha de inicio debe ser anterior o igual a la fecha final",
        )


def _validar_referencias(db: Session, atleta_id: int, entrenador_id: int, deporte_id: int) -> None:
    atleta = obtener_atleta(db, atleta_id)
    obtener_entrenador(db, entrenador_id)
    obtener_deporte(db, deporte_id)
    if atleta.entrenador_id != entrenador_id:
        raise HTTPException(
            status_code=422,
            detail="El entrenador del plan debe ser el entrenador actual del atleta",
        )


def _codigo_en_uso(db: Session, codigo: str, excepto_id: int | None = None) -> bool:
    consulta = select(PlanEntrenamiento.id).where(PlanEntrenamiento.codigo == codigo)
    if excepto_id is not None:
        consulta = consulta.where(PlanEntrenamiento.id != excepto_id)
    return db.scalar(consulta.limit(1)) is not None


def _desactivar_otros(db: Session, atleta_id: int, excepto_id: int | None = None) -> None:
    consulta = select(PlanEntrenamiento).where(
        PlanEntrenamiento.atleta_id == atleta_id,
        PlanEntrenamiento.activo.is_(True),
    )
    if excepto_id is not None:
        consulta = consulta.where(PlanEntrenamiento.id != excepto_id)
    for otro in db.scalars(consulta):
        otro.activo = False
    # Se escribe antes de activar el nuevo, para no chocar con el indice unico.
    db.flush()


def _confirmar(db: Session) -> None:
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Los datos del plan entran en conflicto con otro registro",
        )


def _competencias(lista: list[CompetenciaCreate]) -> list[Competencia]:
    return [Competencia(**c.model_dump()) for c in lista]


def crear_plan(db: Session, datos: PlanCreate) -> PlanEntrenamiento:
    _validar_fechas(datos.fecha_inicio, datos.fecha_final)
    _validar_referencias(db, datos.atleta_id, datos.entrenador_id, datos.deporte_id)
    if _codigo_en_uso(db, datos.codigo):
        raise HTTPException(status_code=409, detail="Ya existe un plan con ese código")

    plan = PlanEntrenamiento(**datos.model_dump(exclude={"competencias"}))
    plan.competencias = _competencias(datos.competencias)
    if datos.activo:
        _desactivar_otros(db, datos.atleta_id)
    db.add(plan)
    _confirmar(db)
    db.refresh(plan)
    return plan


def actualizar_plan(db: Session, plan_id: int, datos: PlanUpdate) -> PlanEntrenamiento:
    plan = obtener_plan(db, plan_id)
    cambios = datos.model_dump(exclude_unset=True, exclude={"competencias"})

    _validar_referencias(
        db,
        plan.atleta_id,
        cambios.get("entrenador_id", plan.entrenador_id),
        cambios.get("deporte_id", plan.deporte_id),
    )
    _validar_fechas(
        cambios.get("fecha_inicio", plan.fecha_inicio),
        cambios.get("fecha_final", plan.fecha_final),
    )
    if "codigo" in cambios and _codigo_en_uso(db, cambios["codigo"], excepto_id=plan.id):
        raise HTTPException(status_code=409, detail="Ya existe un plan con ese código")

    for campo, valor in cambios.items():
        setattr(plan, campo, valor)
    if datos.competencias is not None:
        plan.competencias = _competencias(datos.competencias)
    _confirmar(db)
    db.refresh(plan)
    return plan


def eliminar_plan(db: Session, plan_id: int) -> None:
    plan = obtener_plan(db, plan_id)
    db.delete(plan)
    db.commit()


def activar_plan(db: Session, plan_id: int) -> PlanEntrenamiento:
    plan = obtener_plan(db, plan_id)
    if not plan.activo:
        _desactivar_otros(db, plan.atleta_id, excepto_id=plan.id)
        plan.activo = True
        _confirmar(db)
    db.refresh(plan)
    return plan


def desactivar_plan(db: Session, plan_id: int) -> PlanEntrenamiento:
    plan = obtener_plan(db, plan_id)
    plan.activo = False
    _confirmar(db)
    db.refresh(plan)
    return plan
