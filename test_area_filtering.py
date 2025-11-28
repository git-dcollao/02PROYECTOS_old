"""
Script para probar el filtrado por área en la nueva página requerimiento_ver
"""
from app import create_app
from app.models import Trabajador, Requerimiento, Sector, db

def test_area_filtering():
    app = create_app()
    with app.app_context():
        print("=== PRUEBA DE FILTRADO POR ÁREA ===")
        
        # 1. Verificar SUPERADMIN
        admin = Trabajador.query.filter_by(email='admin@sistema.local').first()
        print(f"\n1. Usuario SUPERADMIN: {admin.nombre}")
        print(f"   Área: {admin.area.nombre if admin.area else 'Sin área'}")
        print(f"   Es superadmin: {admin.is_superadmin()}")
        
        if admin.is_superadmin():
            reqs_admin = Requerimiento.query.filter_by(activo=True).all()
            print(f"   Ve todos los requerimientos: {len(reqs_admin)}")
        
        # 2. Verificar usuario con área SALUD
        user_salud = Trabajador.query.filter_by(email='usuario@sistema.local').first()
        if user_salud and user_salud.area:
            print(f"\n2. Usuario área {user_salud.area.nombre}: {user_salud.nombre}")
            
            # Aplicar mapeo de área a sectores
            area_sector_mapping = {
                'SALUD': ['SALUD'],
                'SECOPLAC': ['MUNICIPAL', 'EDUCACION', 'CEMENTERIO', 'OTRO'],
                'DOM': ['MUNICIPAL', 'CEMENTERIO'],
                'Administración': ['MUNICIPAL', 'SALUD', 'CEMENTERIO', 'EDUCACION', 'OTRO'],
                'SuperAdmin': ['MUNICIPAL', 'SALUD', 'CEMENTERIO', 'EDUCACION', 'OTRO']
            }
            
            area_nombre = user_salud.area.nombre
            sectores_permitidos = area_sector_mapping.get(area_nombre, [])
            print(f"   Sectores permitidos: {sectores_permitidos}")
            
            if sectores_permitidos:
                sectores_ids = [s.id for s in Sector.query.filter(Sector.nombre.in_(sectores_permitidos)).all()]
                reqs_filtrados = Requerimiento.query.filter(
                    Requerimiento.activo == True,
                    Requerimiento.id_sector.in_(sectores_ids)
                ).all()
                print(f"   Ve requerimientos filtrados: {len(reqs_filtrados)}")
                
                for req in reqs_filtrados:
                    print(f"     - {req.nombre} (Sector: {req.sector.nombre})")
        
        # 3. Mostrar todos los requerimientos por sector
        print(f"\n3. Distribución de requerimientos por sector:")
        sectores = Sector.query.all()
        for sector in sectores:
            count = Requerimiento.query.filter_by(activo=True, id_sector=sector.id).count()
            print(f"   {sector.nombre}: {count} requerimientos")

if __name__ == "__main__":
    test_area_filtering()
