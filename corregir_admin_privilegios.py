#!/usr/bin/env python3
"""
Script para corregir privilegios del administrador
Asigna el rol ADMINISTRADOR al usuario administrador@sistema.local
"""

import os
import sys
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Añadir el directorio de la aplicación al path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

try:
    from app import create_app, db
    from app.models import Trabajador, CustomRole
    app = create_app()
    
    def verificar_y_corregir_admin():
        """Verifica y corrige los privilegios del administrador"""
        with app.app_context():
            try:
                print("🔍 Verificando usuario administrador...")
                
                # Buscar el usuario administrador
                admin_user = Trabajador.query.filter_by(email='administrador@sistema.local').first()
                
                if not admin_user:
                    print("❌ Usuario administrador@sistema.local no encontrado")
                    return False
                
                print(f"✅ Usuario encontrado: {admin_user.nombre} ({admin_user.email})")
                print(f"   • Rol actual: {admin_user.rol}")
                print(f"   • Custom Role ID: {admin_user.custom_role_id}")
                print(f"   • Es admin: {getattr(admin_user, 'is_admin', 'No definido')}")
                
                # Buscar el rol ADMINISTRADOR
                admin_role = CustomRole.query.filter_by(name='ADMINISTRADOR').first()
                
                if not admin_role:
                    print("❌ Rol ADMINISTRADOR no encontrado")
                    return False
                
                print(f"✅ Rol ADMINISTRADOR encontrado (ID: {admin_role.id})")
                
                # Verificar si ya tiene el rol correcto
                cambios_realizados = False
                
                if admin_user.custom_role_id != admin_role.id:
                    print(f"🔄 Asignando rol ADMINISTRADOR...")
                    admin_user.custom_role_id = admin_role.id
                    cambios_realizados = True
                
                if admin_user.rol != 'administrador':
                    print(f"🔄 Configurando rol de sistema como 'administrador'...")
                    admin_user.rol = 'administrador'
                    cambios_realizados = True
                
                # Verificar si tiene atributo is_admin y configurarlo
                if hasattr(admin_user, 'is_admin') and not admin_user.is_admin:
                    print(f"🔄 Activando flag is_admin...")
                    admin_user.is_admin = True
                    cambios_realizados = True
                elif not hasattr(admin_user, 'is_admin'):
                    print("ℹ️  Atributo is_admin no existe en el modelo")
                
                if cambios_realizados:
                    db.session.commit()
                    print("✅ Privilegios del administrador corregidos exitosamente")
                else:
                    print("ℹ️  El usuario ya tiene los privilegios correctos")
                
                # Verificar el estado final
                print("\n📊 Estado final del usuario:")
                print(f"   • Nombre: {admin_user.nombre}")
                print(f"   • Email: {admin_user.email}")
                print(f"   • Rol: {admin_user.rol}")
                print(f"   • Custom Role ID: {admin_user.custom_role_id}")
                print(f"   • Custom Role Name: {admin_role.name}")
                print(f"   • Es admin: {getattr(admin_user, 'is_admin', 'No definido')}")
                
                return True
                
            except Exception as e:
                print(f"❌ Error al corregir privilegios: {str(e)}")
                db.session.rollback()
                return False
    
    def listar_todos_los_usuarios():
        """Lista todos los usuarios del sistema con sus roles"""
        with app.app_context():
            try:
                print("\n👥 Lista de todos los usuarios del sistema:")
                print("=" * 80)
                
                usuarios = Trabajador.query.all()
                
                for usuario in usuarios:
                    custom_role = None
                    if usuario.custom_role_id:
                        custom_role = CustomRole.query.get(usuario.custom_role_id)
                    
                    print(f"• {usuario.nombre}")
                    print(f"  Email: {usuario.email}")
                    print(f"  Rol: {usuario.rol}")
                    print(f"  Custom Role: {custom_role.name if custom_role else 'Ninguno'}")
                    print(f"  Es admin: {getattr(usuario, 'is_admin', 'No definido')}")
                    print(f"  Activo: {usuario.activo}")
                    print("-" * 40)
                    
            except Exception as e:
                print(f"❌ Error al listar usuarios: {str(e)}")
    
    def main():
        """Función principal"""
        print("🚀 Iniciando corrección de privilegios del administrador")
        print("=" * 60)
        
        # Verificar y corregir privilegios
        if verificar_y_corregir_admin():
            print("\n✅ Corrección completada exitosamente")
        else:
            print("\n❌ Error en la corrección")
            return 1
        
        # Listar usuarios para verificar
        listar_todos_los_usuarios()
        
        print("\n🎉 Proceso completado")
        return 0
    
    if __name__ == "__main__":
        sys.exit(main())
        
except ImportError as e:
    print(f"❌ Error al importar dependencias: {e}")
    print("Asegúrate de que el archivo se ejecute desde el directorio del proyecto")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error inesperado: {e}")
    sys.exit(1)