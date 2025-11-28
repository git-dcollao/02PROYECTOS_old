from flask import Blueprint, render_template
from .models import Sector, Requerimiento, Grupo

handlers_bp = Blueprint('handlers', __name__)

@handlers_bp.route('/requerimientos')
def requerimientos():  # El nombre de la función coincide con la redirección
    requerimientos = Requerimiento.query.all()
    sectores = Sector.query.all()
    return render_template('requirements/requerimiento.html', requerimientos=requerimientos, sectores=sectores)

# Ruta para la página "Tipo de Recinto"
@handlers_bp.route('/recintos')
def recinto():
    return render_template('recinto.html')

# Ruta para la página "Tipo de Recinto"
@handlers_bp.route('/tiposrecintos')
def tiporecinto():
    return render_template('tiporecinto.html')

# Ruta para la página "Sector"
@handlers_bp.route('/sectores')
def sector():
    return render_template('sectores.html')

# Ruta para la página "Etapa"
@handlers_bp.route('/etapas')
def etapa():
    return render_template('etapas.html')

# Ruta para la página "Trabajador"
@handlers_bp.route('/trabajador')
def trabajador():
    return render_template('trabajador.html')

# Ruta para la página "EtapaN4"
@handlers_bp.route('/etapasN4')
def etapaN4():
    return render_template('etapaN4.html')

# Ruta para la página "EtapaN3"
@handlers_bp.route('/etapasN3')
def etapaN3():
    return render_template('etapaN3.html')

# Ruta para la página "EtapaN2"
@handlers_bp.route('/etapasN2')
def etapaN2():
    return render_template('etapaN2.html')

# Ruta para la página "EtapaN1"
@handlers_bp.route('/etapasN1')
def etapaN1():
    return render_template('etapaN1.html')

# Ruta para la página "Financiamiento"
@handlers_bp.route('/financiamiento')
def financiamiento():
    return render_template('financiamiento.html')

# Ruta para la página "Equipo"
@handlers_bp.route('/especialidad')
def especialidad():
    return render_template('especialidad.html')

# Ruta para la página "Equipo"
@handlers_bp.route('/equipo')
def equipo():
    return render_template('equipo.html')

# Ruta para la página "Grupo"
@handlers_bp.route('/grupo')
def grupo():
    return render_template('grupo.html')

# Ruta para la página "Tipologías del Proyecto"
@handlers_bp.route('/tipologia')
def tipologia():
    return render_template('tipologia.html')

# Ruta para la página "Fases del Proyecto"
@handlers_bp.route('/fase')
def fase():
    return render_template('fase.html')

# Ruta para la página "Tipo de Proyectos"
@handlers_bp.route('/tipoproyecto')
def tipo_de_proyecto():
    return render_template('tipoproyecto.html')

# Ruta para la página "Estado"
@handlers_bp.route('/estado', endpoint='ruta_estado')
def estado():
    return render_template('estado.html')

# Ruta para la página de inicio
@handlers_bp.route('/')
def inicio():
    return render_template('index.html')

# Ejemplo de nueva página
@handlers_bp.route('/mi-nueva-pagina')
def mi_nueva_pagina():
    return render_template('pages/ejemplo-nueva-pagina.html')
