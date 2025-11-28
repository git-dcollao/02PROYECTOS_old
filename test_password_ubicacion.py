#!/usr/bin/env python3
"""
Script para probar la función crear_avances_actividad con password y ubicación
"""
import sys
sys.path.insert(0, '/app')

from app import create_app
from app.models import *
from app.controllers.proyectos_controller import crear_avances_actividad

app = create_app()

with app.app_context():
    print("🔧 PROBANDO FUNCIÓN CON PASSWORD Y UBICACIÓN")
    print("=" * 60)
    
    # 1. Simular usuario logueado con sector y recinto
    usuario_admin = Trabajador.query.filter_by(email='admin@sistema.local').first()
    if not usuario_admin:
        print("❌ Usuario admin no encontrado")
        exit(1)
    
    print(f"👤 Usuario simulado: {usuario_admin.email}")
    print(f"   Sector ID: {usuario_admin.sector_id}")
    print(f"   Recinto ID: {usuario_admin.recinto_id}")
    
    # Si el usuario no tiene sector/recinto asignado, asignar uno para la prueba
    if not usuario_admin.sector_id:
        primer_sector = Sector.query.first()
        if primer_sector:
            usuario_admin.sector_id = primer_sector.id
            print(f"   📝 Asignando sector_id={primer_sector.id} para la prueba")
    
    if not usuario_admin.recinto_id:
        primer_recinto = Recinto.query.first()
        if primer_recinto:
            usuario_admin.recinto_id = primer_recinto.id
            print(f"   📝 Asignando recinto_id={primer_recinto.id} para la prueba")
        db.session.commit()
    
    # 2. Crear un contexto de aplicación con usuario logueado simulado
    from unittest.mock import MagicMock
    
    # Simular current_user
    mock_current_user = MagicMock()
    mock_current_user.sector_id = usuario_admin.sector_id
    mock_current_user.recinto_id = usuario_admin.recinto_id
    mock_current_user.email = usuario_admin.email
    mock_current_user.id = usuario_admin.id
    
    print(f"\n🎭 Current_user simulado:")
    print(f"   Email: {mock_current_user.email}")
    print(f"   Sector ID: {mock_current_user.sector_id}")
    print(f"   Recinto ID: {mock_current_user.recinto_id}")
    
    # 3. Mockear flask_login.current_user
    import app.controllers.proyectos_controller as controller_module
    import flask_login
    
    # Guardar el current_user original
    original_current_user = getattr(flask_login, 'current_user', None)
    
    # Reemplazar temporalmente current_user
    flask_login.current_user = mock_current_user
    
    try:
        # 4. Crear un recurso de prueba que no exista
        recurso_prueba = "TEST_WORKER_001"
        
        # Verificar que no existe
        trabajador_existente = Trabajador.query.filter_by(nombre=recurso_prueba).first()
        if trabajador_existente:
            print(f"🗑️ Eliminando trabajador existente para prueba limpia...")
            # Eliminar avances relacionados
            avances = AvanceActividad.query.filter_by(trabajador_id=trabajador_existente.id).all()
            for avance in avances:
                db.session.delete(avance)
            db.session.delete(trabajador_existente)
            db.session.commit()
        
        # 5. Buscar una actividad para la prueba
        actividad = ActividadProyecto.query.first()
        if not actividad:
            print("❌ No hay actividades para probar")
            exit(1)
        
        print(f"\n🧪 Probando con recurso: '{recurso_prueba}'")
        print(f"   Actividad: {actividad.edt} - {actividad.nombre_tarea}")
        
        # 6. Ejecutar la función
        crear_avances_actividad(
            requerimiento_id=actividad.requerimiento_id,
            actividad_id=actividad.id,
            recursos_string=recurso_prueba,
            progreso_actual=0.0
        )
        
        # Commit para guardar cambios
        db.session.commit()
        
        # 7. Verificar que el trabajador se creó correctamente
        trabajador_creado = Trabajador.query.filter_by(nombre=recurso_prueba).first()
        
        if trabajador_creado:
            print(f"\n✅ ¡ÉXITO! Trabajador creado correctamente:")
            print(f"   Nombre: {trabajador_creado.nombre}")
            print(f"   Email: {trabajador_creado.email}")
            print(f"   RUT: {trabajador_creado.rut}")
            print(f"   Sector ID: {trabajador_creado.sector_id}")
            print(f"   Recinto ID: {trabajador_creado.recinto_id}")
            
            # Verificar password
            if trabajador_creado.password_hash:
                password_valido = trabajador_creado.verify_password("Maho2025")
                print(f"   Password 'Maho2025': {'✅ Válido' if password_valido else '❌ Inválido'}")
            else:
                print(f"   Password: ❌ No establecido")
            
            # Verificar que heredó la ubicación del usuario logueado
            herencia_correcta = (
                trabajador_creado.sector_id == mock_current_user.sector_id and
                trabajador_creado.recinto_id == mock_current_user.recinto_id
            )
            print(f"   Herencia ubicación: {'✅ Correcta' if herencia_correcta else '❌ Incorrecta'}")
            
            # Verificar avance creado
            avance = AvanceActividad.query.filter_by(
                trabajador_id=trabajador_creado.id,
                actividad_id=actividad.id
            ).first()
            print(f"   Avance creado: {'✅ Sí' if avance else '❌ No'}")
            
        else:
            print(f"\n❌ Error: Trabajador no fue creado")
    
    except Exception as e:
        print(f"\n❌ Error durante la prueba: {str(e)}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Restaurar current_user original
        if original_current_user:
            flask_login.current_user = original_current_user
        
    print(f"\n✅ Prueba completada")