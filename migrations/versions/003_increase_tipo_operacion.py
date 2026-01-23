"""Increase tipo_operacion column size to 50 characters

Revision ID: 003_increase_tipo_operacion
Revises: 
Create Date: 2026-01-22 16:40:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003_increase_tipo_operacion'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Cambiar el tamaño de la columna tipo_operacion de 20 a 50
    op.alter_column('historial_control', 'tipo_operacion',
               existing_type=sa.String(20),
               type_=sa.String(50),
               existing_nullable=False)


def downgrade():
    # Revertir el cambio
    op.alter_column('historial_control', 'tipo_operacion',
               existing_type=sa.String(50),
               type_=sa.String(20),
               existing_nullable=False)
