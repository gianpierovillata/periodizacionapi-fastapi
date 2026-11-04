"""deportes, entrenadores y relaciones de atletas

Revision ID: 0002_deportes_entrenadores
Revises: 0001_tablas_base
Create Date: 2026-11-04
"""
import sqlalchemy as sa
from alembic import op

revision = "0002_deportes_entrenadores"
down_revision = "0001_tablas_base"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "deportes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nombre", sa.String(100), nullable=False, unique=True),
        sa.Column("descripcion", sa.Text(), nullable=True),
        sa.Column("tipo", sa.String(50), nullable=False),
        sa.Column("imagen_url", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "entrenadores",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("usuario_id", sa.Integer(), nullable=False, unique=True),
        sa.Column("nombre", sa.String(100), nullable=False),
        sa.Column("apellido", sa.String(100), nullable=False),
        sa.Column(
            "nivel",
            sa.Enum("principiante", "intermedio", "avanzado", name="nivel_entrenador"),
            nullable=False,
        ),
        sa.Column("deporte_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["deporte_id"], ["deportes.id"], ondelete="RESTRICT"),
    )
    op.add_column("atletas", sa.Column("entrenador_id", sa.Integer(), nullable=True))
    op.add_column("atletas", sa.Column("deporte_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_atletas_entrenador_id", "atletas", "entrenadores",
        ["entrenador_id"], ["id"], ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_atletas_deporte_id", "atletas", "deportes",
        ["deporte_id"], ["id"], ondelete="RESTRICT",
    )


def downgrade():
    op.drop_constraint("fk_atletas_deporte_id", "atletas", type_="foreignkey")
    op.drop_constraint("fk_atletas_entrenador_id", "atletas", type_="foreignkey")
    op.drop_column("atletas", "deporte_id")
    op.drop_column("atletas", "entrenador_id")
    op.drop_table("entrenadores")
    op.drop_table("deportes")
