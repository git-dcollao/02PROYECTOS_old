"""
Script para diagnosticar la generación del menú para un usuario específico
Ejecutar: python diagnostico_menu.py
"""

from app import create_app, db
from app.models import Trabajador
from app.services.menu_service import menu_service

def diagnosticar_menu():
    app = create_app()
    
    with app.app_context():
        print("\n" + "="*80)
        print("🔍 DIAGNÓSTICO DE GENERACIÓN DE MENÚ")
        print("="*80 + "\n")
        
        # Buscar usuario admin@sistema.local
        usuario = Trabajador.query.filter_by(email='admin@sistema.local').first()
        
        if not usuario:
            print("❌ Usuario admin@sistema.local no encontrado")
            return
        
        print(f"📋 Usuario: {usuario.nombre}")
        print(f"📧 Email: {usuario.email}")
        print(f"🔑 Rol: {usuario.rol.value if usuario.rol else 'Sin rol'}")
        print(f"🎭 Custom Role ID: {usuario.custom_role_id}")
        print(f"✅ Es SUPERADMIN: {usuario.is_superadmin()}")
        print(f"🔓 Activo: {usuario.activo}")
        
        print("\n" + "-"*80)
        print("📊 GENERANDO MENÚ...")
        print("-"*80 + "\n")
        
        # Generar menú
        menu = menu_service.get_user_menu(usuario)
        
        if not menu:
            print("❌ No se generó menú para este usuario")
            return
        
        print(f"✅ Menú generado con {len(menu)} categorías\n")
        
        total_pages = 0
        for categoria in menu:
            cat_name = categoria['category']
            cat_icon = categoria['icon']
            pages_count = len(categoria['pages'])
            total_pages += pages_count
            
            print(f"\n📁 {cat_icon} {cat_name} ({pages_count} páginas)")
            print("   " + "-"*60)
            
            for page in categoria['pages']:
                icon = page['icon']
                name = page['name']
                url = page['url']
                children_count = len(page.get('children', []))
                
                if children_count > 0:
                    print(f"   {icon} {name} → {url} ({children_count} subpáginas)")
                    for child in page['children']:
                        print(f"      ↳ {child['icon']} {child['name']} → {child['url']}")
                else:
                    print(f"   {icon} {name} → {url}")
        
        print("\n" + "="*80)
        print(f"📊 RESUMEN: {len(menu)} categorías | {total_pages} páginas principales")
        print("="*80 + "\n")

if __name__ == '__main__':
    diagnosticar_menu()
