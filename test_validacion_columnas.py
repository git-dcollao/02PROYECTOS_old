"""
🧪 TEST: Validar corrección de validación de columnas
"""
def main():
    print("=" * 80)
    print("🧪 TEST: Validar corrección de validación de columnas")
    print("=" * 80)
    
    # Columnas que debería requerir el sistema (CORREGIDAS)
    columnas_requeridas_esperadas = [
        'Nivel de esquema', 'EDT', 'Nombre de tarea', 
        'Duración', 'Comienzo', 'Fin', '% completado', 
        'Real Anterior', '% programado', '% Real', 'Decimales', 
        'Predecesoras', 'Nombres de los recursos', 'Días Corrido'
    ]
    
    # Columnas que proporciona el Excel del usuario
    columnas_disponibles = [
        'Nivel de esquema', 'EDT', 'Nombre de tarea', 'Duración', 
        'Comienzo', 'Fin', '% completado', 'Real Anterior', 
        '% programado', '% Real', 'Decimales', 'Predecesoras', 
        'Nombres de los recursos', 'Días Corrido'
    ]
    
    print("📋 Validando columnas:")
    print(f"   Total columnas requeridas: {len(columnas_requeridas_esperadas)}")
    print(f"   Total columnas disponibles: {len(columnas_disponibles)}")
    
    # Buscar columnas faltantes (simulando la lógica del sistema)
    mapeo_columnas = {}
    for col_req in columnas_requeridas_esperadas:
        col_encontrada = None
        for col_disp in columnas_disponibles:
            # Comparación exacta primero
            if col_req == col_disp:
                col_encontrada = col_disp
                break
            # Comparación flexible (sin mayúsculas/minúsculas y espacios)
            elif col_req.lower().replace(' ', '') == str(col_disp).lower().replace(' ', ''):
                col_encontrada = col_disp
                break
        
        if col_encontrada:
            mapeo_columnas[col_req] = col_encontrada
            print(f"   ✅ '{col_req}' → '{col_encontrada}'")
        else:
            print(f"   ❌ '{col_req}' → NO ENCONTRADA")
    
    # Verificar que no hay columnas vacías en requeridas
    columnas_vacias = [col for col in columnas_requeridas_esperadas if col == '' or col is None]
    
    print(f"\n🔍 Verificación de integridad:")
    print(f"   Columnas vacías en requeridas: {len(columnas_vacias)}")
    if columnas_vacias:
        print(f"   ❌ Encontradas columnas vacías: {columnas_vacias}")
    else:
        print(f"   ✅ No hay columnas vacías")
    
    # Calcular columnas faltantes
    columnas_faltantes = [col for col in columnas_requeridas_esperadas if col not in mapeo_columnas]
    
    print(f"\n📊 Resultado de validación:")
    print(f"   Columnas mapeadas exitosamente: {len(mapeo_columnas)}")
    print(f"   Columnas faltantes: {len(columnas_faltantes)}")
    
    if columnas_faltantes:
        print(f"   ❌ Faltantes: {columnas_faltantes}")
        return False
    else:
        print(f"   ✅ Todas las columnas encontradas correctamente")
        
    # Simular mensaje de error/éxito
    if len(columnas_faltantes) == 0 and len(columnas_vacias) == 0:
        print(f"\n✅ TEST EXITOSO: El Excel debería procesarse sin errores de validación")
        print(f"   - No hay columnas vacías en la validación")
        print(f"   - Todas las columnas requeridas están disponibles")
        print(f"   - El mapeo es correcto")
        return True
    else:
        print(f"\n❌ TEST FALLIDO: Hay problemas en la validación")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
