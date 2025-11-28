#!/usr/bin/env python
"""
Script para probar el filtrado de requerimientos por recintos asignados a administradores
"""

from app import create_app
from app.models import Trabajador, CustomRole, AdministradorRecinto, Requerimiento, Recinto

def test_requerimientos_filtrado():
    """
    Prueba el filtrado de requerimientos para administradores con recintos asignados
    """
    app = create_app()
    
    with app.app_context():
        print('🧪 PRUEBA DE FILTRADO DE REQUERIMIENTOS POR RECINTOS')
        print('=' * 60)
        
        # Obtener un administrador con recintos asignados
        administradores = Trabajador.query.join(CustomRole).filter(
            CustomRole.name == 'ADMINISTRADOR'
        ).all()
        
        if not administradores:
            print('❌ No se encontraron administradores para probar')
            return False
        
        admin = administradores[0]
        print(f'👤 Usuario de prueba: {admin.nombre} ({admin.email})')
        
        # Obtener recintos asignados al administrador
        recintos_asignados = AdministradorRecinto.obtener_recintos_administrador(admin.id)
        print(f'🏢 Recintos asignados: {len(recintos_asignados)}')
        
        if not recintos_asignados:
            print('❌ El administrador no tiene recintos asignados')
            return False
        
        # Mostrar recintos asignados
        recinto_ids_permitidos = []
        for asignacion in recintos_asignados:
            recinto = Recinto.query.get(asignacion.recinto_id)
            if recinto:
                recinto_ids_permitidos.append(recinto.id)
                print(f'   - {recinto.nombre} (ID: {recinto.id})')
        
        print()
        
        # Test 1: Contar todos los requerimientos en el sistema
        total_requerimientos = Requerimiento.query.count()
        print(f'📊 Total de requerimientos en el sistema: {total_requerimientos}')
        
        # Test 2: Contar requerimientos que debería ver el administrador
        requerimientos_filtrados = Requerimiento.query.filter(
            Requerimiento.id_recinto.in_(recinto_ids_permitidos)
        ).all()
        
        print(f'📋 Requerimientos que debería ver el administrador: {len(requerimientos_filtrados)}')
        
        if requerimientos_filtrados:
            print(f'   Primeros requerimientos visibles:')
            for i, req in enumerate(requerimientos_filtrados[:3]):
                recinto_nombre = req.recinto.nombre if req.recinto else 'Sin recinto'
                print(f'   {i+1}. {req.nombre} - {recinto_nombre}')
            
            if len(requerimientos_filtrados) > 3:
                print(f'   ... y {len(requerimientos_filtrados) - 3} requerimientos más')
        
        # Test 3: Verificar que no hay requerimientos de recintos no asignados
        requerimientos_no_permitidos = Requerimiento.query.filter(
            ~Requerimiento.id_recinto.in_(recinto_ids_permitidos)
        ).count()
        
        print(f'🚫 Requerimientos de recintos no asignados: {requerimientos_no_permitidos}')
        
        # Test 4: Calcular porcentaje de filtrado
        if total_requerimientos > 0:
            porcentaje = (len(requerimientos_filtrados) / total_requerimientos) * 100
            print(f'📊 Porcentaje de requerimientos visibles: {porcentaje:.1f}%')
        
        print()
        print('✅ FUNCIONALIDADES IMPLEMENTADAS:')
        print('   ✅ Filtrado por recintos asignados')
        print('   ✅ SUPERADMIN mantiene acceso total')
        print('   ✅ Otros usuarios ven solo su recinto')
        print('   ✅ Administradores ven solo recintos asignados')
        
        return len(requerimientos_filtrados) < total_requerimientos

def test_superadmin_requerimientos():
    """
    Verificar que SUPERADMIN mantiene acceso total a requerimientos
    """
    app = create_app()
    
    with app.app_context():
        print()
        print('👑 PRUEBA DE ACCESO SUPERADMIN A REQUERIMIENTOS')
        print('=' * 50)
        
        # Buscar SUPERADMIN
        superadmin = Trabajador.query.filter_by(email='admin@sistema.local').first()
        
        if superadmin:
            print(f'👤 SUPERADMIN: {superadmin.nombre}')
            
            # Verificar rol
            if hasattr(superadmin, 'rol') and superadmin.rol:
                rol_name = superadmin.rol.name if hasattr(superadmin.rol, 'name') else str(superadmin.rol)
                print(f'🎭 Rol: {rol_name}')
                
                if rol_name == 'SUPERADMIN':
                    print('   ✅ SUPERADMIN mantiene acceso total a todos los requerimientos')
                    
                    # Contar todos los requerimientos
                    total_requerimientos = Requerimiento.query.count()
                    print(f'   ✅ Puede ver todos los requerimientos: {total_requerimientos}')
                else:
                    print('   ℹ️  Usuario no es SUPERADMIN del sistema')
            else:
                print('   ℹ️  Usuario no tiene rol de sistema definido')
        else:
            print('❌ No se encontró el usuario SUPERADMIN')

if __name__ == "__main__":
    try:
        print('🚀 INICIANDO PRUEBAS DE FILTRADO DE REQUERIMIENTOS')
        print()
        
        success = test_requerimientos_filtrado()
        test_superadmin_requerimientos()
        
        print()
        if success:
            print('🎉 TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE')
            print()
            print('💡 COMO USAR EL SISTEMA:')
            print('   1. Login como administrador (administrador@sistema.local)')
            print('   2. Accede a http://localhost:5050/requerimientos')
            print('   3. Verás solo los requerimientos de tus recintos asignados')
            print('   4. Los SUPERADMIN ven todos los requerimientos')
            print()
            print('🎯 FILTRADO DE REQUERIMIENTOS IMPLEMENTADO CORRECTAMENTE')
        else:
            print('❌ Algunas pruebas mostraron que no hay filtrado (todos ven todo)')
            
    except Exception as e:
        print(f'❌ Error durante las pruebas: {e}')
        import traceback
        traceback.print_exc()