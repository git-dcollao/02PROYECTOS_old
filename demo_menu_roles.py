"""
Script de demostración del sistema de menús dinámicos por roles
"""

from app import create_app, db
from app.models import Trabajador, UserRole
from app.services.menu_service import menu_service
import json

def demo_menu_by_roles():
    """Demostrar cómo el menú cambia según el rol del usuario"""
    
    app = create_app()
    with app.app_context():
        
        print("🎭 DEMOSTRACIÓN DEL MENÚ DINÁMICO POR ROLES")
        print("=" * 60)
        
        # Crear usuarios de prueba con diferentes roles si no existen
        test_users = [
            {
                'email': 'supervisor@test.com',
                'nombre': 'Supervisor Test',
                'rol': UserRole.SUPERVISOR,
                'password': 'supervisor123'
            },
            {
                'email': 'usuario@test.com', 
                'nombre': 'Usuario Test',
                'rol': UserRole.USUARIO,
                'password': 'usuario123'
            }
        ]
        
        # Crear usuarios de prueba
        for user_data in test_users:
            existing_user = Trabajador.query.filter_by(email=user_data['email']).first()
            if not existing_user:
                user = Trabajador(
                    nombre=user_data['nombre'],
                    email=user_data['email'],
                    rol=user_data['rol'],
                    activo=True
                )
                user.password = user_data['password']
                db.session.add(user)
                print(f"✅ Usuario creado: {user_data['email']}")
            else:
                print(f"⚡ Usuario existente: {user_data['email']}")
        
        db.session.commit()
        
        # Obtener usuarios para demostración
        admin = Trabajador.query.filter_by(email='admin@test.com').first()
        supervisor = Trabajador.query.filter_by(email='supervisor@test.com').first()
        usuario = Trabajador.query.filter_by(email='usuario@test.com').first()
        
        users_to_demo = [
            ('ADMINISTRADOR', admin),
            ('SUPERVISOR', supervisor),
            ('USUARIO BÁSICO', usuario)
        ]
        
        # Demostrar menú por cada rol
        for role_name, user in users_to_demo:
            if not user:
                print(f"❌ No se encontró usuario para {role_name}")
                continue
            
            print(f"\n👤 MENÚ PARA {role_name}:")
            print(f"   📧 Email: {user.email}")
            print(f"   🎭 Rol: {user.rol.value}")
            print("-" * 50)
            
            menu = menu_service.get_user_menu(user)
            
            if not menu:
                print("   ❌ Sin acceso al menú")
                continue
            
            total_pages = 0
            
            for category in menu:
                print(f"\n   📁 {category['category']} ({category['count']} elementos)")
                
                for page in category['pages']:
                    print(f"      📄 {page['name']} → {page['url']}")
                    total_pages += 1
            
            print(f"\n   📊 Total páginas accesibles: {total_pages}")
        
        # Comparativa de acceso
        print(f"\n\n📊 COMPARATIVA DE ACCESO POR ROL:")
        print("=" * 60)
        
        comparison_routes = [
            '/dashboard',
            '/projects', 
            '/projects/create',
            '/projects/gantt',
            '/auth/users',
            '/permissions',
            '/custom-roles',
            '/reports/projects',
            '/settings'
        ]
        
        print(f"{'RUTA':<20} {'ADMIN':<8} {'SUPERVISOR':<12} {'USUARIO':<8}")
        print("-" * 60)
        
        for route in comparison_routes:
            admin_access = has_access(menu_service.get_user_menu(admin), route)
            supervisor_access = has_access(menu_service.get_user_menu(supervisor), route)
            usuario_access = has_access(menu_service.get_user_menu(usuario), route)
            
            print(f"{route:<20} {'✅' if admin_access else '❌':<8} {'✅' if supervisor_access else '❌':<12} {'✅' if usuario_access else '❌':<8}")
        
        # Resumen por rol
        print(f"\n\n📈 RESUMEN DE PERMISOS:")
        print("-" * 30)
        
        for role_name, user in users_to_demo:
            if user:
                menu = menu_service.get_user_menu(user)
                total = sum(cat['count'] for cat in menu) if menu else 0
                print(f"   {role_name:<15}: {total:>2} páginas")
        
        print(f"\n\n🎉 ¡Demostración completada!")
        print(f"\n🌐 Prueba el sistema:")
        print(f"   • Admin: admin@test.com / admin123")
        print(f"   • Supervisor: supervisor@test.com / supervisor123") 
        print(f"   • Usuario: usuario@test.com / usuario123")
        print(f"   • URL: http://localhost:5050/")

def has_access(menu, route):
    """Verificar si un menú incluye acceso a una ruta específica"""
    if not menu:
        return False
    
    for category in menu:
        for page in category.get('pages', []):
            if page.get('url') == route:
                return True
    return False

if __name__ == "__main__":
    try:
        demo_menu_by_roles()
    except Exception as e:
        print(f"\n💥 Error en la demostración: {e}")
        import traceback
        traceback.print_exc()
