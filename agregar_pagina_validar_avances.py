"""
Script para agregar la página de Validación de Avances al sistema de permisos
Ejecutar: python agregar_pagina_validar_avances.py
"""

from app import create_app, db
from app.models import Page, Category, PagePermission

def agregar_pagina_validar_avances():
    app = create_app()
    
    with app.app_context():
        print("🚀 Agregando página 'Validación de Avances' al sistema de permisos...")
        
        try:
            # Verificar si la página ya existe
            pagina_existente = Page.query.filter_by(route='/validar-avances').first()
            
            if pagina_existente:
                print(f"⚠️  La página '/validar-avances' ya existe con ID: {pagina_existente.id}")
                return
            
            # Buscar categoría (buscando una existente del sistema)
            categoria = Category.query.filter_by(name='Proyectos').first()
            
            if not categoria:
                print("⚠️  Categoría 'Proyectos' no encontrada, usando categoría por defecto...")
                # Usar una categoría existente o crear una
                categoria = Category.query.first()
                if not categoria:
                    print("❌ No hay categorías en el sistema")
                    return
            
            # Crear nueva página
            nueva_pagina = Page(
                name='Validación de Avances',
                route='/validar-avances',
                description='Validación supervisada de avances reportados por trabajadores',
                icon='fas fa-check-double',
                category_id=categoria.id,
                active=True,
                is_visible=True,
                display_order=30,
                template_path='validar-avances.html'
            )
            
            db.session.add(nueva_pagina)
            db.session.flush()
            
            print(f"✅ Página 'Validación de Avances' creada con ID: {nueva_pagina.id}")
            
            # Crear permisos para roles personalizados que deben tener acceso
            # SUPERADMIN tiene acceso automático a todas las páginas
            # Aquí asignamos a roles personalizados: ADMIN y CONTROL
            
            from app.models import CustomRole
            
            roles_con_acceso = ['ADMIN', 'CONTROL']
            permisos_creados = 0
            
            for role_name in roles_con_acceso:
                custom_role = CustomRole.query.filter_by(name=role_name).first()
                
                if custom_role:
                    # Verificar si ya existe el permiso
                    permiso_existente = PagePermission.query.filter_by(
                        page_id=nueva_pagina.id,
                        custom_role_id=custom_role.id
                    ).first()
                    
                    if not permiso_existente:
                        permiso = PagePermission(
                            page_id=nueva_pagina.id,
                            custom_role_id=custom_role.id,
                            role_name=custom_role.name
                        )
                        db.session.add(permiso)
                        permisos_creados += 1
                        print(f"✅ Permiso creado para rol '{role_name}'")
                    else:
                        print(f"⚠️  Permiso para rol '{role_name}' ya existe")
                else:
                    print(f"⚠️  Rol '{role_name}' no encontrado")
            
            print(f"✅ Total de permisos creados: {permisos_creados}")
            
            db.session.commit()
            
            print("\n" + "="*60)
            print("🎉 Página 'Validación de Avances' agregada exitosamente")
            print("="*60)
            print(f"📄 Página ID: {nueva_pagina.id}")
            print(f"🔗 Ruta: /validar-avances")
            print(f"📁 Categoría: {categoria.name}")
            print(f"🔑 Permisos creados: {permisos_creados}")
            print("\n⚙️  Próximos pasos:")
            print("   1. Los roles SUPERADMIN, ADMIN y CONTROL ya tienen acceso")
            print("   2. Para otros roles, ir a /permissions/ en la aplicación")
            print("   3. Verificar acceso con usuarios de prueba")
            print("="*60)
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error al agregar la página: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    agregar_pagina_validar_avances()
