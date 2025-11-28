# -*- coding: utf-8 -*-
"""Script para diagnosticar el problema de /control_actividades"""

from app import create_app
from app.models import Page, PagePermission, CustomRole

app = create_app()

with app.app_context():
    # 1. Verificar si existe la página
    page = Page.query.filter_by(route='/control_actividades').first()
    
    if not page:
        print("❌ La página /control_actividades NO EXISTE en la tabla 'page'")
        print("\n🔍 Páginas con rutas similares:")
        similar = Page.query.filter(Page.route.like('%control%')).all()
        for p in similar:
            print(f"   - {p.route}: {p.name} (Activa: {p.active})")
    else:
        print(f"✅ Página encontrada:")
        print(f"   ID: {page.id}")
        print(f"   Nombre: {page.name}")
        print(f"   Ruta: {page.route}")
        print(f"   Activa: {page.active}")
        print(f"   Categoría: {page.category_id}")
        
        # 2. Verificar permisos
        permisos = PagePermission.query.filter_by(page_id=page.id).all()
        
        print(f"\n🔐 Permisos configurados ({len(permisos)}):")
        for perm in permisos:
            # Determinar el nombre del rol
            if perm.custom_role:
                role_name = perm.custom_role.name
            elif perm.role_name:
                role_name = perm.role_name
            else:
                role_name = f"ID:{perm.custom_role_id}"
            
            print(f"   - Rol: {role_name}")
            print(f"     custom_role_id: {perm.custom_role_id}")
            print(f"     role_name: {perm.role_name}")
        
        # 3. Verificar si SUPERADMIN tiene permisos
        superadmin = CustomRole.query.filter_by(name='SUPERADMIN').first()
        if superadmin:
            perm_sa = PagePermission.query.filter_by(
                page_id=page.id,
                role_id=superadmin.id
            ).first()
            
            if perm_sa:
                print(f"\n✅ SUPERADMIN tiene permisos:")
                print(f"   Lectura: {perm_sa.can_read}")
            else:
                print("\n❌ SUPERADMIN NO tiene permisos asignados para esta página")
