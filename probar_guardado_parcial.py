#!/usr/bin/env python3
"""
Script para probar el guardado parcial después de corregir la validación
"""
import requests

def probar_guardado_parcial():
    print("=== PRUEBA DE GUARDADO PARCIAL CORREGIDO ===")
    
    base_url = "http://127.0.0.1:5050"
    
    try:
        # Probar que la página carga
        response = requests.get(f"{base_url}/requerimientos_completar")
        if response.status_code == 200:
            print("✅ Página carga correctamente")
            content = response.text
            
            # Verificar que contiene la función actualizada
            verificaciones = [
                ("Función de validación actualizada", "Guardando progreso:" in content),
                ("Validación flexible", "al menos un campo" in content),
                ("Confirmación para 100%", "confirm(" in content),
                ("Permite progreso parcial", "camposCompletados" in content)
            ]
            
            for nombre, resultado in verificaciones:
                print(f"  {'✅' if resultado else '❌'} {nombre}")
                
        else:
            print(f"❌ Error al cargar página: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
    
    print("\n=== CAMBIOS REALIZADOS ===")
    print()
    print("🔧 VALIDACIÓN JAVASCRIPT ACTUALIZADA:")
    print("❌ ANTES (Muy Restrictiva):")
    print("   • Requería TODOS los campos para guardar")
    print("   • Bloqueaba guardado sin equipo")
    print("   • Bloqueaba guardado sin observaciones")
    print("   • No permitía progreso incremental")
    print()
    print("✅ AHORA (Flexible):")
    print("   • Solo requiere al menos 1 campo para guardar")
    print("   • Permite guardado sin equipo completo")
    print("   • Permite guardado sin observaciones")
    print("   • Calcula porcentaje de progreso")
    print("   • Confirma cuando está 100% completo")
    print()
    
    print("🔄 NUEVO FLUJO DE TRABAJO:")
    print("1. Usuario completa cualquier campo (ej: solo grupo)")
    print("2. Sistema permite guardar (sin validaciones estrictas)")
    print("3. Backend guarda progreso parcial")
    print("4. Mensaje: 'Información guardada'")
    print("5. Usuario puede continuar en otra sesión")
    print("6. Solo cuando 100% completo → confirmación para cambio estado")
    print()
    
    print("✅ BENEFICIOS:")
    print("• Flexibilidad total para guardado incremental")
    print("• Usuario no pierde trabajo por validaciones estrictas")
    print("• Puede trabajar campo por campo")
    print("• Progreso se mantiene entre sesiones")
    print("• UX mejorada significativamente")
    print()
    
    print("🧪 CASOS DE PRUEBA AHORA POSIBLES:")
    print("• ✅ Guardar solo con grupo seleccionado")
    print("• ✅ Guardar sin miembros del equipo")
    print("• ✅ Guardar sin observaciones")
    print("• ✅ Guardar con cualquier combinación parcial")
    print("• ✅ Confirmación solo al estar 100% completo")
    print()
    
    print("🌐 PROBAR EN:")
    print("URL: http://127.0.0.1:5050/requerimientos_completar")
    print("1. Seleccionar solo un grupo en cualquier requerimiento")
    print("2. Hacer clic en 'Guardar Cambios'")
    print("3. Debe permitir guardar sin errores")
    print("4. Mensaje: 'Información guardada'")

if __name__ == "__main__":
    probar_guardado_parcial()
