from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.models import TipoRecinto, Recinto, Sector, Etapa, Trabajador, EtapaN4, EtapaN3, EtapaN2, EtapaN1, Financiamiento, Especialidad, Equipo, Tipologia, Fase, TipoProyecto, Estado, db

controllers_bp = Blueprint('controllers', __name__)

# ==================================================================================
# Rutas CRUD para Recintos
@controllers_bp.route('/recintos', endpoint='ruta_recintos')
def recintos():
    recintos = Recinto.query.all()
    tiposrecintos = TipoRecinto.query.all()
    return render_template('recintos.html', recintos=recintos, tiposrecintos=tiposrecintos)  # Cambiar a recintos.html

# Agregar endpoint para obtener etapas N1 en formato JSON
@controllers_bp.route('/get_recintos', methods=['GET'])
def get_recintos():
    recintos = Recinto.query.all()
    return jsonify([{'id': e.id, 'nombre': e.nombre} for e in recintos])

@controllers_bp.route('/add_recinto', methods=['POST'], endpoint='add_recinto')
def add_recinto():
    try:
        nombre = request.form['nombre']
        descripcion = request.form.get('descripcion', '')  # valor por defecto vacío
        id_tiporecinto = request.form.get('id_tiporecinto', '1')  # valor por defecto 1
        
        nuevo_recinto = Recinto(
            nombre=nombre,
            descripcion=descripcion,
            id_tiporecinto=id_tiporecinto  
        )
        db.session.add(nuevo_recinto)
        db.session.commit()
        flash('Recinto agregado exitosamente')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al agregar recinto: {e}')
    return redirect(url_for('controllers.ruta_recintos'))

@controllers_bp.route('/update_recinto/<int:id>', methods=['POST'], endpoint='update_recinto')
def update_recinto(id):
    try:
        recinto = Recinto.query.get_or_404(id)
        recinto.nombre = request.form['nombre']
        recinto.descripcion = request.form['descripcion']
        recinto.id_tiporecinto = request.form['id_tiporecinto']
        db.session.commit()
        flash('Recinto actualizado exitosamente')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar recinto: {e}')
    return redirect(url_for('controllers.ruta_recintos'))

@controllers_bp.route('/eliminar_recinto/<int:id>', methods=['POST'], endpoint='eliminar_recinto')
def eliminar_recinto(id):
    try:
        recinto = Recinto.query.get_or_404(id)
        db.session.delete(recinto)
        db.session.commit()
        flash('Recinto eliminado exitosamente')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar recinto: {e}')
    return redirect(url_for('controllers.ruta_recintos'))

# ==================================================================================
# Rutas CRUD para Tipo de Recintos
@controllers_bp.route('/tiposrecintos', endpoint='ruta_tiposrecintos')
def tiposrecintos():
    tiposrecintos = TipoRecinto.query.all()
    sectores = Sector.query.all()
    return render_template('tiposrecintos.html', tiposrecintos=tiposrecintos, sectores=sectores)  # Cambiar a recintos.html

# Agregar endpoint para obtener etapas N1 en formato JSON
@controllers_bp.route('/get_tiposrecintos', methods=['GET'])
def get_tiposrecintos():
    tiposrecintos = TipoRecinto.query.all()
    return jsonify([{'id': e.id, 'nombre': e.nombre} for e in tiposrecintos])

@controllers_bp.route('/add_tiporecinto', methods=['POST'], endpoint='add_tiporecinto')
def add_tiporecinto():
    try:
        nombre = request.form['name']
        descripcion = request.form.get('descripcion', '')  # valor por defecto vacío
        id_sector = request.form.get('id_sector', '1')  # valor por defecto 1
        
        nuevo_tiporecinto = TipoRecinto(
            nombre=nombre,
            descripcion=descripcion,
            id_sector=id_sector  
        )
        db.session.add(nuevo_tiporecinto)
        db.session.commit()
        flash('Tipo de Recinto agregado exitosamente')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al agregar recinto: {e}')
    return redirect(url_for('controllers.ruta_tiposrecintos'))

@controllers_bp.route('/update_tiporecinto/<int:id>', methods=['POST'], endpoint='update_tiporecinto')
def update_tiporecinto(id):
    try:
        tiporecinto = TipoRecinto.query.get_or_404(id)
        tiporecinto.nombre = request.form['name']
        tiporecinto.descripcion = request.form['descripcion']
        tiporecinto.id_sector = request.form['id_sector']
        db.session.commit()
        flash('Tipo de Recinto actualizado exitosamente')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar tipo de recinto: {e}')
    return redirect(url_for('controllers.ruta_tiposrecintos'))

@controllers_bp.route('/eliminar_tiporecinto/<int:id>', methods=['POST'], endpoint='eliminar_tiporecinto')
def eliminar_tiporecinto(id):
    try:
        recinto = TipoRecinto.query.get_or_404(id)
        db.session.delete(recinto)
        db.session.commit()
        flash('Tipo de Recinto eliminado exitosamente')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar tipo de recinto: {e}')
    return redirect(url_for('controllers.ruta_tiposrecintos'))

# ==================================================================================
# Rutas CRUD para Sector
@controllers_bp.route('/sectores', endpoint='ruta_sectores')
def sectores():
    sectores = Sector.query.all()
    return render_template('sector.html', sectores=sectores)

@controllers_bp.route('/add_sector', methods=['POST'], endpoint='add_sector')
def add_sector():
    try:
        nombre = request.form['nombre']
        nuevo_sector = Sector(nombre=nombre)
        db.session.add(nuevo_sector)
        db.session.commit()
        flash('Fase agregada exitosamente')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al agregar sector: {e}')
    return redirect(url_for('controllers.ruta_sectores'))

@controllers_bp.route('/update_sector/<int:id>', methods=['POST'], endpoint='update_sector')
def update_sector(id):
    try:
        sector = Sector.query.get_or_404(id)
        sector.nombre = request.form['nombre']
        db.session.commit()
        flash('Sector actualizada exitosamente')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar sector: {e}')
    return redirect(url_for('controllers.ruta_sectores'))

@controllers_bp.route('/eliminar_sector/<int:id>', methods=['POST'], endpoint='eliminar_sector')
def eliminar_sector(id):
    try:
        sector = Sector.query.get_or_404(id)
        db.session.delete(sector)
        db.session.commit()
        flash('Sector eliminada exitosamente')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar sector: {e}')
    return redirect(url_for('controllers.ruta_sectores'))

# ==================================================================================
# Rutas CRUD para Etapa(SNI)
@controllers_bp.route('/etapas', endpoint='ruta_etapas')
def etapas(): 
    etapas = Etapa.query.all()
    tipologias = Tipologia.query.all()  # Importante: obtener todas las tipologias
    return render_template('etapas.html', etapas=etapas, tipologias=tipologias)

@controllers_bp.route('/add_etapa', methods=['POST'], endpoint='add_etapa')
def add_etapa():
    try:
        nombre = request.form['name']
        id_tipologia = request.form.get('id_tipologia', '1')  # valor por defecto 1
        financiamiento = 'financiamiento' in request.form
        
        nuevo_etapa = Etapa(
            nombre=nombre,
            id_tipologia=id_tipologia,
            financiamiento=financiamiento
        )
        db.session.add(nuevo_etapa)
        db.session.commit()
        flash('Etapa  agregada exitosamente')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al agregar tipologia: {e}')
    return redirect(url_for('controllers.ruta_etapas'))

@controllers_bp.route('/update_etapa/<int:id>', methods=['POST'], endpoint='update_etapa')
def update_etapa(id):
    try:
        etapa = Etapa.query.get_or_404(id)
        etapa.nombre = request.form['name']
        etapa.id_tipologia = request.form['id_tipologia']
        etapa.financiamiento = 'financiamiento' in request.form
        db.session.commit()
        flash('Etapa  actualizada exitosamente')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar etapa: {e}')
    return redirect(url_for('controllers.ruta_etapas'))

@controllers_bp.route('/eliminar_etapa/<int:id>', methods=['POST'], endpoint='eliminar_etapa')
def eliminar_etapa(id):
    try: 
        etapa = Etapa.query.get_or_404(id)
        db.session.delete(etapa)
        db.session.commit()
        flash('Etapa  eliminado exitosamente')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar etapa : {e}')
    return redirect(url_for('controllers.ruta_etapas'))

# ==================================================================================
# Rutas CRUD para Trabajador 
@controllers_bp.route('/trabajadores', endpoint='ruta_trabajadores')
def trabajadores():
    trabajadores = Trabajador.query.all()
    return render_template('trabajadores.html', trabajadores=trabajadores)

@controllers_bp.route('/add_trabajador', methods=['POST'], endpoint='add_trabajador')
def add_trabajador():
    try:
        nombre = request.form['name']
        profesion = request.form.get('profesion', '')  # valor por defecto vacío
        nombrecorto = request.form.get('nombrecorto', '')  # valor por defecto vacío
        password = request.form.get('password', 'Maho#2024')  # valor por defecto vacío
        
        nuevo_trabajador = Trabajador(
            nombre=nombre,
            nombrecorto=nombrecorto,
            password=password
        )
        db.session.add(nuevo_trabajador)
        db.session.commit()
        flash('Trabajador agregado exitosamente')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al agregar trabajador: {e}')
    return redirect(url_for('controllers.ruta_trabajadores'))

@controllers_bp.route('/update_trabajador/<int:id>', methods=['POST'], endpoint='update_trabajador')
def update_trabajador(id):
    try:
        trabajador = Trabajador.query.get_or_404(id)
        trabajador.nombre = request.form['name']
        trabajador.profesion = request.form['profesion']
        trabajador.nombrecorto = request.form['nombrecorto']
        trabajador.password = request.form['password']
        db.session.commit()
        flash('Trabajador actualizado exitosamente')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar trabajador: {e}')
    return redirect(url_for('controllers.ruta_trabajadores'))

@controllers_bp.route('/eliminar_trabajador/<int:id>', methods=['POST'], endpoint='eliminar_trabajador')
def eliminar_trabajador(id):
    try:
        trabajador = Trabajador.query.get_or_404(id)
        db.session.delete(trabajador)
        db.session.commit()
        flash('trabajador eliminado exitosamente')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar trabajador: {e}')
    return redirect(url_for('controllers.ruta_trabajadores'))

# ==================================================================================
# Rutas CRUD para EtapaN4
@controllers_bp.route('/etapaN4', endpoint='ruta_etapaN4')
def etapasN4(): 
    etapasN4 = EtapaN4.query.all()
    etapasN3 = EtapaN3.query.all()  # Importante: obtener todas las etapas N3
    return render_template('etapasN4.html', etapasN4=etapasN4, etapasN3=etapasN3)

@controllers_bp.route('/add_etapaN4', methods=['POST'], endpoint='add_etapaN4')
def add_etapaN4():
    try:
        nombre = request.form['name']
        descripcion = request.form.get('descripcion', '')  # valor por defecto vacío
        id_etapaN3 = request.form.get('id_etapaN3', '1')  # valor por defecto 1
        
        nuevo_etapaN4 = EtapaN4(
            nombre=nombre,
            descripcion=descripcion,
            id_etapaN3=id_etapaN3  
        )
        db.session.add(nuevo_etapaN4)
        db.session.commit()
        flash('Etapa N4 agregada exitosamente')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al agregar etapa N3: {e}')
    return redirect(url_for('controllers.ruta_etapaN4'))

@controllers_bp.route('/update_etapaN4/<int:id>', methods=['POST'], endpoint='update_etapaN4')
def update_etapaN4(id):
    try:
        etapaN4 = EtapaN4.query.get_or_404(id)
        etapaN4.nombre = request.form['name']
        etapaN4.descripcion = request.form['descripcion']
        etapaN4.id_etapaN3 = request.form['id_etapaN3']
        db.session.commit()
        flash('Etapa N4 actualizada exitosamente')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar etapaN4: {e}')
    return redirect(url_for('controllers.ruta_etapaN4'))

@controllers_bp.route('/eliminar_etapaN4/<int:id>', methods=['POST'], endpoint='eliminar_etapaN4')
def eliminar_etapaN4(id):
    try: 
        etapaN4 = EtapaN4.query.get_or_404(id)
        db.session.delete(etapaN4)
        db.session.commit()
        flash('Etapa N4 eliminado exitosamente')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar etapa N4: {e}')
    return redirect(url_for('controllers.ruta_etapaN4'))

# ==================================================================================
# Rutas CRUD para EtapaN3 
@controllers_bp.route('/etapaN3', endpoint='ruta_etapaN3')
def etapasN3(): 
    etapasN3 = EtapaN3.query.all()
    etapasN2 = EtapaN2.query.all()  # Importante: obtener todas las etapas N1
    return render_template('etapasN3.html', etapasN3=etapasN3, etapasN2=etapasN2)

@controllers_bp.route('/add_etapaN3', methods=['POST'], endpoint='add_etapaN3')
def add_etapaN3():
    try:
        nombre = request.form['name']
        descripcion = request.form.get('descripcion', '')  # valor por defecto vacío
        id_etapaN2 = request.form.get('id_etapaN2', '1')  # valor por defecto 1
        
        nuevo_etapaN3 = EtapaN3(
            nombre=nombre,
            descripcion=descripcion,
            id_etapaN2=id_etapaN2  
        )
        db.session.add(nuevo_etapaN3)
        db.session.commit()
        flash('Etapa N3 agregada exitosamente')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al agregar etapa N3: {e}')
    return redirect(url_for('controllers.ruta_etapaN3'))

@controllers_bp.route('/update_etapaN3/<int:id>', methods=['POST'], endpoint='update_etapaN3')
def update_etapaN3(id):
    try:
        etapaN3 = EtapaN3.query.get_or_404(id)
        etapaN3.nombre = request.form['name']
        etapaN3.descripcion = request.form['descripcion']
        etapaN3.id_etapaN2 = request.form['id_etapaN2']
        db.session.commit()
        flash('Etapa N3 actualizada exitosamente')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar etapaN3: {e}')
    return redirect(url_for('controllers.ruta_etapaN3'))

@controllers_bp.route('/eliminar_etapaN3/<int:id>', methods=['POST'], endpoint='eliminar_etapaN3')
def eliminar_etapaN3(id):
    try:
        etapaN3 = EtapaN3.query.get_or_404(id)
        db.session.delete(etapaN3)
        db.session.commit()
        flash('Etapa N3 eliminado exitosamente')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar etapa N3: {e}')
    return redirect(url_for('controllers.ruta_etapaN3'))

# ==================================================================================
# Rutas CRUD para EtapaN2 
@controllers_bp.route('/etapaN2', endpoint='ruta_etapaN2')
def etapasN2(): 
    etapasN2 = EtapaN2.query.all()
    etapasN1 = EtapaN1.query.all()  # Importante: obtener todas las etapas N1
    return render_template('etapasN2.html', etapasN2=etapasN2, etapasN1=etapasN1)

# Agregar endpoint para obtener etapas N1 en formato JSON
@controllers_bp.route('/get_etapasN2', methods=['GET'])
def get_etapasN2():
    etapasN2 = EtapaN2.query.all()
    return jsonify([{'id': e.id, 'nombre': e.nombre} for e in etapasN2])

@controllers_bp.route('/add_etapaN2', methods=['POST'], endpoint='add_etapaN2')
def add_etapaN2():
    try:
        nombre = request.form['name']
        descripcion = request.form.get('descripcion', '')  # valor por defecto vacío
        id_etapaN1 = request.form.get('id_etapaN1', '1')  # valor por defecto 1
        
        nuevo_etapaN2 = EtapaN2(
            nombre=nombre,
            descripcion=descripcion,
            id_etapaN1=id_etapaN1  
        )
        db.session.add(nuevo_etapaN2)
        db.session.commit()
        flash('Etapa N2 agregada exitosamente')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al agregar etapa N2: {e}')
    return redirect(url_for('controllers.ruta_etapaN2'))

@controllers_bp.route('/update_etapaN2/<int:id>', methods=['POST'], endpoint='update_etapaN2')
def update_etapaN2(id):
    try:
        etapaN2 = EtapaN2.query.get_or_404(id)
        etapaN2.nombre = request.form['name']
        etapaN2.descripcion = request.form['descripcion']
        etapaN2.id_etapaN1 = request.form['id_etapaN1']
        db.session.commit()
        flash('Etapa N2 actualizada exitosamente')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar etapaN2: {e}')
    return redirect(url_for('controllers.ruta_etapaN2'))

@controllers_bp.route('/eliminar_etapaN2/<int:id>', methods=['POST'], endpoint='eliminar_etapaN2')
def eliminar_etapaN2(id):
    try:
        etapaN2 = EtapaN2.query.get_or_404(id)
        db.session.delete(etapaN2)
        db.session.commit()
        flash('Etapa N2 eliminado exitosamente')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar etapa N2: {e}')
    return redirect(url_for('controllers.ruta_etapaN2'))

# ==================================================================================
# Rutas CRUD para EtapaN1 
@controllers_bp.route('/etapaN1', endpoint='ruta_etapaN1')
def etapasN1(): 
    etapasN1 = EtapaN1.query.all()
    return render_template('etapasN1.html', etapasN1=etapasN1)

# Agregar endpoint para obtener etapas N1 en formato JSON
@controllers_bp.route('/get_etapasN1', methods=['GET'])
def get_etapasN1():
    etapasN1 = EtapaN1.query.all()
    return jsonify([{'id': e.id, 'nombre': e.nombre} for e in etapasN1])

@controllers_bp.route('/add_etapaN1', methods=['POST'], endpoint='add_etapaN1')
def add_etapaN1():
    try:
        nombre = request.form['name']
        descripcion = request.form.get('descripcion', '')  # valor por defecto vacío
        
        nuevo_etapaN1 = EtapaN1(
            nombre=nombre,
            descripcion=descripcion
        )
        db.session.add(nuevo_etapaN1)
        db.session.commit()
        flash('Etapa N1 agregado exitosamente')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al agregar etapa N1: {e}')
    return redirect(url_for('controllers.ruta_etapaN1'))

@controllers_bp.route('/update_etapaN1/<int:id>', methods=['POST'], endpoint='update_etapaN1')
def update_etapaN1(id):
    try:
        etapaN1 = EtapaN1.query.get_or_404(id)
        etapaN1.nombre = request.form['name']
        etapaN1.descripcion = request.form['descripcion']
        db.session.commit()
        flash('Etapa N1 actualizado exitosamente')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar etapaN1: {e}')
    return redirect(url_for('controllers.ruta_etapaN1'))

@controllers_bp.route('/eliminar_etapaN1/<int:id>', methods=['POST'], endpoint='eliminar_etapaN1')
def eliminar_etapaN1(id):
    try:
        etapaN1 = EtapaN1.query.get_or_404(id)
        db.session.delete(etapaN1)
        db.session.commit()
        flash('Etapa N1 eliminado exitosamente')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar etapa N1: {e}')
    return redirect(url_for('controllers.ruta_etapaN1'))

# ==================================================================================
# Rutas CRUD para Financiamiento 
@controllers_bp.route('/financiamientos', endpoint='ruta_financiamientos')
def financiamientos():
    financiamientos = Financiamiento.query.all()
    return render_template('financiamientos.html', financiamientos=financiamientos)

@controllers_bp.route('/add_financiamiento', methods=['POST'], endpoint='add_financiamiento')
def add_financiamiento():
    try:
        nombre = request.form['name']
        descripcion = request.form.get('descripcion', '')  # valor por defecto vacío
        
        nuevo_financiamiento = Financiamiento(
            nombre=nombre,
            descripcion=descripcion
        )
        db.session.add(nuevo_financiamiento)
        db.session.commit()
        flash('Financiamiento agregado exitosamente')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al agregar financiamiento: {e}')
    return redirect(url_for('controllers.ruta_financiamientos'))

@controllers_bp.route('/update_financiamiento/<int:id>', methods=['POST'], endpoint='update_financiamiento')
def update_financiamiento(id):
    try:
        financiamiento = Financiamiento.query.get_or_404(id)
        financiamiento.nombre = request.form['name']
        financiamiento.descripcion = request.form['descripcion']
        db.session.commit()
        flash('Financiamiento actualizado exitosamente')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar financiamiento: {e}')
    return redirect(url_for('controllers.ruta_financiamientos'))

@controllers_bp.route('/eliminar_financiamiento/<int:id>', methods=['POST'], endpoint='eliminar_financiamiento')
def eliminar_financiamiento(id):
    try:
        financiamiento = Financiamiento.query.get_or_404(id)
        db.session.delete(financiamiento)
        db.session.commit()
        flash('Financiamiento eliminado exitosamente')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar financiamiento: {e}')
    return redirect(url_for('controllers.ruta_financiamientos'))

# ==================================================================================
# Rutas CRUD para Especialidad
@controllers_bp.route('/especialidades', endpoint='ruta_especialidades')
def especialidades():
    especialidades = Especialidad.query.all()
    return render_template('especialidad.html', especialidades=especialidades)

@controllers_bp.route('/add_especialidad', methods=['POST'], endpoint='add_especialidad')
def add_especialidad():
    try:
        nombre = request.form['name']
        nuevo_especialidad = Especialidad(nombre=nombre)
        db.session.add(nuevo_especialidad)
        db.session.commit()
        flash('Especialidad agregada exitosamente')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al agregar especialidad: {e}')
    return redirect(url_for('controllers.ruta_especialidades'))

@controllers_bp.route('/update_especialidad/<int:id>', methods=['POST'], endpoint='update_especialidad')
def update_especialidad(id):
    try:
        especialidad = Especialidad.query.get_or_404(id)
        especialidad.nombre = request.form['name']
        db.session.commit()
        flash('Especialidad actualizada exitosamente')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar especialidad: {e}')
    return redirect(url_for('controllers.ruta_especialidades'))

@controllers_bp.route('/eliminar_especialidad/<int:id>', methods=['POST'], endpoint='eliminar_especialidad')
def eliminar_especialidad(id):
    try:
        especialidad = Especialidad.query.get_or_404(id)
        db.session.delete(especialidad)
        db.session.commit()
        flash('Especialidad eliminada exitosamente')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar especialidad: {e}')
    return redirect(url_for('controllers.ruta_especialidades'))

# ==================================================================================
# Rutas CRUD para Equipos
@controllers_bp.route('/equipos', endpoint='ruta_equipos')
def equipos():
    equipos = Equipo.query.all()
    return render_template('equipo.html', equipos=equipos)

@controllers_bp.route('/add_equipo', methods=['POST'], endpoint='add_equipo')
def add_equipo():
    try:
        nombre = request.form['name']
        nuevo_equipo = Equipo(nombre=nombre)
        db.session.add(nuevo_equipo)
        db.session.commit()
        flash('Equipo agregado exitosamente')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al agregar equipo: {e}')
    return redirect(url_for('controllers.ruta_equipos'))

@controllers_bp.route('/update_equipo/<int:id>', methods=['POST'], endpoint='update_equipo')
def update_equipo(id):
    try:
        equipo = Equipo.query.get_or_404(id)
        equipo.nombre = request.form['name']
        db.session.commit()
        flash('Equipo actualizado exitosamente')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar equipo: {e}')
    return redirect(url_for('controllers.ruta_equipos'))

@controllers_bp.route('/eliminar_equipo/<int:id>', methods=['POST'], endpoint='eliminar_equipo')
def eliminar_equipo(id):
    try:
        equipo = Equipo.query.get_or_404(id)
        db.session.delete(equipo)
        db.session.commit()
        flash('Equipo eliminado exitosamente')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar equipo: {e}')
    return redirect(url_for('controllers.ruta_equipos'))

# ==================================================================================
# Rutas CRUD para Tipologías
@controllers_bp.route('/tipologias', endpoint='ruta_tipologias')
def tipologias():
    tipologias = Tipologia.query.all()
    fases = Fase.query.all()  # Importante: obtener todas las fases
    return render_template('tipologias.html', tipologias=tipologias, fases=fases)

# Agregar endpoint para obtener fases en formato JSON
@controllers_bp.route('/get_tipologias', methods=['GET'])
def get_tipologias():
    tipologias = Tipologia.query.all()
    return jsonify([{'id': e.id, 'nombre': e.nombre} for e in tipologias])

@controllers_bp.route('/add_tipologia', methods=['POST'], endpoint='add_tipologia')
def add_tipologia():
    try:
        nombre = request.form['nombre']
        nombrecorto = request.form.get('nombrecorto', '')  # valor por defecto vacío
        id_fase = request.form.get('id_fase', '1')  # valor por defecto 1
        
        nueva_tipologia = Tipologia(
            nombre=nombre,
            nombrecorto=nombrecorto,
            id_fase=id_fase  
        )
        db.session.add(nueva_tipologia)
        db.session.commit()
        flash('Tipologia agregada exitosamente')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al agregar tipologia: {e}')
    return redirect(url_for('controllers.ruta_tipologias'))

@controllers_bp.route('/update_tipologia/<int:id>', methods=['POST'], endpoint='update_tipologia')
def update_tipologia(id):
    try:
        tipologia = Tipologia.query.get_or_404(id)
        tipologia.nombre = request.form['nombre']
        tipologia.nombrecorto = request.form['nombrecorto']
        tipologia.id_fase = request.form['id_fase']
        db.session.commit()
        flash('Tipologia actualizada exitosamente')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar tipologia: {e}')
    return redirect(url_for('controllers.ruta_tipologias'))

@controllers_bp.route('/eliminar_tipologia/<int:id>', methods=['POST'], endpoint='eliminar_tipologia')
def eliminar_tipologia(id):
    try:
        tipologia = Tipologia.query.get_or_404(id)
        db.session.delete(tipologia)
        db.session.commit()
        flash('Tipologia eliminado exitosamente')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar tipologia: {e}')
    return redirect(url_for('controllers.ruta_tipologias'))

# ==================================================================================
# Rutas CRUD para Fases
@controllers_bp.route('/fases', endpoint='ruta_fases')
def fases():
    fases = Fase.query.all()
    return render_template('fase.html', fases=fases)

@controllers_bp.route('/add_fase', methods=['POST'], endpoint='add_fase')
def add_fase():
    try:
        nombre = request.form['name']
        nueva_fase = Fase(nombre=nombre)
        db.session.add(nueva_fase)
        db.session.commit()
        flash('Fase agregada exitosamente')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al agregar fase: {e}')
    return redirect(url_for('controllers.ruta_fases'))

@controllers_bp.route('/update_fase/<int:id>', methods=['POST'], endpoint='update_fase')
def update_fase(id):
    try:
        fase = Fase.query.get_or_404(id)
        fase.nombre = request.form['name']
        db.session.commit()
        flash('Fase actualizada exitosamente')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar fase: {e}')
    return redirect(url_for('controllers.ruta_fases'))

@controllers_bp.route('/eliminar_fase/<int:id>', methods=['POST'], endpoint='eliminar_fase')
def eliminar_fase(id):
    try:
        fase = Fase.query.get_or_404(id)
        db.session.delete(fase)
        db.session.commit()
        flash('Fase eliminada exitosamente')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar fase: {e}')
    return redirect(url_for('controllers.ruta_fases'))

# ==================================================================================
# Rutas CRUD para Tipo de Proyecto 
@controllers_bp.route('/tipoproyectos', endpoint='ruta_tipoproyectos')
def tipoproyectos():
    tipoproyectos = TipoProyecto.query.all()
    return render_template('tipoproyectos.html', tipoproyectos=tipoproyectos)

@controllers_bp.route('/add_tipoproyecto', methods=['POST'], endpoint='add_tipoproyecto')
def add_tipoproyecto():
    try:
        nombre = request.form['name']
        nombrecorto = request.form.get('namecorto', '')  # valor por defecto vacío
        descripcion = request.form.get('descripcion', '')  # valor por defecto vacío
        
        nuevo_tipoproyecto = TipoProyecto(
            nombre=nombre,
            nombrecorto=nombrecorto,
            descripcion=descripcion
        )
        db.session.add(nuevo_tipoproyecto)
        db.session.commit()
        flash('Tipo de Proyecto agregado exitosamente')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al agregar tipo de proyecto: {e}')
    return redirect(url_for('controllers.ruta_tipoproyectos'))

@controllers_bp.route('/update_tipoproyecto/<int:id>', methods=['POST'], endpoint='update_tipoproyecto')
def update_tipoproyecto(id):
    try:
        tipoproyecto = TipoProyecto.query.get_or_404(id)
        tipoproyecto.nombre = request.form['name']
        tipoproyecto.nombrecorto = request.form['namecorto']
        tipoproyecto.descripcion = request.form['descripcion']
        db.session.commit()
        flash('tipo de Proyecto actualizado exitosamente')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar tipo de proyecto: {e}')
    return redirect(url_for('controllers.ruta_tipologias'))

@controllers_bp.route('/eliminar_tipoproyecto/<int:id>', methods=['POST'], endpoint='eliminar_tipoproyecto')
def eliminar_tipoproyecto(id):
    try:
        tipoproyecto = TipoProyecto.query.get_or_404(id)
        db.session.delete(tipoproyecto)
        db.session.commit()
        flash('Tipo de Proyecto eliminado exitosamente')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar tipo de proyecto: {e}')
    return redirect(url_for('controllers.ruta_tipoproyectos'))

# ==================================================================================
# Rutas CRUD para Estados
@controllers_bp.route('/estados', endpoint='ruta_estados')
def estados():
    estados = Estado.query.all()
    return render_template('estados.html', estados=estados)

@controllers_bp.route('/add_estado', methods=['POST'], endpoint='add_estado')
def add_estado():
    try:
        nombre = request.form['name']
        nuevo_estado = Estado(nombre=nombre)
        db.session.add(nuevo_estado)
        db.session.commit()
        flash('Estado agregado exitosamente')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al agregar estado: {e}')
    return redirect(url_for('controllers.ruta_estados'))

@controllers_bp.route('/update_estado/<int:id>', methods=['POST'], endpoint='update_estado')
def update_estado(id):
    try:
        estado = Estado.query.get_or_404(id)
        estado.nombre = request.form['name']
        db.session.commit()
        flash('Estado actualizado exitosamente')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar estado: {e}')
    return redirect(url_for('controllers.ruta_estados'))

@controllers_bp.route('/eliminar_estado/<int:id>', methods=['POST'], endpoint='eliminar_estado')
def eliminar_estado(id):
    try:
        estado = Estado.query.get_or_404(id)
        db.session.delete(estado)
        db.session.commit()
        flash('Estado eliminado exitosamente')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar estado: {e}')
    return redirect(url_for('controllers.ruta_estados'))

# ==================================================================================
# Ruta para la página "Acerca de mí"
@controllers_bp.route('/acerca-de-mi', endpoint='ruta_acerca_de_mi')
def about_me():
    estados = Estado.query.all()
    return render_template('about_me.html', estados=estados)

@controllers_bp.route('/add_aboutme', methods=['POST'], endpoint='add_aboutme')
def add_aboutme():
    try:
        nombre = request.form['name']
        nuevo_estado = Estado(nombre=nombre)
        db.session.add(nuevo_estado)
        db.session.commit()
        flash('Estado agregado exitosamente')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al agregar estado: {e}')
    return redirect(url_for('controllers.ruta_acerca_de_mi'))

@controllers_bp.route('/update_aboutme/<int:id>', methods=['POST'], endpoint='update_aboutme')
def update_aboutme(id):
    try:
        estado = Estado.query.get_or_404(id)
        estado.nombre = request.form['name']
        db.session.commit()
        flash('Estado actualizado exitosamente')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar estado: {e}')
    return redirect(url_for('controllers.ruta_acerca_de_mi'))

@controllers_bp.route('/eliminar_aboutme/<int:id>', methods=['POST'], endpoint='eliminar_aboutme')
def eliminar_aboutme(id):
    try:
        estado = Estado.query.get_or_404(id)
        db.session.delete(estado)
        db.session.commit()
        flash('Estado eliminado exitosamente')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar estado: {e}')
    return redirect(url_for('controllers.ruta_acerca_de_mi'))

# ==================================================================================
# Ruta para la página "Contacto"
@controllers_bp.route('/contacto', endpoint='ruta_contacto')
def contact():
    estados = Estado.query.all()
    return render_template('contact.html', estados=estados)

# ==================================================================================
# Ruta para la página de bienvenida
@controllers_bp.route('/', endpoint='ruta_inicio')
def ruta_inicio():
    return render_template('index.html')
# ==================================================================================
