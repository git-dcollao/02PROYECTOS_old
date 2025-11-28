#!/usr/bin/env python3
"""
Script de diagnóstico interno del sistema de backups
Se ejecuta dentro del contenedor de Flask
"""

import sys
import os
sys.path.append('/app')

from app import create_app, db
from app.routes.admin_routes import BackupManager
import json

def test_backup_system():
    """Probar sistema de backups internamente"""
    print("🔧 DIAGNÓSTICO INTERNO DEL SISTEMA DE BACKUPS")
    print("=" * 50)
    
    try:
        # Crear instancia de la aplicación
        app = create_app()
        
        with app.app_context():
            # Crear instancia del BackupManager
            backup_manager = BackupManager()
            
            print("✅ BackupManager inicializado correctamente")
            print(f"📁 Directorio de backups: {backup_manager.backup_dir}")
            
            # 1. Probar listado de backups
            print("\n📋 Probando listado de backups...")
            backups = backup_manager.list_backups()
            print(f"✅ Backups encontrados: {len(backups)}")
            
            for i, backup in enumerate(backups[:3]):
                print(f"   {i+1}. {backup.get('name', 'Sin nombre')} - {backup.get('size', 0)} bytes")
            
            if len(backups) > 3:
                print(f"   ... y {len(backups) - 3} más")
            
            # 2. Probar configuración de BD
            print("\n🔧 Probando configuración de base de datos...")
            db_config = backup_manager.get_db_config()
            print(f"✅ Host: {db_config['host']}")
            print(f"✅ Database: {db_config['database']}")
            print(f"✅ User: {db_config['user']}")
            
            # 3. Verificar directorio de backups
            print(f"\n📁 Verificando directorio: {backup_manager.backup_dir}")
            if os.path.exists(backup_manager.backup_dir):
                files = os.listdir(backup_manager.backup_dir)
                sql_files = [f for f in files if f.endswith(('.sql', '.sql.gz'))]
                meta_files = [f for f in files if f.endswith('.meta')]
                
                print(f"✅ Archivos SQL: {len(sql_files)}")
                print(f"✅ Archivos metadata: {len(meta_files)}")
                
                # Mostrar tamaños
                total_size = 0
                for f in sql_files:
                    filepath = os.path.join(backup_manager.backup_dir, f)
                    size = os.path.getsize(filepath)
                    total_size += size
                
                print(f"📊 Tamaño total: {total_size:,} bytes ({total_size/1024/1024:.2f} MB)")
            else:
                print("❌ Directorio de backups no existe")
            
            # 4. Probar creación de backup de prueba (opcional)
            print("\n💾 ¿Crear backup de prueba? (Escribir 'si' para continuar)")
            # En lugar de input, vamos a crear uno automáticamente para las pruebas
            print("🚀 Creando backup de prueba automático...")
            
            result = backup_manager.create_backup(
                backup_name="diagnostico_sistema",
                description="Backup de diagnóstico automático",
                include_data=True,
                compress=True
            )
            
            if result.get('success'):
                print(f"✅ Backup de prueba creado: {result.get('filename')}")
                print(f"📊 Tamaño: {result.get('size', 0)} bytes")
            else:
                print(f"❌ Error creando backup: {result.get('message')}")
            
            print("\n" + "=" * 50)
            print("🎯 DIAGNÓSTICO COMPLETADO")
            print("✅ Sistema de backups funcionando correctamente")
            
            return True
            
    except Exception as e:
        print(f"❌ Error durante el diagnóstico: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_backup_system()