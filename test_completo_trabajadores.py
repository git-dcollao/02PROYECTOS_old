#!/usr/bin/env python3
"""
Script para probar la función completa con custom_role_id y nombrecorto
"""
import sys
sys.path.insert(0, '/app')

from app import create_app
from app.models import *
from app.controllers.proyectos_controller import crear_avances_actividad

app = create_app()

with app.app_context():
    print("🔧 PROBANDO FUNCIÓN COMPLETA: PASSWORD + UBICACIÓN + ROL + NOMBRECORTO")
    print("=" * 70)
    
    # 1. Simular usuario logueado con sector y recinto
    usuario_admin = Trabajador.query.filter_by(email='admin@sistema.local').first()
    if not usuario_admin:
        print("❌ Usuario admin no encontrado")
        exit(1)
    
    print(f"👤 Usuario simulado: {usuario_admin.email}")
    print(f"   Sector ID: {usuario_admin.sector_id}")
    print(f"   Recinto ID: {usuario_admin.recinto_id}")
    
    # 2. Verificar que existe el rol con ID 3 (Usuario)
    rol_usuario = CustomRole.query.get(3)
    if rol_usuario:
        print(f"✅ Rol ID 3 encontrado: {rol_usuario.name}")
    else:
        print(f"⚠️ Rol ID 3 no encontrado - se asignará de todas formas")
    
    # 3. Simular current_user
    from unittest.mock import MagicMock
    import flask_login
    
    mock_current_user = MagicMock()
    mock_current_user.sector_id = usuario_admin.sector_id
    mock_current_user.recinto_id = usuario_admin.recinto_id
    mock_current_user.email = usuario_admin.email
    mock_current_user.id = usuario_admin.id
    
    # Reemplazar temporalmente current_user
    original_current_user = getattr(flask_login, 'current_user', None)
    flask_login.current_user = mock_current_user
    
    try:
        # 4. Crear un recurso de prueba que no exista
        recurso_prueba = "ARQTEST"
        
        # Verificar que no existe por nombrecorto
        trabajador_existente = Trabajador.query.filter_by(nombrecorto=recurso_prueba).first()
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
        trabajador_creado = Trabajador.query.filter_by(nombrecorto=recurso_prueba).first()
        
        if trabajador_creado:
            print(f"\n✅ ¡ÉXITO COMPLETO! Trabajador creado correctamente:")
            print(f"   Nombre (temporal): {trabajador_creado.nombre}")
            print(f"   Nombre corto (recurso): {trabajador_creado.nombrecorto}")
            print(f"   Email: {trabajador_creado.email}")
            print(f"   RUT: {trabajador_creado.rut}")
            print(f"   Custom Role ID: {trabajador_creado.custom_role_id}")
            print(f"   Sector ID: {trabajador_creado.sector_id}")
            print(f"   Recinto ID: {trabajador_creado.recinto_id}")
            
            # Verificar password
            if trabajador_creado.password_hash:
                password_valido = trabajador_creado.verify_password("Maho2025")
                print(f"   Password 'Maho2025': {'✅ Válido' if password_valido else '❌ Inválido'}")
            else:
                print(f"   Password: ❌ No establecido")
            
            # Verificar todos los campos requeridos
            validaciones = {
                'Custom Role ID = 3': trabajador_creado.custom_role_id == 3,
                'Nombre corto correcto': trabajador_creado.nombrecorto == recurso_prueba,
                'Nombre temporal generado': trabajador_creado.nombre == f"Usuario {recurso_prueba}",
                'Herencia sector': trabajador_creado.sector_id == mock_current_user.sector_id,
                'Herencia recinto': trabajador_creado.recinto_id == mock_current_user.recinto_id,
                'Password establecido': trabajador_creado.password_hash is not None
            }
            
            print(f"\n📋 VALIDACIONES:")
            for validacion, resultado in validaciones.items():
                print(f"   {validacion}: {'✅ Correcto' if resultado else '❌ Error'}")
            
            # Verificar avance creado
            avance = AvanceActividad.query.filter_by(
                trabajador_id=trabajador_creado.id,
                actividad_id=actividad.id
            ).first()
            print(f"   Avance creado: {'✅ Sí' if avance else '❌ No'}")
            
            # Mostrar información del rol
            if trabajador_creado.custom_role_id:
                rol = CustomRole.query.get(trabajador_creado.custom_role_id)
                if rol:
                    print(f"   Rol asignado: {rol.name} (ID: {rol.id})")
                else:
                    print(f"   Rol: ID {trabajador_creado.custom_role_id} (no encontrado)")
            
            # Resumen final
            todas_validaciones_ok = all(validaciones.values())
            print(f"\n🎯 RESULTADO FINAL: {'✅ TODO CORRECTO' if todas_validaciones_ok and avance else '❌ ALGUNOS ERRORES'}")
            
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