#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corregir el encoding de los textos en tablas de catálogos.
Corrige: Estados, TipoProyecto, Area, AdministradorRecinto
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Estado, TipoProyecto, Area, AdministradorRecinto

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
        
        # Patrones de 4 signos
        '????': '',
    }
    
    result = text
    for old, new in replacements.items():
        result = result.replace(old, new)
    
    return result

def fix_all_catalogos():
    """Corrige el encoding de todos los textos en las tablas de catálogos"""
    
    app = create_app()
    
    with app.app_context():
        print("🔧 Iniciando corrección de encoding en catálogos...")
        print("=" * 70)
        
        total_updated = 0
        
        # ===== CORREGIR ESTADOS =====
        print("\n📄 Procesando tabla 'estado'...")
        estados = Estado.query.all()
        estados_updated = 0
        
        for estado in estados:
            updated = False
            
            # Corregir nombre
            if estado.nombre:
                fixed_nombre = fix_text_encoding(estado.nombre)
                if fixed_nombre != estado.nombre:
                    print(f"   ✓ ID {estado.id}: '{estado.nombre}' → '{fixed_nombre}'")
                    estado.nombre = fixed_nombre
                    updated = True
            
            # Corregir descripción si existe
            if hasattr(estado, 'descripcion') and estado.descripcion:
                fixed_desc = fix_text_encoding(estado.descripcion)
                if fixed_desc != estado.descripcion:
                    print(f"   ✓ [desc] ID {estado.id}: '{estado.descripcion}' → '{fixed_desc}'")
                    estado.descripcion = fixed_desc
                    updated = True
            
            if updated:
                estados_updated += 1
        
        # ===== CORREGIR TIPOS DE PROYECTO =====
        print("\n📄 Procesando tabla 'tipo_proyecto'...")
        tipos = TipoProyecto.query.all()
        tipos_updated = 0
        
        for tipo in tipos:
            updated = False
            
            # Corregir nombre
            if tipo.nombre:
                fixed_nombre = fix_text_encoding(tipo.nombre)
                if fixed_nombre != tipo.nombre:
                    print(f"   ✓ ID {tipo.id}: '{tipo.nombre}' → '{fixed_nombre}'")
                    tipo.nombre = fixed_nombre
                    updated = True
            
            # Corregir descripción si existe
            if hasattr(tipo, 'descripcion') and tipo.descripcion:
                fixed_desc = fix_text_encoding(tipo.descripcion)
                if fixed_desc != tipo.descripcion:
                    print(f"   ✓ [desc] ID {tipo.id}: '{tipo.descripcion}' → '{fixed_desc}'")
                    tipo.descripcion = fixed_desc
                    updated = True
            
            if updated:
                tipos_updated += 1
        
        # ===== CORREGIR AREAS =====
        print("\n📄 Procesando tabla 'area'...")
        areas = Area.query.all()
        areas_updated = 0
        
        for area in areas:
            updated = False
            
            # Corregir nombre
            if area.nombre:
                fixed_nombre = fix_text_encoding(area.nombre)
                if fixed_nombre != area.nombre:
                    print(f"   ✓ ID {area.id}: '{area.nombre}' → '{fixed_nombre}'")
                    area.nombre = fixed_nombre
                    updated = True
            
            # Corregir descripción si existe
            if hasattr(area, 'descripcion') and area.descripcion:
                fixed_desc = fix_text_encoding(area.descripcion)
                if fixed_desc != area.descripcion:
                    print(f"   ✓ [desc] ID {area.id}: '{area.descripcion}' → '{fixed_desc}'")
                    area.descripcion = fixed_desc
                    updated = True
            
            if updated:
                areas_updated += 1
        
        # ===== CORREGIR ADMINISTRADOR RECINTO (si tiene campos de texto) =====
        print("\n📄 Procesando tabla 'administrador_recinto'...")
        admins = AdministradorRecinto.query.all()
        admins_updated = 0
        
        for admin in admins:
            updated = False
            
            # Verificar si tiene algún campo de texto para corregir
            for field in ['nombre', 'descripcion', 'observaciones', 'notas']:
                if hasattr(admin, field):
                    value = getattr(admin, field)
                    if value and isinstance(value, str):
                        fixed_value = fix_text_encoding(value)
                        if fixed_value != value:
                            print(f"   ✓ [{field}] ID {admin.id}: '{value}' → '{fixed_value}'")
                            setattr(admin, field, fixed_value)
                            updated = True
            
            if updated:
                admins_updated += 1
        
        # ===== GUARDAR CAMBIOS =====
        total_updated = estados_updated + tipos_updated + areas_updated + admins_updated
        
        if total_updated > 0:
            try:
                db.session.commit()
                print("=" * 70)
                print(f"✅ Corrección completada exitosamente:")
                print(f"   • Estados actualizados: {estados_updated}")
                print(f"   • Tipos de Proyecto actualizados: {tipos_updated}")
                print(f"   • Áreas actualizadas: {areas_updated}")
                print(f"   • Administradores actualizados: {admins_updated}")
                print(f"   • Total: {total_updated}")
                print("=" * 70)
                
                # Verificar algunos registros
                print("\n📋 Verificación de datos corregidos:")
                
                print("\nEstados:")
                estados_test = Estado.query.limit(5).all()
                for e in estados_test:
                    print(f"   ID {e.id}: {e.nombre}")
                
                print("\nTipos de Proyecto:")
                tipos_test = TipoProyecto.query.limit(5).all()
                for t in tipos_test:
                    print(f"   ID {t.id}: {t.nombre}")
                
                print("\nÁreas:")
                areas_test = Area.query.limit(5).all()
                for a in areas_test:
                    print(f"   ID {a.id}: {a.nombre}")
                    
            except Exception as e:
                db.session.rollback()
                print(f"❌ Error al guardar: {e}")
                return False
        else:
            print("ℹ️  No se encontraron textos para corregir")
        
        return True

if __name__ == '__main__':
    success = fix_all_catalogos()
    sys.exit(0 if success else 1)
