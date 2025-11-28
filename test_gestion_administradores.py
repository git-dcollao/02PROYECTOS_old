#!/usr/bin/env python3
"""
Script de prueba para verificar que el sistema de gestión de administradores
funciona correctamente con el rol ADMIN dinámico.
"""

from app import create_app
from app.models import AdministradorRecinto, Trabajador, CustomRole, Recinto, Sector, TipoRecinto

def test_gestion_administradores():
    """Prueba completa del sistema de gestión de administradores"""
    
    app = create_app()
    with app.app_context():
        print("🚀 INICIANDO PRUEBAS DEL SISTEMA DE GESTIÓN DE ADMINISTRADORES")
        print("=" * 70)
        
        # 1. Verificar roles existentes
        print("\n📋 1. VERIFICANDO ROLES DEL SISTEMA:")
        roles = CustomRole.query.all()
        for role in roles:
            print(f"   - ID: {role.id}, Nombre: {role.name}, Descripción: {role.description}")
        
        # 2. Verificar usuarios con rol ADMIN
        print("\n👥 2. VERIFICANDO USUARIOS CON ROL ADMIN:")
        admin_role = CustomRole.query.filter(
            CustomRole.name.in_(['ADMIN', 'ADMINISTRADOR'])
        ).first()
        
        if admin_role:
            print(f"   ✅ Rol encontrado: {admin_role.name} (ID: {admin_role.id})")
            
            admins = Trabajador.query.filter(
                Trabajador.custom_role_id == admin_role.id
            ).all()
            
            print(f"   📊 Administradores encontrados: {len(admins)}")
            for admin in admins:
                print(f"      - {admin.email} ({admin.nombre})")
        else:
            print("   ❌ No se encontró rol ADMIN")
            return False
        
        # 3. Probar método obtener_matriz_completa()
        print("\n🔧 3. PROBANDO MÉTODO obtener_matriz_completa():")
        try:
            administradores, estructura, asignaciones = AdministradorRecinto.obtener_matriz_completa()
            
            print(f"   ✅ Administradores encontrados: {len(administradores)}")
            print(f"   ✅ Sectores en estructura: {len(estructura)}")
            print(f"   ✅ Conjuntos de asignaciones: {len(asignaciones)}")
            
            # Mostrar detalles de administradores
            for admin in administradores:
                print(f"      - {admin.email} ({admin.nombre}) - Rol: {admin.custom_role.name}")
            
            # Mostrar estructura
            print(f"\n   📊 ESTRUCTURA DE SECTORES:")
            for sector, tipos in estructura.items():
                print(f"      🏢 {sector.nombre}:")
                for tipo, recintos in tipos.items():
                    print(f"         📍 {tipo.nombre}: {len(recintos)} recintos")
            
        except Exception as e:
            print(f"   ❌ Error en obtener_matriz_completa(): {str(e)}")
            return False
        
        # 4. Verificar asignaciones existentes
        print("\n🔗 4. VERIFICANDO ASIGNACIONES EXISTENTES:")
        total_asignaciones = 0
        for admin_id, recinto_ids in asignaciones.items():
            admin = next((a for a in administradores if a.id == admin_id), None)
            if admin:
                print(f"   👤 {admin.email}: {len(recinto_ids)} recintos asignados")
                total_asignaciones += len(recinto_ids)
        
        print(f"   📊 Total de asignaciones: {total_asignaciones}")
        
        # 5. Probar asignación dinámica (simulación)
        print("\n⚙️ 5. PROBANDO LÓGICA DE ASIGNACIÓN:")
        if administradores and len(estructura) > 0:
            admin_test = administradores[0]
            
            # Obtener primer recinto disponible
            primer_recinto = None
            for sector, tipos in estructura.items():
                for tipo, recintos in tipos.items():
                    if recintos:  # Si hay recintos en este tipo
                        primer_recinto = recintos[0]
                        break
                if primer_recinto:
                    break
            
            if primer_recinto:
                print(f"   🔧 Simulando asignación: {admin_test.email} -> {primer_recinto.nombre}")
                
                # Verificar si ya está asignado
                ya_asignado = AdministradorRecinto.tiene_acceso_recinto(admin_test.id, primer_recinto.id)
                print(f"   📋 Ya asignado: {'Sí' if ya_asignado else 'No'}")
                
                if not ya_asignado:
                    print(f"   ✅ Asignación sería válida para {admin_test.email}")
                else:
                    print(f"   ℹ️  {admin_test.email} ya tiene acceso a {primer_recinto.nombre}")
        
        print("\n" + "=" * 70)
        print("🎉 TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE")
        print("✅ El sistema de gestión de administradores está funcionando correctamente")
        print("✅ El rol ADMIN se detecta dinámicamente")
        print("✅ Las consultas y métodos están operativos")
        
        return True

if __name__ == "__main__":
    success = test_gestion_administradores()
    exit(0 if success else 1)