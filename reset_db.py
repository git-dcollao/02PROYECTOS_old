import os
import sys
import time
from flask import Flask

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def reset_database():
    """Resetear completamente la base de datos"""
    print("🚨 ADVERTENCIA: Esto eliminará todos los datos existentes 🚨")
    print("¿Estás seguro de que deseas continuar? (s/n)")
    respuesta = input().lower()
    
    if respuesta != 's':
        print("Operación cancelada")
        return False
    
    try:
        from app import create_app, db
        app = create_app()
        
        with app.app_context():
            print("🗑️ Eliminando todas las tablas...")
            db.drop_all()
            print("✅ Tablas eliminadas correctamente")
            
            print("🏗️ Creando nuevas tablas...")
            db.create_all()
            print("✅ Tablas creadas correctamente")
            
            print("🌱 Creando datos iniciales...")
            from app.seeds import crear_datos_iniciales
            if crear_datos_iniciales():
                print("✅ Datos iniciales creados correctamente")
                return True
            else:
                print("⚠️ Hubo problemas al crear algunos datos iniciales")
                return False
                
    except Exception as e:
        print(f"❌ Error al resetear la base de datos: {str(e)}")
        return False

if __name__ == "__main__":
    if reset_database():
        print("🎉 Base de datos reiniciada exitosamente")
    else:
        print("⚠️ El reinicio de la base de datos no se completó correctamente")
