from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import Estado, db

controllers_bp = Blueprint('controllers', __name__)

# ==================================================================================
# Ruta para la página de bienvenida
@controllers_bp.route('/', endpoint='ruta_inicio')
def ruta_inicio():
    return render_template('index.html')

# ==================================================================================
# Ruta para la página "Acerca de mí"
@controllers_bp.route('/acerca-de-mi', endpoint='ruta_acerca_de_mi')
def about_me():
    estados = Estado.query.all()
    return render_template('about_me.html', estados=estados)

@controllers_bp.route('/add_aboutme', methods=['POST'])
def add():
    nombre = request.form['name']
    nuevo_estado = Estado(nombre=nombre)
    db.session.add(nuevo_estado)
    db.session.commit()
    flash('Estado agregado exitosamente')
    return redirect(url_for('controllers.ruta_acerca_de_mi'))

@controllers_bp.route('/update_aboutme/<int:id>', methods=['POST'])
def update(id):
    estado = Estado.query.get_or_404(id)
    estado.nombre = request.form['name']
    db.session.commit()
    flash('Estado actualizado exitosamente')
    return redirect(url_for('controllers.ruta_acerca_de_mi'))

@controllers_bp.route('/eliminar_aboutme/<int:id>', methods=['POST'])
def eliminar(id):
    estado = Estado.query.get_or_404(id)
    db.session.delete(estado)
    db.session.commit()
    flash('Estado eliminado exitosamente')
    return redirect(url_for('controllers.ruta_acerca_de_mi'))

# ==================================================================================
# Rutas CRUD para Estados
@controllers_bp.route('/estados', endpoint='ruta_esatdos')
def estados():
    estados = Estado.query.all()
    return render_template('estados.html', estados=estados)

@controllers_bp.route('/add', methods=['POST'])
def add():
    nombre = request.form['name']
    nuevo_estado = Estado(nombre=nombre)
    db.session.add(nuevo_estado)
    db.session.commit()
    flash('Estado agregado exitosamente')
    return redirect(url_for('controllers.ruta_estado'))

@controllers_bp.route('/update/<int:id>', methods=['POST'])
def update(id):
    estado = Estado.query.get_or_404(id)
    estado.nombre = request.form['name']
    db.session.commit()
    flash('Estado actualizado exitosamente')
    return redirect(url_for('controllers.ruta_estado'))

@controllers_bp.route('/eliminar/<int:id>', methods=['POST'])
def eliminar(id):
    estado = Estado.query.get_or_404(id)
    db.session.delete(estado)
    db.session.commit()
    flash('Estado eliminado exitosamente')
    return redirect(url_for('controllers.ruta_estado'))

# ==================================================================================
# Ruta para la página "Contacto"
@controllers_bp.route('/contacto', endpoint='ruta_contacto')
def contact():
    estados = Estado.query.all()
    return render_template('contact.html', estados=estados)