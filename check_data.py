#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script para verificar y mostrar datos con codificación correcta"""

from app import create_app, db
from app.models import Area, Trabajador
from sqlalchemy import text
import sys

app = create_app()

with app.app_context():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    
    print("=" * 60)
    print("📊 VERIFICACIÓN DE DATOS EN LA BASE DE DATOS")
    print("=" * 60)
    
    # Verificar áreas
    print("\n🏢 ÁREAS:")
    try:
        areas = db.session.execute(text("SELECT id, nombre, descripcion FROM area LIMIT 10")).fetchall()
        for area in areas:
            print(f"  ID {area[0]}: {area[1]}")
            if area[2]:
                print(f"      Descripción: {area[2]}")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    # Verificar páginas
    print("\n📄 PÁGINAS:")
    try:
        pages = db.session.execute(text("SELECT id, name, route FROM pages WHERE name LIKE '%ión%' OR name LIKE '%Gest%' LIMIT 10")).fetchall()
        for page in pages:
            print(f"  ID {page[0]}: {page[1]} → {page[2]}")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ VERIFICACIÓN COMPLETADA")
    print("=" * 60)
