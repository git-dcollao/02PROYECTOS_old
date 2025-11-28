"""Add fecha_ingreso to trabajador

Revision ID: add_fecha_ingreso_trabajador
Revises: [previous_revision]
Create Date: 2025-01-25 14:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'add_fecha_ingreso_trabajador'
down_revision = None  # Reemplazar con la última revisión
branch_labels = None
depends_on = None

def upgrade():
    # Agregar columna fecha_ingreso a la tabla trabajador
    op.add_column('trabajador', sa.Column('fecha_ingreso', sa.Date(), nullable=True))

def downgrade():
    # Eliminar columna fecha_ingreso de la tabla trabajador
    op.drop_column('trabajador', 'fecha_ingreso')
