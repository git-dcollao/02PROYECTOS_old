import os
import time
import sys
from sqlalchemy import create_engine, text, inspect
from dotenv import load_dotenv

load_dotenv()

def check_database_connection():
    """Verifica la conexión a la base de datos"""
    
    print("🔍 Verificando conexión a la base de datos...")
    
    # Obtener URL de la base de datos
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("❌ No se encontró la variable DATABASE_URL en el archivo .env")
        return False

    # Validar formato de URL
    if not any(db_url.startswith(prefix) for prefix in ['mysql', 'sqlite', 'postgresql']):
        print(f"❌ URL de base de datos inválida: {db_url}")
        return False

    print(f"🔗 Conectando a: {db_url.split('@')[0]}@***")

    # Intentar conexión
    max_attempts = 10
    for attempt in range(max_attempts):
        try:
            print(f"🔄 Intento {attempt + 1}/{max_attempts}...")
            engine = create_engine(db_url)
            
            with engine.connect() as connection:
                # Test básico de conexión
                result = connection.execute(text("SELECT 1 as test"))
                test_result = result.fetchone()
                
                if test_result[0] != 1:
                    print("❌ Error en test básico de conexión")
                    return False
                
                print("✅ Conexión exitosa")
                
                # Obtener información del servidor
                try:
                    if 'mysql' in db_url:
                        version = connection.execute(text("SELECT VERSION()")).fetchone()[0]
                        print(f"📊 MySQL Version: {version}")
                        
                        # Verificar charset
                        charset = connection.execute(text(
                            "SELECT DEFAULT_CHARACTER_SET_NAME FROM information_schema.SCHEMATA "
                            "WHERE SCHEMA_NAME = DATABASE()"
                        )).fetchone()
                        if charset:
                            print(f"🔤 Charset: {charset[0]}")
                    
                except Exception as e:
                    print(f"⚠️  No se pudo obtener información del servidor: {e}")
                
                # Verificar base de datos actual
                try:
                    current_db = connection.execute(text("SELECT DATABASE()")).fetchone()[0]
                    print(f"🗄️  Base de datos actual: {current_db}")
                except Exception as e:
                    print(f"⚠️  No se pudo determinar la base de datos actual: {e}")
                
                # Listar tablas
                inspector = inspect(engine)
                tables = inspector.get_table_names()
                
                print(f"\n📋 Tablas encontradas: {len(tables)}")
                
                if tables:
                    table_info = {}
                    for table in tables:
                        try:
                            count_result = connection.execute(text(f"SELECT COUNT(*) FROM `{table}`"))
                            count = count_result.fetchone()[0]
                            table_info[table] = count
                            print(f"   ✅ {table}: {count} registros")
                        except Exception as e:
                            table_info[table] = f"Error: {e}"
                            print(f"   ❌ {table}: Error al contar registros")
                    
                    # Mostrar resumen
                    total_records = sum(count for count in table_info.values() if isinstance(count, int))
                    print(f"\n📊 Resumen:")
                    print(f"   - Total tablas: {len(tables)}")
                    print(f"   - Total registros: {total_records}")
                else:
                    print("   ⚠️  No se encontraron tablas. La base de datos está vacía.")
                    print("   💡 Ejecuta 'python init_app.py' para crear las tablas iniciales")
                
                # Test de escritura (opcional)
                try:
                    connection.execute(text("CREATE TEMPORARY TABLE test_write (id INT)"))
                    connection.execute(text("INSERT INTO test_write VALUES (1)"))
                    connection.execute(text("DROP TEMPORARY TABLE test_write"))
                    print("✅ Test de escritura exitoso")
                except Exception as e:
                    print(f"⚠️  Test de escritura falló: {e}")
                
                return True
                
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Error en intento {attempt + 1}: {error_msg}")
            
            # Diagnóstico específico para errores comunes
            if "Access denied" in error_msg:
                print("💡 Verifica las credenciales de la base de datos en el archivo .env")
            elif "Unknown database" in error_msg:
                print("💡 La base de datos no existe. Verifica el nombre en el archivo .env")
            elif "Can't connect" in error_msg or "Connection refused" in error_msg:
                print("💡 El servidor de base de datos no está disponible")
                print("   - Verifica que Docker esté ejecutándose")
                print("   - Ejecuta: docker-compose up -d proyectos_db")
            elif "timeout" in error_msg.lower():
                print("💡 Timeout de conexión. El servidor puede estar iniciándose...")
            
            if attempt < max_attempts - 1:
                wait_time = min(2 * (attempt + 1), 10)  # Backoff exponencial
                print(f"⏳ Reintentando en {wait_time} segundos...")
                time.sleep(wait_time)
            else:
                print("\n💥 No se pudo conectar a la base de datos después de múltiples intentos")
                print("\n🔧 Pasos para solucionar:")
                print("1. Verifica que Docker esté ejecutándose")
                print("2. Ejecuta: docker-compose up -d proyectos_db")
                print("3. Verifica las variables en el archivo .env")
                print("4. Revisa los logs: docker-compose logs proyectos_db")
                return False
    
    return False

def check_environment():
    """Verificar variables de entorno necesarias"""
    print("\n🔍 Verificando variables de entorno...")
    
    required_vars = [
        'DATABASE_URL',
        'SECRET_KEY',
        'MYSQL_DB',
        'MYSQL_USER',
        'MYSQL_PW'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
            print(f"❌ {var}: No definida")
        else:
            # Mostrar valor censurado para variables sensibles
            if 'password' in var.lower() or 'secret' in var.lower() or 'key' in var.lower():
                print(f"✅ {var}: ***")
            else:
                print(f"✅ {var}: {value}")
    
    if missing_vars:
        print(f"\n❌ Variables faltantes: {', '.join(missing_vars)}")
        print("💡 Crea un archivo .env con las variables necesarias")
        return False
    
    print("✅ Todas las variables de entorno están definidas")
    return True

def main():
    """Función principal"""
    print("=" * 60)
    print("🔧 VERIFICADOR DE BASE DE DATOS - Sistema de Proyectos")
    print("=" * 60)
    
    # Verificar variables de entorno
    if not check_environment():
        sys.exit(1)
    
    # Verificar conexión a la base de datos
    if check_database_connection():
        print("\n🎉 ¡Verificación completada exitosamente!")
        print("✅ La base de datos está funcionando correctamente")
        sys.exit(0)
    else:
        print("\n⚠️  Verificación fallida")
        print("❌ Hubo problemas al conectar con la base de datos")
        sys.exit(1)

if __name__ == "__main__":
    main()
