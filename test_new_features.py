"""
Script para probar las nuevas funcionalidades del modal de requerimientos:
1. Fecha por defecto (hoy)
2. Guardado del área del solicitante
"""
from app import create_app
from app.models import Requerimiento, Area, Trabajador
from datetime import datetime

def test_new_features():
    app = create_app()
    with app.app_context():
        print("=== PRUEBA DE NUEVAS FUNCIONALIDADES ===")
        
        # 1. Verificar requerimientos existentes con área
        print("\n1. Requerimientos existentes con área:")
        reqs = Requerimiento.query.filter_by(activo=True).all()
        for req in reqs:
            area_nombre = req.area_solicitante.nombre if req.area_solicitante else "Sin área"
            print(f"   - {req.nombre}: {area_nombre}")
        
        # 2. Verificar áreas disponibles
        print("\n2. Áreas disponibles:")
        areas = Area.query.filter_by(activo=True).all()
        for area in areas:
            print(f"   - {area.nombre} (ID: {area.id})")
        
        # 3. Verificar usuarios y sus áreas
        print("\n3. Usuarios y sus áreas:")
        users = Trabajador.query.filter_by(activo=True).all()
        for user in users:
            area_nombre = user.area.nombre if user.area else "Sin área"
            es_superadmin = user.is_superadmin()
            print(f"   - {user.nombre}: {area_nombre} {'(SUPERADMIN)' if es_superadmin else ''}")
        
        # 4. Simular asignación de área para SUPERADMIN
        print("\n4. Lógica de asignación de área:")
        admin = Trabajador.query.filter_by(email='admin@sistema.local').first()
        if admin:
            if admin.is_superadmin():
                area_secoplac = Area.query.filter_by(nombre='SECOPLAC').first()
                area_asignada = area_secoplac.nombre if area_secoplac else "SECOPLAC no encontrada"
                print(f"   - SUPERADMIN se asignaría a: {area_asignada}")
            else:
                area_asignada = admin.area.nombre if admin.area else "Sin área"
                print(f"   - Usuario normal usaría: {area_asignada}")
        
        # 5. Fecha de hoy
        print(f"\n5. Fecha de hoy para formulario: {datetime.now().strftime('%Y-%m-%d')}")

if __name__ == "__main__":
    test_new_features()
