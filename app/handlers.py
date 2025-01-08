from flask import Blueprint, render_template, jsonify

handlers_bp = Blueprint('handlers', __name__)

# Ruta para la página "Ingreso de Requerimientos"
@handlers_bp.route('/requerimientos')
def requerimiento():
    return render_template('requerimiento.html')

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

# # Ruta para la página "Acerca de mí"
# @handlers_bp.route('/acerca-de-mi', endpoint='ruta_acerca_de_mi')
# def acerca_de_mi():
#     return render_template('about_me.html')

# # Ruta para la página de proyectos
# @handlers_bp.route('/proyectos')
# def proyectos():
#     return render_template('pages/proyectos.html')

# # Ruta para la página de portafolio
# @handlers_bp.route('/portafolio/<nombre>')
# def portafolio(nombre):
#     return render_template('pages/portafolio.html', nombre=nombre)

# Ruta para la página de contacto
# @handlers_bp.route('/contacto')
# def contacto():
#     return render_template('pages/contacto.html')

# Ruta para la página de inicio
@handlers_bp.route('/')
def inicio():
    return render_template('index.html')
