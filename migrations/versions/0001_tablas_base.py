"""tablas base: usuarios y atletas

Revision ID: 0001_tablas_base
Revises:
Create Date: 2026-11-04
"""
import sqlalchemy as sa
from alembic import op

revision = "0001_tablas_base"
down_revision = None
branch_labels = None
depends_on = None


def _existe(tabla: str) -> bool:
    # Las bases creadas antes de usar Alembic ya tienen estas tablas.
    return sa.inspect(op.get_bind()).has_table(tabla)


def upgrade():
    if not _existe("usuarios"):
        op.create_table(
            "usuarios",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("nombre", sa.String(100), nullable=False),
            sa.Column("apellido", sa.String(100), nullable=False),
            sa.Column("email", sa.String(255), nullable=False, unique=True),
            sa.Column("rol", sa.Enum("atleta", "entrenador", name="rol_usuario"), nullable=False),
            sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        )
    if not _existe("atletas"):
        op.create_table(
            "atletas",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("usuario_id", sa.Integer(), nullable=False, unique=True),
            sa.Column("nombre", sa.String(100), nullable=False),
            sa.Column("apellido", sa.String(100), nullable=False),
            sa.Column("fecha_nacimiento", sa.Date(), nullable=False),
            sa.Column("direccion", sa.String(255), nullable=True),
            sa.Column(
                "nivel",
                sa.Enum("principiante", "intermedio", "avanzado", name="nivel_atleta"),
                nullable=False,
            ),
            sa.Column("categoria", sa.String(50), nullable=False),
            sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"], ondelete="CASCADE"),
        )


def downgrade():
    op.drop_table("atletas")
    op.drop_table("usuarios")
