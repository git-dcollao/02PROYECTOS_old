#!/usr/bin/env python3
"""
Script para probar la funcionalidad de agregar categorías
"""
import sys
import os
import requests
import json

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Category, Page, PagePermission, UserRole

def test_category_creation():
    """Probar la creación de categorías desde la base de datos"""
    app = create_app()
    
    with app.app_context():
        print("🧪 Probando funcionalidad de categorías...")
        
        # Crear una categoría de prueba
        test_category = Category(
            name="Prueba BD",
            color="success",
            description="Categoría de prueba creada programáticamente"
        )
        
        try:
            db.session.add(test_category)
            db.session.commit()
            print(f"✅ Categoría '{test_category.name}' creada con ID: {test_category.id}")
            
            # Verificar que se guardó
            saved_category = Category.query.filter_by(name="Prueba BD").first()
            if saved_category:
                print(f"✅ Categoría verificada: {saved_category.name} - {saved_category.color}")
                
                # Eliminar la categoría de prueba
                db.session.delete(saved_category)
                db.session.commit()
                print("✅ Categoría de prueba eliminada")
                
            else:
                print("❌ No se pudo verificar la categoría")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            db.session.rollback()

def show_current_categories():
    """Mostrar categorías actuales"""
    app = create_app()
    
    with app.app_context():
        print("\n📋 Categorías actuales en la base de datos:")
        print("-" * 50)
        
        categories = Category.query.all()
        for category in categories:
            pages_count = len(category.pages)
            print(f"🏷️  {category.name} ({category.color}) - {pages_count} páginas")
        
        print(f"\n📊 Total: {len(categories)} categorías")

if __name__ == '__main__':
    print("🔧 Probando sistema de categorías con base de datos")
    print("=" * 60)
    
    show_current_categories()
    test_category_creation()
    
    print("\n" + "=" * 60)
    print("🎉 Pruebas completadas")
#!/usr/bin/env python3
"""
Script para probar la funcionalidad de agregar categorías
"""
import sys
import os
import requests
import json

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Category, Page, PagePermission, UserRole

def test_category_creation():
    """Probar la creación de categorías desde la base de datos"""
    app = create_app()
    
    with app.app_context():
        print("🧪 Probando funcionalidad de categorías...")
        
        # Crear una categoría de prueba
        test_category = Category(
            name="Prueba BD",
            color="success",
            description="Categoría de prueba creada programáticamente"
        )
        
        try:
            db.session.add(test_category)
            db.session.commit()
            print(f"✅ Categoría '{test_category.name}' creada con ID: {test_category.id}")
            
            # Verificar que se guardó
            saved_category = Category.query.filter_by(name="Prueba BD").first()
            if saved_category:
                print(f"✅ Categoría verificada: {saved_category.name} - {saved_category.color}")
                
                # Eliminar la categoría de prueba
                db.session.delete(saved_category)
                db.session.commit()
                print("✅ Categoría de prueba eliminada")
                
            else:
                print("❌ No se pudo verificar la categoría")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            db.session.rollback()

def show_current_categories():
    """Mostrar categorías actuales"""
    app = create_app()
    
    with app.app_context():
        print("\n📋 Categorías actuales en la base de datos:")
        print("-" * 50)
        
        categories = Category.query.all()
        for category in categories:
            pages_count = len(category.pages)
            print(f"🏷️  {category.name} ({category.color}) - {pages_count} páginas")
        
        print(f"\n📊 Total: {len(categories)} categorías")

if __name__ == '__main__':
    print("🔧 Probando sistema de categorías con base de datos")
    print("=" * 60)
    
    show_current_categories()
    test_category_creation()
    
    print("\n" + "=" * 60)
    print("🎉 Pruebas completadas")
