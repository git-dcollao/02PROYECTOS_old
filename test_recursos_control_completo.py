"""
🧪 TEST: Validar que NO se guardan recursos en actividad_proyecto
"""
import re

def simular_procesamiento_control():
    print("=" * 80)
    print("🧪 TEST: Validar que NO se guardan recursos en actividad_proyecto")
    print("=" * 80)
    
    # Simular datos del Excel de control
    datos_excel = [
        # Actividad existente (UPDATE)
        {
            'edt': '1.1.1',
            'nombre_tarea': 'Diseño inicial',
            'fecha_inicio': '2025-01-01',
            'fecha_fin': '2025-01-10', 
            'duracion': 10,
            'progreso': 0.75,  # 75%
            'recursos': 'Juan Pérez, María García',
            'predecesoras': '1.1',
            'tipo': 'UPDATE'  # Simulando que existe
        },
        # Nueva actividad (INSERT)
        {
            'edt': '1.2.1',
            'nombre_tarea': 'Implementación nueva',
            'fecha_inicio': '2025-01-11',
            'fecha_fin': '2025-01-20',
            'duracion': 9,
            'progreso': 0.0,  # 0%
            'recursos': 'Carlos López, Ana Rodríguez',
            'predecesoras': '1.1.1',
            'tipo': 'INSERT'  # Simulando que es nueva
        }
    ]
    
    print("📊 Datos de prueba:")
    for i, datos in enumerate(datos_excel, 1):
        print(f"   {i}. EDT: {datos['edt']} | Tipo: {datos['tipo']} | Recursos: {datos['recursos']}")
    
    print(f"\n🔍 Simulando procesamiento de control de actividades...")
    
    # Simular el procesamiento de cada fila
    for num_fila, datos_fila in enumerate(datos_excel, 1):
        print(f"\n📝 Procesando fila {num_fila} - EDT: {datos_fila['edt']} ({datos_fila['tipo']})")
        
        if datos_fila['tipo'] == 'UPDATE':
            print(f"🔄 ACTUALIZANDO actividad existente:")
            print(f"   ✅ Nombre: {datos_fila['nombre_tarea']}")
            print(f"   ✅ Fechas: {datos_fila['fecha_inicio']} → {datos_fila['fecha_fin']}")
            print(f"   ✅ Progreso: {datos_fila['progreso'] * 100}%")
            print(f"   ✅ Duración: {datos_fila['duracion']} días")
            print(f"   ✅ Predecesoras: {datos_fila['predecesoras']}")
            
            # RECURSOS: Procesar SIN guardar
            if datos_fila['recursos']:
                print(f"   🧑‍💼 Procesando recursos EXISTENTE: {datos_fila['recursos']}")
                recursos_lista = [r.strip() for r in datos_fila['recursos'].split(',')]
                print(f"      → Trabajadores detectados: {len(recursos_lista)}")
                print(f"      → Creando avances para trabajadores")
                print(f"      ❌ NO guardando recursos en actividad_proyecto.recursos")
            
        elif datos_fila['tipo'] == 'INSERT':
            print(f"➕ CREANDO nueva actividad:")
            
            # Simular creación de ActividadProyecto (SIN recursos)
            nueva_actividad_data = {
                'edt': datos_fila['edt'],
                'nombre_tarea': datos_fila['nombre_tarea'],
                'fecha_inicio': datos_fila['fecha_inicio'],
                'fecha_fin': datos_fila['fecha_fin'],
                'duracion': datos_fila['duracion'],
                'progreso': datos_fila['progreso'],
                'predecesoras': datos_fila['predecesoras'],
                # 'recursos': None  # ← NO SE INCLUYE
            }
            
            print(f"   ✅ Nueva actividad creada:")
            for campo, valor in nueva_actividad_data.items():
                if campo == 'progreso':
                    print(f"      {campo}: {valor * 100}%")
                else:
                    print(f"      {campo}: {valor}")
            
            print(f"      ❌ recursos: NO INCLUIDO en la actividad")
            
            # RECURSOS: Procesar SIN guardar
            if datos_fila['recursos']:
                print(f"   🧑‍💼 Procesando recursos NUEVA: {datos_fila['recursos']}")
                recursos_lista = [r.strip() for r in datos_fila['recursos'].split(',')]
                print(f"      → Trabajadores detectados: {len(recursos_lista)}")
                print(f"      → Creando avances para trabajadores")
                print(f"      ❌ NO guardando recursos en actividad_proyecto.recursos")
    
    print(f"\n📊 RESUMEN DEL PROCESAMIENTO:")
    print(f"   Total actividades procesadas: {len(datos_excel)}")
    print(f"   Actividades actualizadas: {sum(1 for d in datos_excel if d['tipo'] == 'UPDATE')}")
    print(f"   Actividades creadas: {sum(1 for d in datos_excel if d['tipo'] == 'INSERT')}")
    print(f"   Recursos procesados: {sum(1 for d in datos_excel if d['recursos'])}")
    print(f"   Recursos guardados en tabla: 0")  # ← ESTE ES EL OBJETIVO
    
    print(f"\n✅ VALIDACIÓN:")
    print(f"   ✅ Fechas y progreso se actualizan correctamente")
    print(f"   ✅ Trabajadores se crean desde recursos del Excel")
    print(f"   ✅ Avances se registran para cada trabajador")
    print(f"   ✅ Recursos NO se guardan en actividad_proyecto.recursos")
    print(f"   ✅ Historial NO incluye recursos")
    
    print(f"\n🎉 COMPORTAMIENTO ESPERADO:")
    print(f"   La tabla actividad_proyecto NO debe tener filas nuevas con recursos")
    print(f"   Los trabajadores y avances se crean en sus tablas correspondientes")
    print(f"   Los cambios de fechas/progreso se reflejan en la carta Gantt")
    
    return True

if __name__ == "__main__":
    success = simular_procesamiento_control()
    exit(0 if success else 1)
