#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de diagnóstico para verificar codificación UTF-8
"""

from app import create_app, db
from app.models import Trabajador
import sys

def test_encoding():
    """Verificar codificación de la base de datos"""
    app = create_app()
    
    with app.app_context():
        # Configurar salida UTF-8
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
        
        print("=" * 60)
        print("🔍 DIAGNÓSTICO DE CODIFICACIÓN UTF-8")
        print("=" * 60)
        
        # Test 1: Verificar conexión a BD
        try:
            result = db.session.execute(db.text("SELECT @@character_set_database, @@collation_database"))
            charset, collation = result.fetchone()
            print(f"\n✅ Charset de BD: {charset}")
            print(f"✅ Collation de BD: {collation}")
        except Exception as e:
            print(f"\n❌ Error al verificar charset: {e}")
        
        # Test 2: Verificar datos con caracteres especiales
        print("\n" + "=" * 60)
        print("👥 TRABAJADORES CON CARACTERES ESPECIALES")
        print("=" * 60)
        
        trabajadores = Trabajador.query.limit(10).all()
        
        for t in trabajadores:
            # Verificar si tiene caracteres especiales
            tiene_especiales = any(ord(c) > 127 for c in t.nombre if c)
            emoji = "🔤" if tiene_especiales else "📝"
            
            print(f"\n{emoji} ID {t.id}:")
            print(f"   Nombre: {t.nombre}")
            print(f"   Email: {t.email}")
            if hasattr(t, 'rol'):
                print(f"   Rol: {t.rol}")
            
            # Mostrar bytes si tiene caracteres especiales
            if tiene_especiales:
                print(f"   Bytes (nombre): {t.nombre.encode('utf-8')}")
        
        # Test 3: Crear texto con caracteres especiales
        print("\n" + "=" * 60)
        print("📝 TEST DE CARACTERES ESPECIALES")
        print("=" * 60)
        
        test_strings = [
            "Gestión de Permisos",
            "Cerrar Sesión",
            "Administración",
            "Configuración",
            "Año 2025",
            "Niño - Niña",
            "¡Hola! ¿Cómo estás?",
            "Español - ñ, á, é, í, ó, ú"
        ]
        
        for s in test_strings:
            print(f"   ✓ {s}")
            # Verificar que se codifica correctamente
            encoded = s.encode('utf-8')
            decoded = encoded.decode('utf-8')
            if s == decoded:
                print(f"      ✅ Codificación correcta")
            else:
                print(f"      ❌ Error en codificación")
        
        print("\n" + "=" * 60)
        print("✅ DIAGNÓSTICO COMPLETADO")
        print("=" * 60)

if __name__ == '__main__':
    test_encoding()
