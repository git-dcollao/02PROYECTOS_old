"""
Script para probar el filtrado de trabajadores por recinto
"""

from app import create_app
from app.models import Trabajador, Sector, Recinto, TipoRecinto

def probar_filtrado():
    app = create_app()
    
    with app.app_context():
        print("=== PRUEBA DE FILTRADO DE TRABAJADORES POR RECINTO ===\n")
        
        # Obtener trabajadores
        trabajadores = Trabajador.query.all()
        print(f"Total de trabajadores en BD: {len(trabajadores)}")
        
        # Mostrar información de cada trabajador
        for t in trabajadores:
            print(f"\nTrabajador: {t.nombre}")
            print(f"  - Email: {t.email}")
            print(f"  - Rol: {t.rol}")
            print(f"  - Sector ID: {t.sector_id}")
            print(f"  - Sector: {t.sector.nombre if t.sector else 'Sin sector'}")
            print(f"  - Recinto ID: {t.recinto_id}")
            print(f"  - Recinto: {t.recinto.nombre if t.recinto else 'Sin recinto'}")
            
            if t.recinto and t.recinto.tiporecinto:
                print(f"  - Tipo Recinto: {t.recinto.tiporecinto.nombre}")
        
        print("\n=== SIMULACIÓN DE FILTROS ===")
        
        # Simular filtro para SUPERADMIN
        superadmin = Trabajador.query.filter_by(rol='SUPERADMIN').first()
        if superadmin:
            print(f"\nSUPERADMIN ({superadmin.nombre}):")
            print(f"  - Ve todos los trabajadores: {len(trabajadores)}")
        
        # Simular filtro para usuarios normales
        usuarios_normales = Trabajador.query.filter(Trabajador.rol != 'SUPERADMIN').all()
        
        for usuario in usuarios_normales:
            if usuario.recinto_id:
                trabajadores_mismo_recinto = Trabajador.query.filter_by(recinto_id=usuario.recinto_id).all()
                print(f"\nUSUARIO ({usuario.nombre}) - Recinto {usuario.recinto.nombre if usuario.recinto else 'N/A'}:")
                print(f"  - Ve trabajadores del mismo recinto: {len(trabajadores_mismo_recinto)}")
                for t in trabajadores_mismo_recinto:
                    print(f"    * {t.nombre}")
            else:
                print(f"\nUSUARIO ({usuario.nombre}) - Sin recinto:")
                print(f"  - Solo se ve a sí mismo: 1 trabajador")
        
        print("\n=== ESTADÍSTICAS GENERALES ===")
        sectores = Sector.query.filter_by(activo=True).all()
        recintos = Recinto.query.filter_by(activo=True).all()
        
        print(f"Sectores activos: {len(sectores)}")
        for s in sectores:
            print(f"  - {s.nombre}")
        
        print(f"Recintos activos: {len(recintos)}")
        for r in recintos:
            tipo = r.tiporecinto.nombre if r.tiporecinto else 'Sin tipo'
            sector = r.tiporecinto.sector.nombre if r.tiporecinto and r.tiporecinto.sector else 'Sin sector'
            print(f"  - {r.nombre} (Tipo: {tipo}, Sector: {sector})")

if __name__ == "__main__":
    probar_filtrado()