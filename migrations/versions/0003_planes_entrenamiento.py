"""planes de entrenamiento y competencias

Revision ID: 0003_planes_entrenamiento
Revises: 0002_deportes_entrenadores
Create Date: 2026-11-04
"""
import sqlalchemy as sa
from alembic import op

revision = "0003_planes_entrenamiento"
down_revision = "0002_deportes_entrenadores"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "planes_entrenamiento",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("codigo", sa.String(30), nullable=False, unique=True),
        sa.Column("nombre", sa.String(100), nullable=False),
        sa.Column("descripcion", sa.Text(), nullable=True),
        sa.Column("ano", sa.Integer(), nullable=False),
        sa.Column("fecha_inicio", sa.Date(), nullable=False),
        sa.Column("fecha_final", sa.Date(), nullable=False),
        sa.Column("objetivos", sa.Text(), nullable=True),
        sa.Column("activo", sa.Boolean(), nullable=False),
        sa.Column("atleta_id", sa.Integer(), nullable=False),
        sa.Column("entrenador_id", sa.Integer(), nullable=False),
        sa.Column("deporte_id", sa.Integer(), nullable=False),
        sa.Column(
            "atleta_activo_key",
            sa.Integer(),
            sa.Computed("CASE WHEN activo THEN atleta_id END", persisted=True),
            nullable=True,
        ),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["atleta_id"], ["atletas.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["entrenador_id"], ["entrenadores.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["deporte_id"], ["deportes.id"], ondelete="RESTRICT"),
        sa.UniqueConstraint("atleta_activo_key", name="uq_plan_activo_por_atleta"),
    )
    op.create_table(
        "competencias",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("plan_id", sa.Integer(), nullable=False),
        sa.Column("nombre", sa.String(100), nullable=False),
        sa.Column("fecha", sa.Date(), nullable=False),
        sa.Column("lugar", sa.String(150), nullable=True),
        sa.ForeignKeyConstraint(["plan_id"], ["planes_entrenamiento.id"], ondelete="CASCADE"),
    )


def downgrade():
    op.drop_table("competencias")
    op.drop_table("planes_entrenamiento")
