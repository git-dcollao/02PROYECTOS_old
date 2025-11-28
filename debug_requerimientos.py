#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import create_app, db
from app.models import Requerimiento, Trabajador, AdministradorRecinto

def debug_requerimientos():
    app = create_app()
    with app.app_context():
        # Verificar requerimientos totales
        total_reqs = Requerimiento.query.count()
        print(f'Total requerimientos en BD: {total_reqs}')
        
        # Obtener últimos 5 requerimientos
        print('\nÚltimos 5 requerimientos:')
        reqs = Requerimiento.query.order_by(Requerimiento.id.desc()).limit(5).all()
        for r in reqs:
            recinto_nombre = r.recinto.nombre if r.recinto else "N/A"
            print(f'ID: {r.id}, Nombre: {r.nombre}, Recinto: {recinto_nombre}, Activo: {r.activo}')
        
        # Verificar permisos del usuario administrador@sistema.local
        print('\n--- Verificando permisos de administrador@sistema.local ---')
        admin_user = Trabajador.query.filter_by(email='administrador@sistema.local').first()
        if admin_user:
            print(f'Usuario encontrado: {admin_user.nombre}, Rol: {admin_user.rol}')
            
            # Verificar sus recintos permitidos
            recintos_admin = AdministradorRecinto.query.filter_by(administrador_id=admin_user.id).all()
            print(f'Recintos permitidos: {len(recintos_admin)}')
            for ra in recintos_admin:
                recinto_nombre = ra.recinto.nombre if ra.recinto else "N/A"
                print(f'  - Recinto ID: {ra.recinto_id}, Nombre: {recinto_nombre}')
                
            # Contar requerimientos que puede ver este usuario
            if admin_user.rol == 'SUPERADMIN':
                reqs_visibles = Requerimiento.query.filter_by(activo=True).count()
                print(f'Como SUPERADMIN puede ver: {reqs_visibles} requerimientos activos')
            else:
                recinto_ids = [ra.recinto_id for ra in recintos_admin]
                if recinto_ids:
                    reqs_visibles = Requerimiento.query.filter(
                        Requerimiento.id_recinto.in_(recinto_ids),
                        Requerimiento.activo == True
                    ).count()
                    print(f'Con permisos de recinto puede ver: {reqs_visibles} requerimientos')
                    
                    # Mostrar qué requerimientos específicos puede ver
                    print('\nRequerimientos específicos que puede ver:')
                    reqs_permitidos = Requerimiento.query.filter(
                        Requerimiento.id_recinto.in_(recinto_ids),
                        Requerimiento.activo == True
                    ).all()
                    for r in reqs_permitidos:
                        recinto_nombre = r.recinto.nombre if r.recinto else "N/A"
                        print(f'  - ID: {r.id}, {r.nombre}, Recinto: {recinto_nombre}')
                else:
                    print('No tiene recintos asignados, no puede ver requerimientos')
        else:
            print('Usuario administrador@sistema.local no encontrado')
        
        # Verificar requerimiento específico de ED. CONSISTORIAL si existe
        print('\n--- Verificando requerimientos de ED. CONSISTORIAL ---')
        from app.models import Recinto
        ed_consistorial = Recinto.query.filter_by(nombre='ED. CONSISTORIAL').first()
        if ed_consistorial:
            print(f'Recinto encontrado: {ed_consistorial.nombre} (ID: {ed_consistorial.id})')
            reqs_ed_consistorial = Requerimiento.query.filter_by(
                id_recinto=ed_consistorial.id,
                activo=True
            ).all()
            print(f'Requerimientos en ED. CONSISTORIAL: {len(reqs_ed_consistorial)}')
            for r in reqs_ed_consistorial:
                print(f'  - ID: {r.id}, {r.nombre}')
        else:
            print('Recinto ED. CONSISTORIAL no encontrado')

if __name__ == '__main__':
    debug_requerimientos()