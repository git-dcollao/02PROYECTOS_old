#!/usr/bin/env python3
"""
Script de gestión para la aplicación de proyectos
"""

import os
import sys
import click
from flask import Flask
from flask.cli import with_appcontext

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import create_app, db
    from config import get_config
except ImportError as e:
    print(f"❌ Error de importación: {e}")
    print("💡 Asegúrate de que el directorio 'app' existe y contiene los archivos necesarios")
    sys.exit(1)

# Crear aplicación
app = create_app()

@app.cli.command()
@click.option('--coverage/--no-coverage', default=False, help='Ejecutar con cobertura de código')
def test(coverage):
    """Ejecutar tests unitarios"""
    try:
        import pytest
        
        if coverage:
            os.environ['FLASK_COVERAGE'] = '1'
            import coverage as cov
            COV = cov.Coverage(branch=True, include='app/*')
            COV.start()
        
        # Ejecutar tests
        exit_code = pytest.main(['-v', 'tests/'])
        
        if coverage:
            COV.stop()
            COV.save()
            print('\nReporte de cobertura:')
            COV.report()
            COV.html_report(directory='htmlcov')
            print('Reporte HTML guardado en: htmlcov/index.html')
            COV.erase()
        
        sys.exit(exit_code)
    except ImportError:
        print("❌ pytest no está instalado. Ejecuta: pip install pytest")

@app.cli.command()
@click.option('--length', default=32, help='Longitud de la clave')
def generate_secret_key(length):
    """Generar una clave secreta segura"""
    import secrets
    import string
    
    alphabet = string.ascii_letters + string.digits + '!@#$%^&*'
    secret_key = ''.join(secrets.choice(alphabet) for _ in range(length))
    
    print(f"Clave secreta generada ({length} caracteres):")
    print(f"SECRET_KEY='{secret_key}'")
    print("\n⚠️ Guarda esta clave en tu archivo .env")

@app.cli.command()
@with_appcontext
def init_db():
    """Inicializar la base de datos"""
    print("🗄️ Inicializando base de datos...")
    
    try:
        db.create_all()
        print("✅ Tablas creadas exitosamente")
        
        # Crear datos iniciales
        try:
            from app.seeds import crear_datos_iniciales
            if crear_datos_iniciales():
                print("✅ Datos iniciales creados")
            else:
                print("⚠️ Algunos datos iniciales no se pudieron crear")
        except ImportError:
            print("⚠️ No se encontró el módulo seeds")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

@app.cli.command()
@with_appcontext
def seed_data():
    """Crear datos de ejemplo para desarrollo"""
    print("🌱 Creando datos de ejemplo...")
    
    try:
        from app.seeds import crear_datos_ejemplo
        if crear_datos_ejemplo():
            print("✅ Datos de ejemplo creados exitosamente")
        else:
            print("⚠️ Algunos datos no se pudieron crear")
            
    except Exception as e:
        print(f"❌ Error: {e}")

@app.cli.command()
@click.option('--format', default='table', help='Formato de salida: table, json, csv')
@with_appcontext
def show_config(format):
    """Mostrar configuración actual"""
    config_dict = {
        'FLASK_ENV': app.config.get('FLASK_ENV', 'No definido'),
        'DEBUG': app.config.get('DEBUG'),
        'TESTING': app.config.get('TESTING'),
        'DATABASE_URI': app.config.get('SQLALCHEMY_DATABASE_URI'),
        'SECRET_KEY': '***' if app.config.get('SECRET_KEY') else 'No definido',
        'LOG_LEVEL': app.config.get('LOG_LEVEL'),
        'ITEMS_PER_PAGE': app.config.get('ITEMS_PER_PAGE'),
    }
    
    if format == 'json':
        import json
        print(json.dumps(config_dict, indent=2))
    elif format == 'csv':
        print("Clave,Valor")
        for key, value in config_dict.items():
            print(f"{key},{value}")
    else:  # table
        print("\n📊 Configuración actual:")
        print("-" * 50)
        for key, value in config_dict.items():
            print(f"{key:<20}: {value}")
        print("-" * 50)

@app.cli.command()
@with_appcontext
def check_db():
    """Verificar conexión y estado de la base de datos"""
    print("🔍 Verificando base de datos...")
    
    try:
        # Probar conexión usando SQLAlchemy 2.0
        from sqlalchemy import text
        result = db.session.execute(text('SELECT 1'))
        print("✅ Conexión exitosa")
        
        # Contar tablas
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"📊 Tablas encontradas: {len(tables)}")
        
        for table in tables:
            try:
                result = db.session.execute(text(f'SELECT COUNT(*) FROM `{table}`'))
                count = result.scalar()
                print(f"   - {table}: {count} registros")
            except Exception as e:
                print(f"   - {table}: Error al contar ({e})")
                
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        sys.exit(1)

@app.cli.command()
@click.argument('email')
@click.argument('password')
@with_appcontext
def create_admin(email, password):
    """Crear usuario administrador"""
    print(f"👤 Creando administrador: {email}")
    
    try:
        from app.models import Trabajador
        from werkzeug.security import generate_password_hash
        
        # Verificar si ya existe
        if Trabajador.query.filter_by(email=email).first():
            print("❌ El usuario ya existe")
            return
        
        # Crear usuario
        admin = Trabajador(
            nombre="Administrador",
            email=email,
            password=generate_password_hash(password),
            profesion="Administrador",
            nombrecorto="admin",
            activo=True
        )
        
        db.session.add(admin)
        db.session.commit()
        
        print("✅ Administrador creado exitosamente")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.session.rollback()

@app.cli.command()
def routes():
    """Mostrar todas las rutas disponibles"""
    print("\n🛣️ Rutas disponibles:")
    print("-" * 80)
    
    rules = sorted(app.url_map.iter_rules(), key=lambda x: x.rule)
    
    for rule in rules:
        methods = ', '.join(sorted(rule.methods - {'HEAD', 'OPTIONS'}))
        print(f"{rule.rule:<40} {methods:<20} {rule.endpoint}")
    
    print("-" * 80)
    print(f"Total: {len(rules)} rutas")

if __name__ == '__main__':
    app.cli()
    """Mostrar todas las rutas disponibles"""
    print("\n🛣️  Rutas disponibles:")
    print("-" * 80)
    
    rules = sorted(app.url_map.iter_rules(), key=lambda x: x.rule)
    
    for rule in rules:
        methods = ', '.join(sorted(rule.methods - {'HEAD', 'OPTIONS'}))
        ##print(f"{rule.rule:<40} {methods:<20} {rule.endpoint}")
    
    print("-" * 80)
    print(f"Total: {len(rules)} rutas")
