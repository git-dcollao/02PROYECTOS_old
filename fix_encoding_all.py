#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corregir el encoding de TODOS los textos en las tablas pages y categories.
Usa reemplazo de patrones UTF-8 mal interpretados.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Page, Category

def fix_text_encoding(text):
    """
    Corrige el encoding de un texto que fue mal interpretado.
    Reemplaza patrones comunes de UTF-8 mal decodificado.
    """
    if not text:
        return text
    
    # Mapeo de caracteres UTF-8 mal interpretados
    replacements = {
        # Vocales con tilde
        '├í': 'á',
        '├®': 'é', 
        '├¡': 'í',
        '├│': 'ó',
        '├║': 'ú',
        'Ã¡': 'á',
        'Ã©': 'é',
        'Ã­': 'í',
        'Ã³': 'ó',
        'Ãº': 'ú',
        
        # Mayúsculas con tilde
        '├ü': 'Á',
        '├ë': 'É',
        '├ì': 'Í',
        '├ô': 'Ó',
        '├Ü': 'Ú',
        'Ã': 'Á',
        'Ã‰': 'É',
        'Ã': 'Í',
        'Ã"': 'Ó',
        'Ãš': 'Ú',
        
        # Ñ y ñ
        '├▒': 'ñ',
        '├æ': 'Ñ',
        'Ã±': 'ñ',
        
        # Caracteres especiales
        '┬¿': '¿',
        '┬í': '¡',
        'Â¿': '¿',
        'Â¡': '¡',
        
        # Patrones de 4 signos de interrogación
        '????': '',  # Eliminar si no se puede determinar
    }
    
    result = text
    for old, new in replacements.items():
        result = result.replace(old, new)
    
    return result

def fix_all_encoding():
    """Corrige el encoding de todos los textos en pages y categories"""
    
    app = create_app()
    
    with app.app_context():
        print("🔧 Iniciando corrección completa de encoding...")
        print("=" * 70)
        
        # ===== CORREGIR PAGES =====
        print("\n📄 Procesando tabla 'pages'...")
        pages = Page.query.all()
        pages_updated = 0
        
        for page in pages:
            updated = False
            original_name = page.name
            original_desc = page.description
            
            # Corregir name
            if page.name:
                fixed_name = fix_text_encoding(page.name)
                if fixed_name != page.name:
                    print(f"   ✓ [name] ID {page.id}: '{page.name}' → '{fixed_name}'")
                    page.name = fixed_name
                    updated = True
            
            # Corregir description
            if page.description:
                fixed_desc = fix_text_encoding(page.description)
                if fixed_desc != page.description:
                    print(f"   ✓ [desc] ID {page.id}: '{page.description}' → '{fixed_desc}'")
                    page.description = fixed_desc
                    updated = True
            
            if updated:
                pages_updated += 1
        
        # ===== CORREGIR CATEGORIES =====
        print("\n📁 Procesando tabla 'categories'...")
        categories = Category.query.all()
        categories_updated = 0
        
        for category in categories:
            updated = False
            
            # Corregir name
            if category.name:
                fixed_name = fix_text_encoding(category.name)
                if fixed_name != category.name:
                    print(f"   ✓ [name] ID {category.id}: '{category.name}' → '{fixed_name}'")
                    category.name = fixed_name
                    updated = True
            
            # Corregir description
            if category.description:
                fixed_desc = fix_text_encoding(category.description)
                if fixed_desc != category.description:
                    print(f"   ✓ [desc] ID {category.id}: '{category.description}' → '{fixed_desc}'")
                    category.description = fixed_desc
                    updated = True
            
            if updated:
                categories_updated += 1
        
        # ===== GUARDAR CAMBIOS =====
        total_updated = pages_updated + categories_updated
        
        if total_updated > 0:
            try:
                db.session.commit()
                print("=" * 70)
                print(f"✅ Corrección completada exitosamente:")
                print(f"   • Pages actualizadas: {pages_updated}")
                print(f"   • Categories actualizadas: {categories_updated}")
                print(f"   • Total: {total_updated}")
                print("=" * 70)
                
                # Verificar algunas páginas
                print("\n📋 Verificación de datos corregidos:")
                print("\nPages:")
                test_pages = Page.query.filter(Page.id.in_([1, 2, 11, 19, 38])).all()
                for page in test_pages:
                    print(f"   ID {page.id}: {page.name} - {page.description}")
                
                print("\nCategories:")
                test_cats = Category.query.all()
                for cat in test_cats:
                    print(f"   ID {cat.id}: {cat.name} - {cat.description}")
                    
            except Exception as e:
                db.session.rollback()
                print(f"❌ Error al guardar: {e}")
                return False
        else:
            print("ℹ️  No se encontraron textos para corregir")
        
        return True

if __name__ == '__main__':
    success = fix_all_encoding()
    sys.exit(0 if success else 1)
