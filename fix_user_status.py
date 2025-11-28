#!/usr/bin/env python3
"""
Script para verificar y reactivar usuarios desactivados
"""
from app import create_app, db
from app.models import Trabajador, UserRole

def verificar_y_reactivar_usuarios():
    """Verificar estado de usuarios y reactivar cuentas importantes"""
    app = create_app()
    
    with app.app_context():
        print("🔍 Verificando estado de usuarios...")
        
        try:
            # Obtener todos los usuarios
            usuarios = Trabajador.query.all()
            
            print(f"📊 Total de usuarios encontrados: {len(usuarios)}")
            print("\n📋 Estado actual de usuarios:")
            print("-" * 60)
            
            usuarios_desactivados = []
            
            for usuario in usuarios:
                status = "✅ ACTIVO" if usuario.activo else "❌ DESACTIVADO"
                rol = usuario.rol.value if usuario.rol else "Sin rol"
                
                print(f"ID: {usuario.id:2} | {usuario.nombre:15} | {usuario.email or 'Sin email':25} | {rol:10} | {status}")
                
                if not usuario.activo:
                    usuarios_desactivados.append(usuario)
            
            print("-" * 60)
            
            # Reactivar usuarios importantes automáticamente
            usuarios_criticos = ['admin@sistema.com']
            reactivados = 0
            
            for usuario in usuarios_desactivados:
                if usuario.email in usuarios_criticos or usuario.rol in [UserRole.ADMIN, UserRole.SUPERADMIN]:
                    print(f"🔧 Reactivando usuario crítico: {usuario.nombre} ({usuario.email})")
                    usuario.activo = True
                    usuario.intentos_fallidos = 0
                    usuario.bloqueado_hasta = None
                    reactivados += 1
            
            if reactivados > 0:
                db.session.commit()
                print(f"✅ {reactivados} usuario(s) crítico(s) reactivado(s)")
            else:
                print("ℹ️  No hay usuarios críticos desactivados")
            
            # Mostrar resumen final
            if usuarios_desactivados:
                print(f"\n⚠️  Usuarios aún desactivados: {len(usuarios_desactivados) - reactivados}")
                for usuario in usuarios_desactivados:
                    if not usuario.activo:  # Solo mostrar los que siguen desactivados
                        print(f"   - {usuario.nombre} ({usuario.email or 'Sin email'})")
                        
                print("\n💡 Para reactivar manualmente desde la web:")
                print("   1. Login como administrador en http://localhost:5050/")
                print("   2. Ve a 'Usuarios' en el dashboard")
                print("   3. Haz clic en el botón 'activar' (ícono verde) junto al usuario")
            else:
                print("\n🎉 ¡Todos los usuarios están activos!")
                
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error al verificar usuarios: {e}")
            return False

def crear_usuario_emergencia():
    """Crear un usuario administrador de emergencia si no existe ninguno activo"""
    app = create_app()
    
    with app.app_context():
        try:
            # Verificar si hay algún administrador activo
            admin_activo = Trabajador.query.filter(
                Trabajador.rol.in_([UserRole.ADMIN, UserRole.SUPERADMIN]),
                Trabajador.activo == True
            ).first()
            
            if not admin_activo:
                print("🚨 ¡No hay administradores activos! Creando usuario de emergencia...")
                
                # Crear admin de emergencia
                admin_emergencia = Trabajador(
                    nombre='Admin Emergencia',
                    email='emergency@sistema.com',
                    profesion='Administrador de Emergencia',
                    nombrecorto='emergency',
                    rol=UserRole.ADMIN,
                    activo=True
                )
                admin_emergencia.password = 'Emergency123!'
                
                db.session.add(admin_emergencia)
                db.session.commit()
                
                print("✅ Usuario de emergencia creado:")
                print("   📧 Email: emergency@sistema.com")
                print("   🔐 Contraseña: Emergency123!")
                print("   ⚠️  ¡Cambia esta contraseña después de iniciar sesión!")
                
                return True
            else:
                print(f"✅ Administrador activo encontrado: {admin_activo.nombre} ({admin_activo.email})")
                return False
                
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error al crear usuario de emergencia: {e}")
            return False

if __name__ == '__main__':
    print("🛠️  Sistema de Gestión de Usuarios - Herramienta de Diagnóstico")
    print("=" * 70)
    
    # Verificar y reactivar usuarios
    print("\n🔍 PASO 1: Verificación de usuarios")
    verificar_y_reactivar_usuarios()
    
    # Crear usuario de emergencia si es necesario
    print("\n🚨 PASO 2: Verificación de administradores activos")
    crear_usuario_emergencia()
    
    print("\n" + "=" * 70)
    print("🎯 Proceso completado. Ahora puedes intentar el login nuevamente.")
    print("📌 Credenciales principales:")
    print("   Email: admin@sistema.com")
    print("   Contraseña: admin123")
