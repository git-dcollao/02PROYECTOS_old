#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import create_app, db
from app.models import Trabajador, AdministradorRecinto, Recinto, CustomRole

def fix_admin_permissions():
    app = create_app()
    with app.app_context():
        # 1. Verificar y corregir el rol del administrador
        admin_user = Trabajador.query.filter_by(email='administrador@sistema.local').first()
        if admin_user:
            print(f'Usuario: {admin_user.nombre}')
            print(f'Rol actual: {admin_user.rol}')
            print(f'Custom role ID: {admin_user.custom_role_id}')
            
            # Si no tiene rol, asignar ADMINISTRADOR
            if not admin_user.rol:
                # Buscar el rol ADMINISTRADOR en custom_roles
                admin_role = CustomRole.query.filter_by(name='ADMINISTRADOR', active=True).first()
                if admin_role:
                    admin_user.custom_role_id = admin_role.id
                    admin_user.rol = 'ADMINISTRADOR'
                    db.session.commit()
                    print(f'✅ Rol actualizado a: ADMINISTRADOR (ID: {admin_role.id})')
                else:
                    print('❌ Rol ADMINISTRADOR no encontrado en custom_roles')
            
        # 2. Mostrar todos los recintos disponibles
        print('\n--- Recintos disponibles ---')
        recintos = Recinto.query.filter_by(activo=True).all()
        for r in recintos:
            print(f'ID: {r.id}, Nombre: {r.nombre}')
        
        # 3. Asignar todos los recintos al administrador (para pruebas)
        if admin_user and recintos:
            print(f'\n--- Asignando recintos al administrador ---')
            for recinto in recintos:
                # Verificar si ya tiene la asignación
                asignacion_existente = AdministradorRecinto.query.filter_by(
                    administrador_id=admin_user.id,
                    recinto_id=recinto.id
                ).first()
                
                if not asignacion_existente:
                    nueva_asignacion = AdministradorRecinto(
                        administrador_id=admin_user.id,
                        recinto_id=recinto.id,
                        activo=True
                    )
                    db.session.add(nueva_asignacion)
                    print(f'✅ Asignado: {recinto.nombre}')
                else:
                    if not asignacion_existente.activo:
                        asignacion_existente.activo = True
                        print(f'✅ Reactivado: {recinto.nombre}')
                    else:
                        print(f'⚠️  Ya asignado: {recinto.nombre}')
            
            db.session.commit()
            print('✅ Todas las asignaciones guardadas')
        
        # 4. Verificar el resultado final
        print('\n--- Verificación final ---')
        recintos_admin = AdministradorRecinto.query.filter_by(
            administrador_id=admin_user.id,
            activo=True
        ).all()
        print(f'Recintos asignados al administrador: {len(recintos_admin)}')
        for ra in recintos_admin:
            print(f'  - {ra.recinto.nombre}')

if __name__ == '__main__':
    fix_admin_permissions()