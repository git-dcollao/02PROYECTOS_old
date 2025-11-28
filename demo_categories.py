#!/usr/bin/env python3
"""
🚀 DEMO RÁPIDA: Agregar Categorías y Modificar Permisos
========================================================

Este script demuestra todas las funcionalidades del sistema de permisos
"""

import subprocess
import sys

def run_command(command, description):
    """Ejecutar comando y mostrar resultado"""
    print(f"\n{'='*60}")
    print(f"🔧 {description}")
    print(f"{'='*60}")
    print(f"$ {command}")
    print()
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("ERROR:", result.stderr)
    except Exception as e:
        print(f"Error ejecutando comando: {e}")

def demo_complete():
    """Demostración completa del sistema"""
    
    print("🎯 DEMOSTRACIÓN COMPLETA DEL SISTEMA DE PERMISOS Y CATEGORÍAS")
    print("=" * 70)
    
    # 1. Ver estado actual
    run_command("python category_manager.py list-categories", 
                "Estado actual del sistema")
    
    # 2. Agregar nuevas categorías
    run_command('python category_manager.py add-category "Inventario"',
                "Agregar categoría Inventario")
    
    run_command('python category_manager.py add-category "Seguridad"',
                "Agregar categoría Seguridad")
    
    # 3. Agregar páginas en las nuevas categorías
    run_command('python category_manager.py add-page "inventory.products" "Productos" "Inventario" --roles SUPERADMIN ADMIN SUPERVISOR --description "Catálogo de productos y stock"',
                "Agregar página de productos")
    
    run_command('python category_manager.py add-page "inventory.suppliers" "Proveedores" "Inventario" --roles SUPERADMIN ADMIN --description "Gestión de proveedores"',
                "Agregar página de proveedores")
    
    run_command('python category_manager.py add-page "security.audit" "Auditoría" "Seguridad" --roles SUPERADMIN --description "Logs de auditoría del sistema"',
                "Agregar página de auditoría")
    
    # 4. Modificar permisos existentes
    run_command('python category_manager.py update-permissions "main.dashboard" --roles SUPERADMIN ADMIN SUPERVISOR USUARIO',
                "Dar acceso al dashboard a todos los roles")
    
    # 5. Ver resultado final
    run_command("python category_manager.py list-categories",
                "Estado final del sistema")
    
    run_command('python category_manager.py list-pages --category "Inventario"',
                "Ver páginas de Inventario")
    
    print("\n" + "="*70)
    print("✅ DEMOSTRACIÓN COMPLETADA")
    print("=" * 70)
    print()
    print("🌐 Para ver los cambios en la interfaz web:")
    print("   1. Accede a: http://localhost:5050/permissions/")
    print("   2. Login: admin@sistema.com / admin123")
    print("   3. Verás las nuevas categorías con sus colores")
    print()
    print("📖 Para más información consulta:")
    print("   - GUIA_PERMISOS_CATEGORIAS.md")
    print("   - category_manager.py --help")

if __name__ == "__main__":
    demo_complete()
