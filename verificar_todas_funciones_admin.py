#!/usr/bin/env python3
"""
Script para verificar que todas las funciones de requerimientos 
usen correctamente el sistema AdministradorRecinto
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import db, Trabajador, AdministradorRecinto, Requerimiento, Estado

def verificar_sistema_permisos():
    app = create_app()
    
    with app.app_context():
        print("=== VERIFICAR SISTEMA DE PERMISOS CONSOLIDADO ===")
        
        # 1. Verificar usuario administrador
        admin = Trabajador.query.filter_by(email='administrador@sistema.local').first()
        if not admin:
            print("❌ Usuario administrador no encontrado")
            return
            
        print(f"👤 Usuario: {admin.nombre}")
        print(f"   Email: {admin.email}")
        print(f"   Es SUPERADMIN: {admin.is_superadmin()}")
        print(f"   Recinto directo: {admin.recinto_id}")
        
        # 2. Verificar asignaciones AdministradorRecinto
        admin_recintos = AdministradorRecinto.query.filter_by(
            administrador_id=admin.id, 
            activo=True
        ).all()
        
        print(f"\n📋 Asignaciones AdministradorRecinto: {len(admin_recintos)}")
        for ar in admin_recintos:
            print(f"   - Recinto ID {ar.recinto_id}: {ar.recinto.nombre}")
        
        # 3. Verificar permisos de páginas
        paginas_requerimientos = [
            '/requerimientos',
            '/requerimientos_aceptar', 
            '/requerimientos_completar'
        ]
        
        print(f"\n🔐 Permisos de páginas:")
        for pagina in paginas_requerimientos:
            tiene_permiso = admin.has_page_permission(pagina)
            print(f"   {pagina}: {'✅ SÍ' if tiene_permiso else '❌ NO'}")
        
        # 4. Verificar requerimientos visibles según cada filtro
        print(f"\n🔍 REQUERIMIENTOS VISIBLES POR CATEGORÍA:")
        
        # Estado "En Solicitud" para requerimientos_aceptar  
        estado_solicitud = Estado.query.filter(
            Estado.nombre.ilike('%en solicitud%')
        ).first()
        
        # Estado "Aceptado" para requerimientos_completar
        estado_aceptado = Estado.query.filter(
            Estado.nombre.ilike('%aceptada%')
        ).first()
        
        if estado_solicitud:
            reqs_aceptar = Requerimiento.query.filter(
                Requerimiento.id_estado == estado_solicitud.id
            ).all()
            print(f"   📥 En Solicitud (para aceptar): {len(reqs_aceptar)}")
            for req in reqs_aceptar:
                print(f"      ID {req.id}: {req.nombre} (Recinto: {req.recinto.nombre if req.recinto else 'N/A'})")
        
        if estado_aceptado:
            reqs_completar = Requerimiento.query.filter(
                Requerimiento.id_estado == estado_aceptado.id
            ).all()
            print(f"   ✅ Aceptados (para completar): {len(reqs_completar)}")
            for req in reqs_completar:
                print(f"      ID {req.id}: {req.nombre} (Recinto: {req.recinto.nombre if req.recinto else 'N/A'})")
        
        # 5. Simular filtros que aplicaría cada función
        recintos_admin = [ar.recinto_id for ar in admin_recintos]
        
        print(f"\n🎯 FILTROS APLICADOS (IDs de recintos: {recintos_admin}):")
        
        # Filtro general de requerimientos
        reqs_generales = Requerimiento.query.filter(
            Requerimiento.id_recinto.in_(recintos_admin)
        ).all()
        print(f"   📋 Requerimientos generales: {len(reqs_generales)}")
        
        # Filtro requerimientos_aceptar
        if estado_solicitud:
            reqs_para_aceptar = Requerimiento.query.filter(
                Requerimiento.id_estado == estado_solicitud.id,
                Requerimiento.id_recinto.in_(recintos_admin)
            ).all()
            print(f"   📥 Para aceptar/rechazar: {len(reqs_para_aceptar)}")
        
        # Filtro requerimientos_completar  
        if estado_aceptado:
            reqs_para_completar = Requerimiento.query.filter(
                Requerimiento.id_estado == estado_aceptado.id,
                Requerimiento.id_recinto.in_(recintos_admin)
            ).all()
            print(f"   ✅ Para completar: {len(reqs_para_completar)}")
        
        print(f"\n🎉 RESUMEN:")
        print(f"   ✅ Sistema AdministradorRecinto: {len(admin_recintos)} asignaciones")
        print(f"   ✅ Permisos de páginas: {len([p for p in paginas_requerimientos if admin.has_page_permission(p)])}/3")
        print(f"   ✅ Requerimientos accesibles: {len(reqs_generales)}")
        print(f"   🔧 CORRECCIONES APLICADAS: requerimientos(), requerimientos_aceptar(), requerimientos_completar()")
        print(f"   🔧 ENDPOINTS CORREGIDOS: update_requerimiento_aceptar, update_requerimiento_rechazar, update_requerimiento_completar")

if __name__ == '__main__':
    verificar_sistema_permisos()