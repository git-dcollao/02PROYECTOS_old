from app import create_app
from app.models import AdministradorRecinto, Trabajador
from flask_login import login_user

app = create_app()

with app.app_context():
    try:
        print('🔍 Simulando controlador gestion_administradores...')
        
        # Simular obtener el usuario admin como current_user
        admin_user = Trabajador.query.filter_by(email='admin@sistema.local').first()
        if not admin_user:
            print('❌ Usuario admin no encontrado')
        else:
            print(f'✅ Usuario encontrado: {admin_user.nombre}')
            print(f'🔐 Rol: {admin_user.rol.name if admin_user.rol else "Sin rol"}')
            
            # Verificar permisos como en el controlador
            if not (hasattr(admin_user, 'rol') and admin_user.rol and admin_user.rol.name == 'SUPERADMIN'):
                print('❌ ERROR: Usuario no tiene permisos SUPERADMIN')
            else:
                print('✅ Usuario tiene permisos SUPERADMIN')
                
                # Probar obtener matriz
                administradores, estructura, asignaciones = AdministradorRecinto.obtener_matriz_completa()
                
                # Calcular estadísticas como en el controlador
                total_administradores = len(administradores)
                total_recintos = sum(len(recintos) for sector_tipos in estructura.values() 
                                   for recintos in sector_tipos.values())
                total_asignaciones = sum(len(asignaciones_admin) for asignaciones_admin in asignaciones.values())
                
                print(f'📊 Total administradores: {total_administradores}')
                print(f'📊 Total recintos: {total_recintos}')
                print(f'📊 Total asignaciones: {total_asignaciones}')
                
                print('✅ Simulación del controlador exitosa - No debería haber errores')
    
    except Exception as e:
        print(f'❌ ERROR en simulación: {e}')
        import traceback
        traceback.print_exc()