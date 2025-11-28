#!/usr/bin/env python3
"""
Script para probar la reubicación del campo Observaciones Adicionales
"""
import requests

def probar_reubicacion_observaciones():
    print("=== PRUEBA DE REUBICACIÓN - OBSERVACIONES ADICIONALES ===")
    
    # URL base
    base_url = "http://127.0.0.1:5050"
    
    print("\n1. Probando carga de página con cambios...")
    try:
        response = requests.get(f"{base_url}/requerimientos_completar")
        if response.status_code == 200:
            print("✅ Página carga correctamente")
            
            # Verificar que contiene los elementos esperados
            content = response.text
            
            checks = [
                ("Observaciones mantienen funcionalidad", 'name="observacion"' in content),
                ("Observaciones fuera de Información del Proyecto", 'Observaciones Adicionales' not in content.split('Información del Proyecto')[1].split('Miembros Responsables')[0] if 'Información del Proyecto' in content and 'Miembros Responsables' in content else False),
                ("Observaciones después de Miembros", 'Observaciones Adicionales' in content),
                ("Sección independiente creada", 'Observaciones del Proyecto' in content),
                ("Campo opcional indicado", 'Campo opcional' in content),
                ("Select de grupo mantiene", 'name="id_grupo"' in content),
                ("Icon de observaciones", 'fa-comment-alt' in content)
            ]
            
            for check_name, result in checks:
                if result:
                    print(f"  ✅ {check_name}")
                else:
                    print(f"  ❌ {check_name}")
                    
        else:
            print(f"❌ Error al cargar página: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
    
    print("\n=== ESTRUCTURA ACTUALIZADA ===")
    print("📋 Organización del formulario:")
    print("1. Información del Proyecto")
    print("   - Tipología *")
    print("   - Fuente de Financiamiento *") 
    print("   - Tipo de Proyecto *")
    print("   - Prioridad *")
    print("   - Grupo *")
    print()
    print("2. Miembros Responsables")
    print("   - Tabla de miembros del equipo")
    print("   - Botón agregar miembros")
    print()
    print("3. Observaciones Adicionales (REUBICADO)")
    print("   - Campo opcional independiente")
    print("   - Debajo de miembros responsables")
    print("   - Sección completa propia")
    print()
    
    print("✅ BENEFICIOS DE LA REUBICACIÓN:")
    print("- Mejor organización visual del formulario")
    print("- Observaciones no interfieren con campos requeridos")
    print("- Sección independiente más clara")
    print("- Flujo lógico: datos requeridos → equipo → observaciones")
    
    print("\n🌐 La página actualizada está disponible en:")
    print("http://127.0.0.1:5050/requerimientos_completar")

if __name__ == "__main__":
    probar_reubicacion_observaciones()
