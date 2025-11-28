#!/usr/bin/env python3
"""
Script de migración para preparar la aplicación para producción
- Actualiza roles existentes de ADMIN_AREA a CONTROL
- Elimina referencias a roles obsoletos
- Verifica la integridad de los datos
"""

import sys
import os

# Agregar el directorio raíz al path para importar la app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Trabajador, CustomRole, PagePermission, UserRole
from sqlalchemy import text

def migrate_roles():
    """Migrar roles existentes para producción"""
    app = create_app()
    
    with app.app_context():
        print("🚀 Iniciando migración de roles para producción...")
        
        try:
            # 1. Actualizar trabajadores con roles del sistema obsoletos
            print("\n1️⃣ Migrando trabajadores con roles del sistema...")
            
            # Buscar trabajadores que puedan tener referencias a roles obsoletos
            # Nota: Como cambiamos el enum, estos deberían fallar, pero verificamos
            trabajadores_con_rol = Trabajador.query.filter(Trabajador.rol.isnot(None)).all()
            
            for trabajador in trabajadores_con_rol:
                print(f"   📋 Verificando trabajador: {trabajador.email} - Rol: {trabajador.rol}")
                
                # Si el rol no es válido según el nuevo enum, convertir a rol personalizado
                if trabajador.rol and trabajador.rol.name not in ['SUPERADMIN', 'ADMIN', 'CONTROL', 'USUARIO']:
                    print(f"   ⚠️ Rol inválido detectado: {trabajador.rol}")
                    # Aquí harías la conversión si fuera necesario
            
            # 2. Actualizar roles personalizados
            print("\n2️⃣ Actualizando roles personalizados...")
            
            # Cambiar ADMIN_AREA a CONTROL en roles personalizados
            role_admin_area = CustomRole.query.filter_by(name='ADMIN_AREA').first()
            if role_admin_area:
                print(f"   🔄 Cambiando rol ADMIN_AREA a CONTROL...")
                role_admin_area.name = 'CONTROL'
                role_admin_area.description = 'Control de Proyectos con permisos de supervisión y control'
                db.session.add(role_admin_area)
            
            # Eliminar rol SOLICITANTE si existe
            role_solicitante = CustomRole.query.filter_by(name='SOLICITANTE').first()
            if role_solicitante:
                print(f"   🗑️ Eliminando rol SOLICITANTE...")
                # Primero, actualizar trabajadores que tengan este rol
                trabajadores_solicitante = Trabajador.query.filter_by(custom_role_id=role_solicitante.id).all()
                for trabajador in trabajadores_solicitante:
                    print(f"      📝 Cambiando {trabajador.email} de SOLICITANTE a ADMIN")
                    if not trabajador.set_custom_role_by_name('ADMIN'):
                        trabajador.rol = UserRole.ADMIN
                        trabajador.custom_role_id = None
                
                # Eliminar permisos del rol SOLICITANTE
                PagePermission.query.filter_by(custom_role_id=role_solicitante.id).delete()
                
                # Eliminar el rol
                db.session.delete(role_solicitante)
            
            # 3. Actualizar permisos de página que referencien roles obsoletos
            print("\n3️⃣ Actualizando permisos de página...")
            
            # Buscar permisos que referencien ADMIN_AREA
            permisos_admin_area = PagePermission.query.filter_by(role_name='ADMIN_AREA').all()
            for permiso in permisos_admin_area:
                print(f"   🔄 Cambiando permiso de ADMIN_AREA a CONTROL...")
                permiso.role_name = 'CONTROL'
                db.session.add(permiso)
            
            # Eliminar permisos que referencien SOLICITANTE
            permisos_solicitante = PagePermission.query.filter_by(role_name='SOLICITANTE').all()
            for permiso in permisos_solicitante:
                print(f"   🗑️ Eliminando permiso para SOLICITANTE...")
                db.session.delete(permiso)
            
            # 4. Verificar integridad de datos
            print("\n4️⃣ Verificando integridad de datos...")
            
            # Contar trabajadores por tipo de rol
            total_trabajadores = Trabajador.query.count()
            trabajadores_rol_sistema = Trabajador.query.filter(Trabajador.rol.isnot(None)).count()
            trabajadores_rol_custom = Trabajador.query.filter(Trabajador.custom_role_id.isnot(None)).count()
            trabajadores_sin_rol = Trabajador.query.filter(
                Trabajador.rol.is_(None), 
                Trabajador.custom_role_id.is_(None)
            ).count()
            
            print(f"   📊 Total trabajadores: {total_trabajadores}")
            print(f"   📊 Con rol del sistema: {trabajadores_rol_sistema}")
            print(f"   📊 Con rol personalizado: {trabajadores_rol_custom}")
            print(f"   📊 Sin rol: {trabajadores_sin_rol}")
            
            # Verificar roles personalizados activos
            roles_activos = CustomRole.query.filter_by(active=True).all()
            print(f"   📊 Roles personalizados activos: {len(roles_activos)}")
            for rol in roles_activos:
                count_usuarios = Trabajador.query.filter_by(custom_role_id=rol.id).count()
                print(f"      - {rol.name}: {count_usuarios} usuarios")
            
            # Confirmar cambios
            respuesta = input("\n¿Confirmar cambios? (s/n): ").lower().strip()
            if respuesta in ['s', 'si', 'sí', 'y', 'yes']:
                db.session.commit()
                print("✅ Migración completada exitosamente!")
                return True
            else:
                db.session.rollback()
                print("❌ Migración cancelada por el usuario")
                return False
                
        except Exception as e:
            print(f"\n❌ Error durante la migración: {e}")
            db.session.rollback()
            return False

def verificar_configuracion():
    """Verificar que la configuración esté correcta después de la migración"""
    app = create_app()
    
    with app.app_context():
        print("\n🔍 Verificando configuración post-migración...")
        
        # Verificar que todos los usuarios tengan rol válido
        usuarios_sin_rol_valido = []
        
        for trabajador in Trabajador.query.all():
            tiene_rol_valido = False
            
            # Verificar rol del sistema
            if trabajador.rol:
                if trabajador.rol in [UserRole.SUPERADMIN, UserRole.ADMIN, UserRole.CONTROL, UserRole.USUARIO]:
                    tiene_rol_valido = True
            
            # Verificar rol personalizado
            if trabajador.custom_role_id and trabajador.custom_role and trabajador.custom_role.active:
                tiene_rol_valido = True
            
            if not tiene_rol_valido:
                usuarios_sin_rol_valido.append(trabajador)
        
        if usuarios_sin_rol_valido:
            print(f"   ⚠️ Encontrados {len(usuarios_sin_rol_valido)} usuarios sin rol válido:")
            for user in usuarios_sin_rol_valido:
                print(f"      - {user.email}")
        else:
            print("   ✅ Todos los usuarios tienen roles válidos")
        
        # Verificar roles personalizados necesarios
        roles_necesarios = ['SUPERADMIN', 'ADMIN', 'CONTROL', 'USUARIO']
        roles_faltantes = []
        
        for rol_name in roles_necesarios:
            if rol_name == 'SUPERADMIN':
                continue  # Este es del sistema
            
            rol_existe = CustomRole.query.filter_by(name=rol_name, active=True).first()
            if not rol_existe:
                roles_faltantes.append(rol_name)
        
        if roles_faltantes:
            print(f"   ⚠️ Roles personalizados faltantes: {', '.join(roles_faltantes)}")
        else:
            print("   ✅ Todos los roles necesarios están presentes")

if __name__ == '__main__':
    print("=" * 60)
    print("MIGRACIÓN PARA PRODUCCIÓN - SISTEMA DE ROLES")
    print("=" * 60)
    
    if migrate_roles():
        verificar_configuracion()
        print("\n🎉 ¡Migración completada! La aplicación está lista para producción.")
    else:
        print("\n💥 Migración falló. Revise los errores y vuelva a intentar.")
    
    print("=" * 60)