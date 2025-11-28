import time
import sys
import os

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_minimal_init():
    """Ejecutar inicialización mínima cuando falla la normal"""
    try:
        print("🔧 Ejecutando inicialización mínima del sistema...")
        from init_minimal import init_minimal_system
        return init_minimal_system()
    except Exception as e:
        print(f"❌ Error en inicialización mínima: {e}")
        return True  # Continuar de todas formas

def wait_for_db(app, max_attempts=30):
    """Esperar a que la base de datos esté disponible"""
    print("🔄 Esperando conexión a la base de datos...")
    
    for attempt in range(max_attempts):
        try:
            with app.app_context():
                from app import db
                from sqlalchemy import text
                # Usar el método correcto para SQLAlchemy 2.0
                with db.engine.connect() as connection:
                    connection.execute(text('SELECT 1'))
                print("✅ Conexión a la base de datos establecida")
                return True
                
        except Exception as e:
            print(f"❌ Intento {attempt + 1}/{max_attempts}: {e}")
            if attempt < max_attempts - 1:
                time.sleep(2)
            else:
                print("💥 No se pudo conectar a la base de datos")
                return False
    
    return False

def initialize_database(app):
    """Inicializar la base de datos y crear datos iniciales"""
    print("🚀 Inicializando base de datos...")
    
    try:
        with app.app_context():
            from app import db
            print("📋 Creando tablas...")
            db.create_all()
            print("✅ Tablas creadas exitosamente")
            
            print("🌱 Creando datos iniciales...")
            try:
                from app.seeds import crear_datos_iniciales
                if crear_datos_iniciales():
                    print("✅ Datos iniciales creados exitosamente")
                    return True
                else:
                    print("⚠️ Algunos datos iniciales no se pudieron crear")
                    print("🔄 Ejecutando inicialización mínima...")
                    return run_minimal_init()
            except ImportError:
                print("⚠️ No se encontró el módulo seeds")
                print("🔄 Ejecutando inicialización mínima...")
                return run_minimal_init()
            except Exception as e:
                print(f"❌ Error en seeds: {e}")
                print("🔄 Ejecutando inicialización mínima...")
                return run_minimal_init()
                
    except Exception as e:
        print(f"❌ Error inicializando base de datos: {e}")
        return False

def main():
    """Función principal de inicialización"""
    print("🎯 Iniciando aplicación...")
    
    try:
        from app import create_app
        app = create_app()
        print("✅ Aplicación Flask creada")
        
        if not wait_for_db(app):
            print("💥 Error: No se pudo conectar a la base de datos")
            sys.exit(1)
        
        if not initialize_database(app):
            print("⚠️ Advertencia: Problemas al inicializar datos")
        
        print("🎉 Aplicación inicializada correctamente")
        return app
        
    except Exception as e:
        print(f"💥 Error fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    app = main()
    print("🚀 Iniciando servidor Flask...")

    app.run(host='0.0.0.0', port=5050, debug=True)