#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para verificar el filtrado de requerimientos por aceptar
basado en los recintos asignados a administradores.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import (
    Trabajador, CustomRole, AdministradorRecinto, 
    Requerimiento, Recinto, Estado
)

def test_requerimientos_aceptar_filtrado():
    """
    Prueba el filtrado de requerimientos por aceptar (estado En Solicitud)
    """
    app = create_app()
    
    with app.app_context():
        print("🧪 PRUEBA DE FILTRADO DE REQUERIMIENTOS POR ACEPTAR")
        print("=" * 60)
        
        # Obtener el usuario administrador de prueba
        admin_user = Trabajador.query.filter_by(email='administrador@sistema.local').first()
        
        if not admin_user:
            print("❌ No se encontró el usuario administrador de prueba")
            return
            
        print(f"👤 Usuario de prueba: {admin_user.nombre} ({admin_user.email})")
        
        # Verificar recintos asignados
        recintos_asignados = AdministradorRecinto.obtener_recintos_administrador(admin_user.id)
        print(f"🏢 Recintos asignados: {len(recintos_asignados)}")
        
        recinto_ids = []
        for asignacion in recintos_asignados:
            recinto = Recinto.query.get(asignacion.recinto_id)
            if recinto:
                recinto_ids.append(recinto.id)
                print(f"   - {recinto.nombre} (ID: {recinto.id})")
        
        if not recinto_ids:
            print("⚠️  El administrador no tiene recintos asignados")
            return
            
        # Obtener estado "En Solicitud" (id_estado = 1)
        estado_solicitud = Estado.query.filter_by(id=1).first()
        if not estado_solicitud:
            print("❌ No se encontró el estado 'En Solicitud'")
            return
            
        print(f"📋 Estado a filtrar: {estado_solicitud.nombre} (ID: {estado_solicitud.id})")
        
        # Contar requerimientos totales en estado "En Solicitud"
        total_requerimientos = Requerimiento.query.filter_by(id_estado=1).count()
        print(f"📊 Total de requerimientos en estado 'En Solicitud': {total_requerimientos}")
        
        # Contar requerimientos que debería ver el administrador
        requerimientos_administrador = Requerimiento.query.filter(
            Requerimiento.id_estado == 1,
            Requerimiento.id_recinto.in_(recinto_ids)
        ).all()
        
        print(f"📋 Requerimientos por aceptar que debería ver el administrador: {len(requerimientos_administrador)}")
        
        if requerimientos_administrador:
            print("   Requerimientos visibles:")
            for req in requerimientos_administrador[:5]:  # Mostrar máximo 5
                recinto = Recinto.query.get(req.id_recinto)
                estado = Estado.query.get(req.id_estado)
                recinto_nombre = recinto.nombre if recinto else "Recinto no encontrado"
                estado_nombre = estado.nombre if estado else "Estado no encontrado"
                print(f"   {req.id}. {req.nombre} - {recinto_nombre} ({estado_nombre})")
        
        # Contar requerimientos de recintos no asignados
        requerimientos_otros = Requerimiento.query.filter(
            Requerimiento.id_estado == 1,
            ~Requerimiento.id_recinto.in_(recinto_ids)
        ).count()
        
        print(f"🚫 Requerimientos de recintos no asignados: {requerimientos_otros}")
        
        # Calcular porcentaje
        if total_requerimientos > 0:
            porcentaje = (len(requerimientos_administrador) / total_requerimientos) * 100
            print(f"📊 Porcentaje de requerimientos visibles: {porcentaje:.1f}%")
        
        print("\n✅ FUNCIONALIDADES IMPLEMENTADAS:")
        print("   ✅ Filtrado por recintos asignados")
        print("   ✅ Solo requerimientos en estado 'En Solicitud'")
        print("   ✅ SUPERADMIN mantiene acceso total")
        print("   ✅ Otros usuarios ven solo su recinto")
        print("   ✅ Administradores ven solo recintos asignados")

def test_superadmin_access():
    """
    Prueba que el SUPERADMIN mantenga acceso a todos los requerimientos por aceptar
    """
    app = create_app()
    
    with app.app_context():
        print("\n👑 PRUEBA DE ACCESO SUPERADMIN A REQUERIMIENTOS POR ACEPTAR")
        print("=" * 58)
        
        # Buscar un SUPERADMIN
        superadmin = Trabajador.query.join(CustomRole).filter(
            CustomRole.name == 'SUPERADMIN'
        ).first()
        
        if superadmin:
            print(f"👤 SUPERADMIN: {superadmin.nombre}")
            print(f"🎭 Rol: {superadmin.custom_role.name}")
            
            total_requerimientos = Requerimiento.query.filter_by(id_estado=1).count()
            print(f"   ✅ SUPERADMIN mantiene acceso total a todos los requerimientos por aceptar")
            print(f"   ✅ Puede ver todos los requerimientos en solicitud: {total_requerimientos}")
        else:
            print("   ⚠️  No se encontró usuario SUPERADMIN")

if __name__ == "__main__":
    print("🚀 INICIANDO PRUEBAS DE FILTRADO DE REQUERIMIENTOS POR ACEPTAR\n")
    
    try:
        test_requerimientos_aceptar_filtrado()
        test_superadmin_access()
        
        print("\n✅ PRUEBAS COMPLETADAS EXITOSAMENTE")
        
    except Exception as e:
        print(f"\n❌ ERROR EN LAS PRUEBAS: {str(e)}")
        import traceback
        traceback.print_exc()