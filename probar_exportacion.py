#!/usr/bin/env python3
"""
Script para probar la funcionalidad de exportación de actividades a Excel
"""
import sys
import os

# Agregar el directorio del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import ActividadProyecto, Requerimiento

def probar_exportacion_actividades():
    """Verificar los datos que se exportarán a Excel"""
    app = create_app()
    
    with app.app_context():
        try:
            # Obtener todas las actividades activas
            actividades = ActividadProyecto.query.filter_by(activo=True).order_by(
                ActividadProyecto.requerimiento_id,
                ActividadProyecto.edt
            ).all()
            
            if not actividades:
                print("⚠️ No hay actividades para exportar")
                return False
            
            print(f"📊 Actividades encontradas para exportar: {len(actividades)}")
            print("=" * 140)
            print(f"{'ID':<5} {'Nivel':<7} {'EDT':<10} {'Nombre de tarea':<40} {'Duración':<10} {'Inicio':<12} {'Fin':<12} {'Recursos':<15}")
            print("=" * 140)
            
            for actividad in actividades[:10]:  # Mostrar solo las primeras 10
                fecha_inicio = actividad.fecha_inicio.strftime('%d/%m/%Y') if actividad.fecha_inicio else 'N/A'
                fecha_fin = actividad.fecha_fin.strftime('%d/%m/%Y') if actividad.fecha_fin else 'N/A'
                nombre_corto = (actividad.nombre_tarea[:37] + '...') if len(actividad.nombre_tarea or '') > 40 else (actividad.nombre_tarea or '')
                recursos_corto = (actividad.recursos[:12] + '...') if len(actividad.recursos or '') > 15 else (actividad.recursos or '')
                
                print(f"{actividad.id:<5} {actividad.nivel_esquema or 1:<7} {actividad.edt or '':<10} {nombre_corto:<40} {actividad.duracion or 0:<10} {fecha_inicio:<12} {fecha_fin:<12} {recursos_corto:<15}")
            
            if len(actividades) > 10:
                print(f"... y {len(actividades) - 10} actividades más")
            
            print("=" * 140)
            
            # Estadísticas por proyecto
            proyectos_stats = {}
            for actividad in actividades:
                req_id = actividad.requerimiento_id
                if req_id not in proyectos_stats:
                    req = Requerimiento.query.get(req_id)
                    proyectos_stats[req_id] = {
                        'nombre': req.nombre if req else f'Proyecto {req_id}',
                        'total_actividades': 0
                    }
                proyectos_stats[req_id]['total_actividades'] += 1
            
            print(f"\n📋 Distribución por proyecto:")
            for req_id, stats in proyectos_stats.items():
                print(f"   - {stats['nombre']}: {stats['total_actividades']} actividades")
            
            print(f"\n✅ Columnas que se exportarán:")
            columnas = [
                'Id', 'Nivel de esquema', 'EDT', 'Nombre de tarea', 
                'Duración', 'Comienzo', 'Fin', 'Predecesoras', 'Nombres de los recursos'
            ]
            for i, col in enumerate(columnas, 1):
                print(f"   {i}. {col}")
            
            print(f"\n🌐 Endpoint disponible en: http://127.0.0.1:5050/exportar_actividades_xlsx")
            print(f"🌐 Página disponible en: http://127.0.0.1:5050/control_actividades")
            
            return True
                
        except Exception as e:
            print(f"❌ Error al verificar datos: {str(e)}")
            return False

if __name__ == "__main__":
    if probar_exportacion_actividades():
        print("\n🎉 Verificación completada exitosamente")
    else:
        print("\n💥 Verificación fallida")
        sys.exit(1)
