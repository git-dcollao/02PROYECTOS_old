"""
Script para asignar recintos a trabajadores existentes para probar el filtrado
"""

from app import create_app
from app.models import Trabajador, Sector, Recinto, TipoRecinto, db

def asignar_recintos():
    app = create_app()
    
    with app.app_context():
        print("=== ASIGNANDO RECINTOS A TRABAJADORES ===\n")
        
        # Obtener recintos disponibles
        recintos = Recinto.query.filter_by(activo=True).all()
        print("Recintos disponibles:")
        for r in recintos:
            print(f"  - ID {r.id}: {r.nombre} ({r.tiporecinto.sector.nombre if r.tiporecinto and r.tiporecinto.sector else 'Sin sector'})")
        
        # Asignar recintos específicos a usuarios de prueba (sin modificar roles)
        asignaciones = [
            {'email': 'administrador@sistema.local', 'recinto_id': 1},  # CESFAM La Tortuga
            {'email': 'control@sistema.local', 'recinto_id': 2},        # CECOSF El Boro
            {'email': 'usuario@sistema.local', 'recinto_id': 3},        # SAPU Dr. Héctor Reyno
            {'email': 'solicitante@sistema.local', 'recinto_id': 4},    # Oficinas DEPSA
        ]
        
        for asignacion in asignaciones:
            trabajador = Trabajador.query.filter_by(email=asignacion['email']).first()
            if trabajador:
                recinto = Recinto.query.get(asignacion['recinto_id'])
                if recinto:
                    trabajador.recinto_id = asignacion['recinto_id']
                    # También asignar el sector correspondiente
                    if recinto.tiporecinto and recinto.tiporecinto.sector:
                        trabajador.sector_id = recinto.tiporecinto.sector.id
                    
                    print(f"✅ Asignado {trabajador.nombre} -> {recinto.nombre} (Sector: {recinto.tiporecinto.sector.nombre if recinto.tiporecinto and recinto.tiporecinto.sector else 'N/A'})")
                else:
                    print(f"❌ No se encontró recinto ID {asignacion['recinto_id']}")
            else:
                print(f"❌ No se encontró trabajador con email {asignacion['email']}")
        
        # Guardar cambios
        try:
            db.session.commit()
            print("\n✅ Cambios guardados exitosamente")
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error al guardar cambios: {e}")
        
        print("\n=== RESUMEN FINAL ===")
        trabajadores = Trabajador.query.all()
        for t in trabajadores:
            if t.recinto_id:
                print(f"{t.nombre} ({t.email}) -> {t.recinto.nombre} - Sector: {t.sector.nombre if t.sector else 'N/A'} - Rol: {t.rol}")

if __name__ == "__main__":
    asignar_recintos()