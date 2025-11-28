"""Add Gantt tables

Revision ID: add_gantt_tables
Revises: [previous_revision]
Create Date: 2024-01-XX XX:XX:XX.XXXXXX

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'add_gantt_tables'
down_revision = None  # Reemplazar con la última revisión
branch_labels = None
depends_on = None

def upgrade():
    # Crear tabla actividades_gantt
    op.create_table('actividades_gantt',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('requerimiento_id', sa.Integer(), nullable=False),
        sa.Column('edt', sa.String(length=50), nullable=False),
        sa.Column('nombre_tarea', sa.String(length=255), nullable=False),
        sa.Column('fecha_inicio', sa.Date(), nullable=False),
        sa.Column('fecha_fin', sa.Date(), nullable=False),
        sa.Column('duracion', sa.Integer(), nullable=False),
        sa.Column('progreso', sa.Float(), nullable=True),
        sa.Column('nivel_esquema', sa.Integer(), nullable=True),
        sa.Column('predecesoras', sa.String(length=255), nullable=True),
        sa.Column('recursos_originales', sa.Text(), nullable=True),
        sa.Column('fecha_creacion', sa.DateTime(), nullable=True),
        sa.Column('fecha_actualizacion', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['requerimiento_id'], ['requerimientos.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Crear tabla recursos_trabajador
    op.create_table('recursos_trabajador',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('requerimiento_id', sa.Integer(), nullable=False),
        sa.Column('actividad_gantt_id', sa.Integer(), nullable=False),
        sa.Column('edt', sa.String(length=50), nullable=False),
        sa.Column('fecha_asignacion', sa.DateTime(), nullable=True),
        sa.Column('recurso', sa.String(length=255), nullable=False),
        sa.Column('id_trabajador', sa.Integer(), nullable=False),
        sa.Column('porcentaje_asignacion', sa.Float(), nullable=True),
        sa.Column('fecha_creacion', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['actividad_gantt_id'], ['actividades_gantt.id'], ),
        sa.ForeignKeyConstraint(['id_trabajador'], ['trabajadores.id'], ),
        sa.ForeignKeyConstraint(['requerimiento_id'], ['requerimientos.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Crear índices
    op.create_index('idx_actividades_gantt_req_edt', 'actividades_gantt', ['requerimiento_id', 'edt'])
    op.create_index('idx_recurso_trabajador_unique', 'recursos_trabajador', ['actividad_gantt_id', 'id_trabajador'])

def downgrade():
    op.drop_index('idx_recurso_trabajador_unique', table_name='recursos_trabajador')
    op.drop_index('idx_actividades_gantt_req_edt', table_name='actividades_gantt')
    op.drop_table('recursos_trabajador')
    op.drop_table('actividades_gantt')
