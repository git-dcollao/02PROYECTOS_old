#!/usr/bin/env python3
"""
Script para agregar permisos de la página requerimientos_aceptar
al sistema de permisos dinámico
"""

import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import Page, PagePermission, UserRole, Category
from flask import Flask

def agregar_permisos_requerimientos_aceptar():
    """
    Agregar permisos para la página requerimientos_aceptar
    """
    app = create_app()
    
    with app.app_context():
        try:
            print("🔍 Verificando página 'requerimientos_aceptar'...")
            
            # Buscar la página
            pagina = Page.query.filter_by(route='/requerimientos_aceptar').first()
            
            if not pagina:
                print("❌ Página '/requerimientos_aceptar' no encontrada en la base de datos")
                print("   Ejecute primero las semillas (seeds) para crear las páginas")
                return False
            
            print(f"✅ Página encontrada: {pagina.name} (ID: {pagina.id})")
            
            # Verificar si ya existe permiso para SUPERADMIN
            permiso_existente = PagePermission.query.filter_by(
                page_id=pagina.id,
                system_role=UserRole.SUPERADMIN
            ).first()
            
            if permiso_existente:
                print("✅ El permiso SUPERADMIN ya existe para esta página")
                return True
            
            # Crear permiso para SUPERADMIN
            print("🔧 Creando permiso SUPERADMIN para requerimientos_aceptar...")
            
            nuevo_permiso = PagePermission(
                page_id=pagina.id,
                system_role=UserRole.SUPERADMIN,
                role_name=UserRole.SUPERADMIN.value
            )
            
            db.session.add(nuevo_permiso)
            db.session.commit()
            
            print("✅ Permiso SUPERADMIN creado exitosamente")
            
            # Verificar resultado
            total_permisos = PagePermission.query.filter_by(page_id=pagina.id).count()
            print(f"📊 Total de permisos para esta página: {total_permisos}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error al agregar permisos: {str(e)}")
            db.session.rollback()
            return False

def verificar_estado_permisos():
    """
    Verificar el estado actual de los permisos
    """
    app = create_app()
    
    with app.app_context():
        try:
            print("\n🔍 VERIFICACIÓN COMPLETA DEL SISTEMA DE PERMISOS")
            print("=" * 50)
            
            # Verificar página
            pagina = Page.query.filter_by(route='/requerimientos_aceptar').first()
            if pagina:
                print(f"✅ Página: {pagina.name}")
                print(f"   - Ruta: {pagina.route}")
                print(f"   - Categoría: {pagina.category.name if pagina.category else 'Sin categoría'}")
                print(f"   - Visible: {'Sí' if pagina.is_visible else 'No'}")
                print(f"   - Orden: {pagina.display_order}")
                
                # Verificar permisos
                permisos = PagePermission.query.filter_by(page_id=pagina.id).all()
                print(f"   - Permisos activos: {len(permisos)}")
                
                for permiso in permisos:
                    print(f"     * {permiso.role_name} (ID: {permiso.id})")
            else:
                print("❌ Página no encontrada")
                
            # Verificar categoría de requerimientos
            cat_req = Category.query.filter_by(name='Requerimiento').first()
            if cat_req:
                print(f"\n✅ Categoría 'Requerimiento': {len(cat_req.pages)} páginas")
                for p in cat_req.pages:
                    permisos_count = len(p.permissions)
                    print(f"   - {p.name}: {permisos_count} permisos")
            
        except Exception as e:
            print(f"❌ Error en verificación: {str(e)}")

if __name__ == "__main__":
    print("🚀 CONFIGURANDO PERMISOS PARA REQUERIMIENTOS ACEPTAR")
    print("=" * 55)
    
    # Agregar permisos
    if agregar_permisos_requerimientos_aceptar():
        print("\n✅ Configuración completada exitosamente")
        
        # Verificar estado final
        verificar_estado_permisos()
        
        print("\n🎯 PRÓXIMOS PASOS:")
        print("1. Reiniciar la aplicación Docker")
        print("2. Iniciar sesión como SUPERADMIN") 
        print("3. Navegar a http://localhost:5050/permissions/")
        print("4. Verificar que 'Requerimientos Aceptar' aparece en el menú")
        print("5. Probar la funcionalidad en http://localhost:5050/requerimientos_aceptar")
        
    else:
        print("\n❌ Error en la configuración")
        sys.exit(1)