#!/usr/bin/env python3
"""
Analizador de Backup - Contador de Trabajadores
===========================================
Script para analizar un backup específico y contar trabajadores
"""

import gzip
import re
import os
import sys

def analyze_backup_workers(backup_filename):
    """Analiza un backup específico y cuenta los trabajadores"""
    
    backup_path = os.path.join("backups", backup_filename)
    
    print(f"🔍 Analizando backup: {backup_filename}")
    print("=" * 60)
    
    if not os.path.exists(backup_path):
        print(f"❌ Archivo no encontrado: {backup_path}")
        return None
    
    try:
        # Leer archivo comprimido
        with gzip.open(backup_path, 'rt', encoding='utf-8') as f:
            content = f.read()
        
        print(f"✅ Archivo leído exitosamente")
        print(f"📏 Tamaño descomprimido: {len(content):,} caracteres")
        
        # Buscar definición de tabla trabajador
        table_pattern = r'CREATE TABLE.*?`trabajador`.*?;'
        table_match = re.search(table_pattern, content, re.DOTALL | re.IGNORECASE)
        
        if table_match:
            print(f"✅ Tabla 'trabajador' encontrada en el backup")
            
            # Extraer estructura de la tabla
            table_def = table_match.group(0)
            columns = re.findall(r'`(\w+)`.*?,', table_def)
            print(f"📋 Columnas encontradas: {len(columns)} columnas")
            print(f"🔍 Principales: {', '.join(columns[:8])}...")
        else:
            print("⚠️ Tabla 'trabajador' no encontrada en CREATE TABLE")
        
        # Buscar INSERTs de trabajadores
        insert_patterns = [
            r'INSERT INTO.*?`trabajador`.*?VALUES.*?;',
            r'INSERT INTO.*?trabajador.*?VALUES.*?;',
            r'INSERT INTO `trabajador`.*?;'
        ]
        
        total_workers = 0
        workers_details = []
        
        for i, pattern in enumerate(insert_patterns):
            inserts = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
            if inserts:
                print(f"✅ Patrón {i+1}: Encontrados {len(inserts)} INSERT statements")
                
                for insert in inserts:
                    # Contar VALUES en cada INSERT
                    values_pattern = r'\([^)]+\)'
                    values = re.findall(values_pattern, insert)
                    total_workers += len(values)
                    
                    # Extraer nombres si es posible
                    for value in values[:5]:  # Solo primeros 5 para muestra
                        name_match = re.search(r"'([^']*)', *'([^']*)'", value)
                        if name_match:
                            workers_details.append(f"  • {name_match.group(1)} ({name_match.group(2)})")
                
                break  # Usar solo el primer patrón que funcione
        
        if total_workers > 0:
            print(f"\n🎯 RESULTADO:")
            print(f"👥 Total de trabajadores en el backup: {total_workers}")
            
            if workers_details:
                print(f"\n📋 Muestra de trabajadores encontrados:")
                for detail in workers_details[:10]:  # Mostrar solo primeros 10
                    print(detail)
                if len(workers_details) > 10:
                    print(f"  ... y {len(workers_details) - 10} más")
        else:
            print("❌ No se encontraron trabajadores en el backup")
            
            # Búsqueda alternativa más amplia
            print("\n🔍 Realizando búsqueda alternativa...")
            trabajador_mentions = re.findall(r'trabajador', content, re.IGNORECASE)
            print(f"📊 Menciones de 'trabajador': {len(trabajador_mentions)}")
            
            # Buscar cualquier INSERT que pueda tener datos de usuarios
            all_inserts = re.findall(r'INSERT INTO.*?;', content, re.DOTALL | re.IGNORECASE)
            print(f"📊 Total de INSERT statements: {len(all_inserts)}")
        
        # Información adicional del backup
        print(f"\n📈 Estadísticas del backup:")
        tables = re.findall(r'CREATE TABLE.*?`(\w+)`', content, re.IGNORECASE)
        print(f"📊 Total de tablas: {len(set(tables))}")
        print(f"📋 Principales tablas: {', '.join(sorted(set(tables))[:10])}")
        
        return total_workers
        
    except Exception as e:
        print(f"❌ Error procesando backup: {e}")
        return None

def main():
    """Función principal"""
    backup_file = "Datos_Para_Control_V1_20251114_165031.sql.gz"
    
    result = analyze_backup_workers(backup_file)
    
    print("\n" + "=" * 60)
    if result is not None:
        print(f"🎉 Análisis completado")
        print(f"📊 Trabajadores encontrados: {result}")
    else:
        print("❌ No se pudo analizar el backup")
    print("=" * 60)

if __name__ == "__main__":
    main()