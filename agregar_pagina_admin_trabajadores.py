#!/usr/bin/env python3
"""
Script para agregar la página de administración avanzada de trabajadores
solo para usuarios SUPERADMIN
"""
import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Category, Page, PagePermission, UserRole

def agregar_pagina_admin_trabajadores():
    """Agregar la página de administración avanzada de trabajadores"""
    print("🚀 Agregando página de administración avanzada de trabajadores...")
    
    try:
        # Buscar la categoría de usuarios
        categoria_usuarios = Category.query.filter_by(name='Usuarios').first()
        if not categoria_usuarios:
            print("❌ No se encontró la categoría 'Usuarios'")
            return False
        
        # Verificar si la página ya existe
        pagina_existente = Page.query.filter_by(route='/admin/trabajadores').first()
        if pagina_existente:
            print("⚠️ La página '/admin/trabajadores' ya existe")
            return True
        
        # Crear la nueva página
        pagina_admin = Page(
            route='/admin/trabajadores',
            name='Admin Trabajadores',
            description='Administración avanzada de trabajadores con múltiples áreas (solo SUPERADMIN)',
            category_id=categoria_usuarios.id,
            template_path='trabajadores_admin.html',
            active=True,
            display_order=10,  # Después de la página normal de trabajadores
            icon='fas fa-users-cog',
            is_visible=True,
            menu_group='admin'
        )
        
        db.session.add(pagina_admin)
        db.session.flush()  # Para obtener el ID
        
        # Crear permiso solo para SUPERADMIN
        permiso_superadmin = PagePermission(
            page_id=pagina_admin.id,
            system_role=UserRole.SUPERADMIN,
            role_name=UserRole.SUPERADMIN.value
        )
        
        db.session.add(permiso_superadmin)
        db.session.commit()
        
        print("✅ Página de administración avanzada de trabajadores creada exitosamente")
        print(f"   📄 Ruta: {pagina_admin.route}")
        print(f"   🏷️ Nombre: {pagina_admin.name}")
        print(f"   🔐 Permisos: Solo SUPERADMIN")
        print(f"   📁 Template: {pagina_admin.template_path}")
        
        return True
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error agregando página admin trabajadores: {e}")
        import traceback
        traceback.print_exc()
        return False

def verificar_paginas_trabajadores():
    """Verificar que ambas páginas de trabajadores estén configuradas correctamente"""
    print("\n🔍 Verificando páginas de trabajadores...")
    
    # Página normal de trabajadores
    pagina_normal = Page.query.filter_by(route='/trabajadores').first()
    if pagina_normal:
        permisos_normal = PagePermission.query.filter_by(page_id=pagina_normal.id).all()
        roles_normal = [p.role_name for p in permisos_normal]
        print(f"✅ Página normal '/trabajadores':")
        print(f"   📄 Nombre: {pagina_normal.name}")
        print(f"   🔐 Roles con acceso: {', '.join(roles_normal)}")
    else:
        print("❌ Página normal '/trabajadores' no encontrada")
    
    # Página admin de trabajadores
    pagina_admin = Page.query.filter_by(route='/admin/trabajadores').first()
    if pagina_admin:
        permisos_admin = PagePermission.query.filter_by(page_id=pagina_admin.id).all()
        roles_admin = [p.role_name for p in permisos_admin]
        print(f"✅ Página admin '/admin/trabajadores':")
        print(f"   📄 Nombre: {pagina_admin.name}")
        print(f"   🔐 Roles con acceso: {', '.join(roles_admin)}")
    else:
        print("❌ Página admin '/admin/trabajadores' no encontrada")

def mostrar_resumen_sistema():
    """Mostrar resumen del sistema de trabajadores"""
    print("\n📊 RESUMEN DEL SISTEMA DE TRABAJADORES")
    print("=" * 60)
    
    print("🔄 Funcionalidad implementada:")
    print("   ✅ Página normal (/trabajadores):")
    print("      - Restricción a UNA área por trabajador para no-SUPERADMIN")
    print("      - Acceso para ADMIN, ADMIN_AREA, USUARIO (según configuración)")
    print("   ✅ Página admin (/admin/trabajadores):")
    print("      - Gestión completa de múltiples áreas por trabajador")
    print("      - Solo acceso para SUPERADMIN")
    print("      - Estadísticas avanzadas y herramientas de gestión")
    
    print("\n🎯 URLs del sistema:")
    print("   📄 Trabajadores normal: http://localhost:5050/trabajadores")
    print("   🔧 Trabajadores admin: http://localhost:5050/admin/trabajadores")
    
    print("\n🔐 Control de acceso:")
    print("   👤 Usuarios normales: Solo una área por trabajador")
    print("   👑 SUPERADMIN: Múltiples áreas y gestión avanzada")

if __name__ == '__main__':
    app = create_app()
    
    with app.app_context():
        print("🚀 Configurando sistema avanzado de trabajadores...")
        print("=" * 60)
        
        try:
            # Agregar página admin
            if agregar_pagina_admin_trabajadores():
                # Verificar configuración
                verificar_paginas_trabajadores()
                
                # Mostrar resumen
                mostrar_resumen_sistema()
                
                print("\n" + "=" * 60)
                print("🎉 ¡Sistema de trabajadores configurado exitosamente!")
                print("💡 Ahora SUPERADMIN tiene acceso completo a gestión avanzada")
                
            else:
                print("❌ No se pudo configurar el sistema de trabajadores")
                
        except Exception as e:
            print(f"\n💥 Error durante la configuración: {str(e)}")
            import traceback
            traceback.print_exc()
            sys.exit(1)