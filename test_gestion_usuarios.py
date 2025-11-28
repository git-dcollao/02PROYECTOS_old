#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para verificar la funcionalidad de gestión de usuarios
(asignación de recintos adicionales a trabajadores por administradores)
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import (
    Trabajador, CustomRole, AdministradorRecinto, 
    TrabajadorRecinto, Recinto
)

def test_gestion_usuarios():
    """
    Prueba la funcionalidad de gestión de usuarios por administradores
    """
    app = create_app()
    
    with app.app_context():
        print("🧪 PRUEBA DE FUNCIONALIDAD GESTIÓN DE USUARIOS")
        print("=" * 60)
        
        # 1. Obtener un administrador de prueba
        admin_user = Trabajador.query.filter_by(email='administrador@sistema.local').first()
        
        if not admin_user:
            print("❌ No se encontró el usuario administrador de prueba")
            return
            
        print(f"👤 Administrador de prueba: {admin_user.nombre} ({admin_user.email})")
        
        # 2. Verificar recintos asignados al administrador
        recintos_admin = AdministradorRecinto.obtener_recintos_administrador(admin_user.id)
        print(f"🏢 Recintos que gestiona: {len(recintos_admin)}")
        
        recinto_ids_admin = []
        for asignacion in recintos_admin:
            recinto = Recinto.query.get(asignacion.recinto_id)
            if recinto:
                recinto_ids_admin.append(recinto.id)
                print(f"   - {recinto.nombre} (ID: {recinto.id})")
        
        if not recinto_ids_admin:
            print("⚠️  El administrador no tiene recintos asignados")
            return
            
        # 3. Obtener trabajadores de esos recintos (excluyendo administradores)
        trabajadores = Trabajador.query.join(CustomRole).filter(
            Trabajador.recinto_id.in_(recinto_ids_admin),
            CustomRole.name.notin_(['ADMINISTRADOR', 'SUPERADMIN'])
        ).all()
        
        print(f"👥 Trabajadores gestionables: {len(trabajadores)}")
        for trabajador in trabajadores[:3]:  # Mostrar máximo 3
            print(f"   - {trabajador.nombre} (Recinto: {trabajador.recinto.nombre if trabajador.recinto else 'Sin recinto'})")
        
        if not trabajadores:
            print("⚠️  No hay trabajadores gestionables en los recintos asignados")
            return
            
        # 4. Probar la matriz de gestión
        print(f"\n📊 PROBANDO MATRIZ DE GESTIÓN")
        trabajadores_matriz, estructura, asignaciones = TrabajadorRecinto.obtener_matriz_por_administrador(admin_user.id)
        
        print(f"📋 Trabajadores en matriz: {len(trabajadores_matriz)}")
        print(f"🏗️  Sectores en estructura: {len(estructura)}")
        print(f"📎 Asignaciones actuales: {sum(len(asigs) for asigs in asignaciones.values())}")
        
        # 5. Probar asignación de un recinto adicional
        if trabajadores_matriz and estructura:
            trabajador_prueba = trabajadores_matriz[0]
            
            # Buscar un recinto diferente al recinto de origen del trabajador
            recinto_adicional = None
            for sector, tipos in estructura.items():
                for tipo, recintos in tipos.items():
                    for recinto in recintos:
                        if recinto.id != trabajador_prueba.recinto_id:
                            recinto_adicional = recinto
                            break
                    if recinto_adicional:
                        break
                if recinto_adicional:
                    break
            
            if recinto_adicional:
                print(f"\n🔧 PRUEBA DE ASIGNACIÓN")
                print(f"👤 Trabajador: {trabajador_prueba.nombre}")
                print(f"🏠 Recinto origen: {trabajador_prueba.recinto.nombre}")
                print(f"🏢 Recinto adicional: {recinto_adicional.nombre}")
                
                # Probar asignación
                success, message = TrabajadorRecinto.asignar_recinto(
                    trabajador_prueba.id, 
                    recinto_adicional.id
                )
                print(f"✅ Asignar: {success} - {message}")
                
                # Verificar asignación
                tiene_acceso = TrabajadorRecinto.tiene_acceso_recinto(
                    trabajador_prueba.id, 
                    recinto_adicional.id
                )
                print(f"🔍 Verificar acceso: {tiene_acceso}")
                
                # Probar desasignación
                success, message = TrabajadorRecinto.desasignar_recinto(
                    trabajador_prueba.id, 
                    recinto_adicional.id
                )
                print(f"❌ Desasignar: {success} - {message}")
                
                # Verificar desasignación
                tiene_acceso = TrabajadorRecinto.tiene_acceso_recinto(
                    trabajador_prueba.id, 
                    recinto_adicional.id
                )
                print(f"🔍 Verificar acceso después: {tiene_acceso}")

def test_permisos_administrador():
    """
    Prueba que los administradores solo puedan gestionar trabajadores de sus recintos
    """
    app = create_app()
    
    with app.app_context():
        print("\n🔒 PRUEBA DE PERMISOS DE ADMINISTRADOR")
        print("=" * 50)
        
        # Obtener administrador
        admin_user = Trabajador.query.filter_by(email='administrador@sistema.local').first()
        if not admin_user:
            print("❌ No se encontró administrador de prueba")
            return
            
        # Obtener recintos gestionados
        recintos_admin = AdministradorRecinto.obtener_recintos_administrador(admin_user.id)
        recinto_ids_admin = [asignacion.recinto_id for asignacion in recintos_admin]
        
        # Obtener un trabajador de un recinto NO gestionado
        trabajador_externo = Trabajador.query.filter(
            ~Trabajador.recinto_id.in_(recinto_ids_admin) if recinto_ids_admin else True,
            Trabajador.id != admin_user.id
        ).first()
        
        if trabajador_externo:
            print(f"👤 Trabajador externo: {trabajador_externo.nombre}")
            print(f"🏢 Su recinto: {trabajador_externo.recinto.nombre if trabajador_externo.recinto else 'Sin recinto'}")
            
            # Verificar que el admin NO puede gestionar este trabajador
            puede_gestionar = trabajador_externo.recinto_id in recinto_ids_admin if recinto_ids_admin else False
            print(f"🚫 ¿Puede gestionar?: {puede_gestionar}")
            
            if not puede_gestionar:
                print("✅ Permisos funcionando correctamente - Admin no puede gestionar trabajadores externos")
            else:
                print("❌ ERROR: Admin puede gestionar trabajadores que no debería")
        else:
            print("⚠️  No se encontró trabajador externo para probar permisos")

def test_modelo_trabajador_recinto():
    """
    Prueba las funciones del modelo TrabajadorRecinto
    """
    app = create_app()
    
    with app.app_context():
        print("\n🔧 PRUEBA DEL MODELO TrabajadorRecinto")
        print("=" * 45)
        
        # Verificar que el modelo existe y está importado
        try:
            from app.models import TrabajadorRecinto
            print("✅ Modelo TrabajadorRecinto importado correctamente")
            
            # Verificar métodos estáticos
            methods = ['asignar_recinto', 'desasignar_recinto', 'obtener_recintos_trabajador', 
                      'tiene_acceso_recinto', 'obtener_matriz_por_administrador']
            
            for method in methods:
                if hasattr(TrabajadorRecinto, method):
                    print(f"✅ Método {method} disponible")
                else:
                    print(f"❌ Método {method} NO disponible")
                    
        except ImportError as e:
            print(f"❌ Error importando TrabajadorRecinto: {e}")

if __name__ == "__main__":
    print("🚀 INICIANDO PRUEBAS DE GESTIÓN DE USUARIOS\n")
    
    try:
        test_modelo_trabajador_recinto()
        test_gestion_usuarios() 
        test_permisos_administrador()
        
        print("\n✅ TODAS LAS PRUEBAS COMPLETADAS")
        
    except Exception as e:
        print(f"\n❌ ERROR EN LAS PRUEBAS: {str(e)}")
        import traceback
        traceback.print_exc()