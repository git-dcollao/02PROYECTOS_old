#!/usr/bin/env python3
"""
🔍 DIAGNÓSTICO MYSQL - Sistema de Limpieza de Base de Datos
==========================================================

Herramienta de diagnóstico para validar configuración MySQL
y probar capacidades de limpieza antes de restauración completa.

Autor: Asistente IA  
Versión: 1.0
Fecha: 2025-11-18
"""

import os
import sys
import time
import traceback
import pymysql
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Agregar el directorio app al PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def main():
    """Función principal de diagnóstico"""
    print("🔍 DIAGNÓSTICO MYSQL - Sistema de Limpieza")
    print("=" * 50)
    
    try:
        from app.models import db, Trabajador
        from app.services.backup_service import EnhancedBackupManager
        from config import Config
        
        # Configuración de conexión
        config = Config()
        database_url = config.SQLALCHEMY_DATABASE_URI
        
        print(f"📊 URL de Base de Datos: {database_url}")
        print("")
        
        # Test 1: Conexión básica
        print("🔧 TEST 1: Conexión básica a MySQL")
        test_basic_connection(database_url)
        print("")
        
        # Test 2: Configuraciones de timeout
        print("⏰ TEST 2: Configuraciones de timeout")
        test_mysql_timeouts(database_url)
        print("")
        
        # Test 3: Análisis de tablas
        print("📋 TEST 3: Análisis de tablas del sistema")
        test_table_analysis(database_url)
        print("")
        
        # Test 4: Test de limpieza simulada
        print("🧹 TEST 4: Simulación de limpieza (dry-run)")
        test_cleanup_simulation(database_url)
        print("")
        
        # Test 5: Test de configuración de backup service
        print("⚙️ TEST 5: Configuración de BackupService")
        test_backup_service_config()
        print("")
        
        print("✅ DIAGNÓSTICO COMPLETADO EXITOSAMENTE")
        
    except Exception as e:
        print(f"❌ ERROR CRÍTICO EN DIAGNÓSTICO: {e}")
        traceback.print_exc()
        return 1
    
    return 0

def test_basic_connection(database_url):
    """Test básico de conexión"""
    try:
        engine = create_engine(database_url)
        
        with engine.connect() as connection:
            result = connection.execute(text("SELECT VERSION() as version"))
            version = result.scalar()
            print(f"✅ Conexión exitosa - MySQL versión: {version}")
            
            # Test de configuración
            result = connection.execute(text("SHOW VARIABLES LIKE 'max_allowed_packet'"))
            packet_size = result.fetchone()
            print(f"📦 Max allowed packet: {packet_size[1]}")
            
    except Exception as e:
        print(f"❌ Error en conexión básica: {e}")
        raise

def test_mysql_timeouts(database_url):
    """Test de configuraciones de timeout"""
    try:
        engine = create_engine(database_url)
        
        with engine.connect() as connection:
            timeout_vars = [
                'wait_timeout',
                'interactive_timeout',
                'net_read_timeout',
                'net_write_timeout',
                'max_allowed_packet'
            ]
            
            for var in timeout_vars:
                result = connection.execute(text(f"SHOW VARIABLES LIKE '{var}'"))
                value = result.fetchone()
                if value:
                    print(f"⏱️  {var}: {value[1]}")
                else:
                    print(f"❓ {var}: No encontrado")
                    
    except Exception as e:
        print(f"❌ Error al verificar timeouts: {e}")

def test_table_analysis(database_url):
    """Análisis de tablas del sistema"""
    try:
        engine = create_engine(database_url)
        
        with engine.connect() as connection:
            # Obtener lista de tablas
            result = connection.execute(text("SHOW TABLES"))
            tables = [row[0] for row in result.fetchall()]
            
            print(f"📊 Total de tablas: {len(tables)}")
            print("")
            
            # Análisis de tamaño por tabla
            table_sizes = []
            for table in tables:
                try:
                    result = connection.execute(text(f"SELECT COUNT(*) FROM `{table}`"))
                    count = result.scalar()
                    table_sizes.append((table, count))
                except Exception as e:
                    print(f"⚠️  Error contando {table}: {e}")
            
            # Mostrar tablas ordenadas por tamaño
            table_sizes.sort(key=lambda x: x[1], reverse=True)
            print("📋 Tablas por número de registros:")
            
            for table, count in table_sizes[:10]:  # Top 10
                print(f"   {table}: {count:,} registros")
            
            if len(table_sizes) > 10:
                print(f"   ... y {len(table_sizes) - 10} tablas más")
                
    except Exception as e:
        print(f"❌ Error en análisis de tablas: {e}")

def test_cleanup_simulation(database_url):
    """Simulación de limpieza sin ejecutar"""
    try:
        engine = create_engine(
            database_url,
            pool_pre_ping=True,
            pool_recycle=3600,
            connect_args={
                'connect_timeout': 30,
                'read_timeout': 1800,  # 30 minutos
                'write_timeout': 1800,  # 30 minutos
            }
        )
        
        with engine.connect() as connection:
            # Test de configuración de timeout extendido
            print("🔧 Configurando timeouts extendidos...")
            
            timeout_commands = [
                "SET SESSION wait_timeout = 1800",
                "SET SESSION interactive_timeout = 1800", 
                "SET SESSION net_read_timeout = 900",
                "SET SESSION net_write_timeout = 900"
            ]
            
            for cmd in timeout_commands:
                try:
                    connection.execute(text(cmd))
                    print(f"✅ {cmd}")
                except Exception as e:
                    print(f"⚠️  {cmd} - Error: {e}")
            
            # Test de operaciones simuladas
            print("\n🧪 Probando operaciones de limpieza...")
            
            # Obtener tablas del sistema
            result = connection.execute(text("SHOW TABLES"))
            tables = [row[0] for row in result.fetchall()]
            
            # Filtrar tablas del sistema
            system_tables = [
                'migration_versions',
                'alembic_version',
                'mysql',
                'information_schema',
                'performance_schema',
                'sys'
            ]
            
            user_tables = [t for t in tables if not any(st in t.lower() for st in system_tables)]
            
            print(f"📊 Total tablas de usuario a limpiar: {len(user_tables)}")
            
            # Simular limpieza tabla por tabla
            simulation_time = 0
            for i, table in enumerate(user_tables[:5]):  # Solo primeras 5 para demo
                start_time = time.time()
                
                try:
                    # Solo consultar estructura (no ejecutar limpieza)
                    result = connection.execute(text(f"DESCRIBE `{table}`"))
                    columns = result.fetchall()
                    
                    duration = time.time() - start_time
                    simulation_time += duration
                    
                    print(f"   {i+1:2d}. {table}: {len(columns)} columnas - {duration:.3f}s")
                    
                except Exception as e:
                    print(f"   {i+1:2d}. {table}: ❌ Error - {e}")
            
            print(f"\n⏱️  Tiempo simulado para 5 tablas: {simulation_time:.3f}s")
            print(f"📈 Proyección para {len(user_tables)} tablas: ~{simulation_time * len(user_tables) / 5:.1f}s")
            
    except Exception as e:
        print(f"❌ Error en simulación: {e}")

def test_backup_service_config():
    """Test de configuración del servicio de backup"""
    try:
        # Importar EnhancedBackupManager
        from app.services.backup_service import EnhancedBackupManager
        
        # Crear instancia
        backup_manager = EnhancedBackupManager()
        
        print(f"✅ EnhancedBackupManager inicializado correctamente")
        print(f"📂 Directorio de backups: {getattr(backup_manager, 'backup_directory', 'No definido')}")
        
        # Verificar métodos disponibles
        methods = [method for method in dir(backup_manager) if not method.startswith('_')]
        print(f"🔧 Métodos disponibles: {len(methods)}")
        
        # Verificar método de limpieza
        if hasattr(backup_manager, '_clear_all_database_tables'):
            print("✅ Método de limpieza encontrado: _clear_all_database_tables")
        else:
            print("❌ Método de limpieza no encontrado")
            
    except Exception as e:
        print(f"❌ Error en EnhancedBackupManager: {e}")

if __name__ == "__main__":
    exit_code = main()
    print(f"\n🎯 Diagnóstico terminado con código: {exit_code}")
    sys.exit(exit_code)