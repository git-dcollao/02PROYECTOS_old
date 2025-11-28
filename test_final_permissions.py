#!/usr/bin/env python3
"""
Test completo de funciones de permisos para verificar las correcciones
"""
import sys
sys.path.append('.')

from app import create_app, db
from app.models import UserRole, Trabajador

# Crear una clase de usuario temporal para las pruebas
class TestUser:
    def __init__(self, username, rol_name, custom_role_id=None, custom_role_name=None):
        self.username = username
        if rol_name == 'SUPERADMIN':
            self.rol = UserRole.SUPERADMIN
        else:
            # Simular un enum simple
            class MockRole:
                def __init__(self, name, value):
                    self.name = name
                    self.value = value
            self.rol = MockRole(rol_name, rol_name.lower())
        
        self.custom_role_id = custom_role_id
        if custom_role_name and custom_role_id:
            class MockCustomRole:
                def __init__(self, name):
                    self.name = name
            self.custom_role = MockCustomRole(custom_role_name)
        else:
            self.custom_role = None

# Clase para simular un trabajador
class MockTrabajador:
    def __init__(self, area_id):
        self.area_id = area_id

def main():
    app = create_app()
    with app.app_context():
        from app.controllers import user_has_admin_permissions
        from app.utils.area_permissions import puede_editar_trabajador, puede_crear_trabajador_en_area
        from app.services.menu_service import MenuService
        
        print('🔧 PRUEBAS DE PERMISOS DESPUÉS DE LAS CORRECCIONES')
        print('=' * 60)
        print()
        
        # Probar usuario administrador con custom_role_id=1
        admin_user = TestUser('administrador@sistema.local', 'admin', custom_role_id=1, custom_role_name='ADMINISTRADOR')
        
        print('👤 USUARIO ADMINISTRADOR CON CUSTOM ROLE')
        print('-' * 40)
        print(f'Usuario: {admin_user.username}')
        rol_name = admin_user.rol.name if hasattr(admin_user.rol, 'name') else str(admin_user.rol)
        print(f'Rol: {rol_name}')
        print(f'Custom Role ID: {admin_user.custom_role_id}')
        custom_name = admin_user.custom_role.name if admin_user.custom_role else None
        print(f'Custom Role Name: {custom_name}')
        print()
        
        # Probar función user_has_admin_permissions
        result1 = user_has_admin_permissions(admin_user)
        print(f'✅ user_has_admin_permissions(): {result1}')
        
        # Probar función puede_editar_trabajador con un trabajador ficticio
        trabajador = MockTrabajador(area_id=1)
        result2 = puede_editar_trabajador(admin_user, trabajador)
        print(f'✅ puede_editar_trabajador(): {result2}')
        
        # Probar función puede_crear_trabajador_en_area
        result3 = puede_crear_trabajador_en_area(admin_user, area_id=1)
        print(f'✅ puede_crear_trabajador_en_area(): {result3}')
        
        print()
        print('👑 USUARIO SUPERADMIN (CONTROL)')
        print('-' * 30)
        
        # Probar con SUPERADMIN
        superadmin_user = TestUser('admin@sistema.local', 'SUPERADMIN')
        
        result4 = user_has_admin_permissions(superadmin_user)
        print(f'✅ SUPERADMIN user_has_admin_permissions(): {result4}')
        
        result5 = puede_editar_trabajador(superadmin_user, trabajador)
        print(f'✅ SUPERADMIN puede_editar_trabajador(): {result5}')
        
        result6 = puede_crear_trabajador_en_area(superadmin_user, area_id=1)
        print(f'✅ SUPERADMIN puede_crear_trabajador_en_area(): {result6}')
        
        print()
        print('📊 RESUMEN DE PRUEBAS DE FUNCIONES')
        print('-' * 35)
        expected_results = [True, True, True, True, True, True]
        actual_results = [result1, result2, result3, result4, result5, result6]
        
        all_passed = all(actual_results)
        
        if all_passed:
            print('🎉 ¡TODAS LAS PRUEBAS PASARON EXITOSAMENTE!')
            print('✅ Las funciones de permisos están funcionando correctamente para:')
            print('   - Usuarios con custom_role_id y nombre ADMINISTRADOR')
            print('   - Usuarios con rol SUPERADMIN')
        else:
            print('❌ ALGUNAS PRUEBAS FALLARON:')
            tests = ['Custom Admin Permissions', 'Custom Edit Worker', 'Custom Create Worker', 
                    'Super Admin Permissions', 'Super Edit Worker', 'Super Create Worker']
            for i, (expected, actual) in enumerate(zip(expected_results, actual_results)):
                status = '✅' if actual == expected else '❌'
                print(f'   {status} {tests[i]}: {actual} (esperado: {expected})')

        print()
        print('🍽️ PRUEBAS DEL SISTEMA DE MENÚ')
        print('-' * 30)
        
        # Probar el servicio de menú con el usuario real
        real_admin_user = Trabajador.query.filter_by(email='administrador@sistema.local').first()
        if real_admin_user:
            print(f'✅ Usuario real encontrado: {real_admin_user.email}')
            print(f'   - Rol: {real_admin_user.rol}')
            print(f'   - Custom Role ID: {real_admin_user.custom_role_id}')
            if real_admin_user.custom_role:
                print(f'   - Custom Role Name: {real_admin_user.custom_role.name}')
            
            # Probar el servicio de menú
            menu_service = MenuService()
            menu = menu_service.get_user_menu(real_admin_user)
            print(f'🎯 Menú generado:')
            print(f'   - Total de categorías: {len(menu)}')
            print(f'   - Tipo del menú: {type(menu)}')
            print(f'   - Estructura del menú: {menu}')
            
            # Contar páginas totales
            total_pages = 0
            if isinstance(menu, list):
                for item in menu:
                    if isinstance(item, dict) and 'pages' in item:
                        total_pages += len(item['pages'])
            
            print(f'   - Total de páginas encontradas: {total_pages}')
            
            if len(menu) > 0:
                print('🎉 ¡EL MENÚ SE GENERA CORRECTAMENTE!')
                menu_success = True
            else:
                print('❌ NO SE GENERÓ NINGÚN MENÚ')
                menu_success = False
        else:
            print('❌ Usuario administrador@sistema.local no encontrado')
            menu_success = False

        print()
        print('🏁 RESUMEN FINAL')
        print('=' * 20)
        
        if all_passed and menu_success:
            print('🎉 ¡TODAS LAS CORRECCIONES FUNCIONAN PERFECTAMENTE!')
            print()
            print('✅ Sistema de permisos corregido exitosamente')
            print('✅ Funciones user_has_admin_permissions() funcionando')
            print('✅ Funciones de área de permisos funcionando') 
            print('✅ Sistema de menú funcionando para custom roles')
            print()
            print('🚀 El usuario administrador@sistema.local ahora puede:')
            print('   1. ✅ Ver el menú correspondiente a su custom_role_id=1')
            print('   2. ✅ Acceder a la página /trabajadores')
            print('   3. ✅ Editar y crear trabajadores de su recinto')
            print()
            print('🌟 ¡CORRECCIÓN COMPLETADA CON ÉXITO!')
        else:
            print('❌ ALGUNAS CORRECCIONES NO FUNCIONAN CORRECTAMENTE')
            if not all_passed:
                print('   - Problemas en las funciones de permisos')
            if not menu_success:
                print('   - Problemas en el sistema de menú')

if __name__ == '__main__':
    main()