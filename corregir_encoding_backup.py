#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corregir errores de encoding UTF-8 en el archivo de backup SQL
Los caracteres mal codificados (├│, ├í, ├ñ, etc.) se corrigen a sus versiones correctas
"""

import os
import re
from datetime import datetime

def corregir_encoding(archivo_entrada, archivo_salida=None):
    """
    Corrige errores de encoding en archivo SQL
    
    Args:
        archivo_entrada: Ruta del archivo SQL con errores
        archivo_salida: Ruta del archivo corregido (si es None, se sobrescribe el original)
    """
    
    # Mapeo de caracteres mal codificados a caracteres correctos
    correcciones = {
        '├│': 'ó',
        '├í': 'á',
        '├ñ': 'ñ',
        '├®': 'í',
        '├©': 'é',
        '├║': 'ú',
        '├ú': 'Ú',
        '├ü': 'Á',
        '├ë': 'Ñ',
        '├ô': 'Ó',
        '├ì': 'Í',
        '├ë': 'É',
    }
    
    print("=" * 80)
    print("🔧 CORRECCIÓN DE ENCODING UTF-8 EN BACKUP SQL")
    print("=" * 80)
    
    # Verificar que el archivo existe
    if not os.path.exists(archivo_entrada):
        print(f"❌ ERROR: El archivo '{archivo_entrada}' no existe")
        return False
    
    # Si no se especifica archivo de salida, crear uno con timestamp
    if archivo_salida is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_base = os.path.splitext(archivo_entrada)[0]
        archivo_salida = f"{nombre_base}_CORREGIDO_{timestamp}.sql"
    
    print(f"\n📁 Archivo entrada: {archivo_entrada}")
    print(f"📁 Archivo salida: {archivo_salida}")
    
    # Leer el archivo como bytes y decodificar manualmente
    try:
        with open(archivo_entrada, 'rb') as f:
            contenido_bytes = f.read()
        
        # Intentar decodificar como UTF-8
        try:
            contenido = contenido_bytes.decode('utf-8')
        except UnicodeDecodeError:
            # Si falla, usar latin-1
            contenido = contenido_bytes.decode('latin-1')
            
    except Exception as e:
        print(f"❌ Error al leer el archivo: {e}")
        return False
    
    # Contar errores antes de la corrección
    total_errores = 0
    errores_por_tipo = {}
    
    for caracter_mal, caracter_correcto in correcciones.items():
        count = contenido.count(caracter_mal)
        if count > 0:
            total_errores += count
            errores_por_tipo[caracter_mal] = {
                'correcto': caracter_correcto,
                'count': count
            }
    
    print(f"\n📊 Errores encontrados: {total_errores}")
    if errores_por_tipo:
        print("\n🔍 Detalle de correcciones:")
        for mal, info in errores_por_tipo.items():
            print(f"   '{mal}' → '{info['correcto']}': {info['count']} ocurrencias")
    
    # Aplicar correcciones
    contenido_corregido = contenido
    for caracter_mal, caracter_correcto in correcciones.items():
        contenido_corregido = contenido_corregido.replace(caracter_mal, caracter_correcto)
    
    # Escribir el archivo corregido
    try:
        with open(archivo_salida, 'w', encoding='utf-8', newline='\n') as f:
            f.write(contenido_corregido)
        print(f"\n✅ Archivo corregido guardado exitosamente")
        
        # Mostrar estadísticas
        size_original = os.path.getsize(archivo_entrada)
        size_corregido = os.path.getsize(archivo_salida)
        
        print(f"\n📈 Estadísticas:")
        print(f"   Tamaño original: {size_original:,} bytes")
        print(f"   Tamaño corregido: {size_corregido:,} bytes")
        print(f"   Errores corregidos: {total_errores}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al escribir el archivo: {e}")
        return False

def verificar_correcciones(archivo):
    """
    Verifica que el archivo no tenga errores de encoding
    """
    print("\n" + "=" * 80)
    print("🔍 VERIFICACIÓN DE CORRECCIONES")
    print("=" * 80)
    
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Buscar patrones de caracteres mal codificados
        patron_errores = re.compile(r'├[│íñ®©║úüëôì]')
        errores = patron_errores.findall(contenido)
        
        if errores:
            print(f"⚠️  Se encontraron {len(errores)} caracteres con posibles errores")
            print("   Primeros 10 errores:", errores[:10])
            return False
        else:
            print("✅ No se encontraron errores de encoding")
            return True
            
    except Exception as e:
        print(f"❌ Error al verificar: {e}")
        return False

def mostrar_ejemplos(archivo):
    """
    Muestra ejemplos de líneas corregidas
    """
    print("\n" + "=" * 80)
    print("📋 EJEMPLOS DE CORRECCIONES")
    print("=" * 80)
    
    ejemplos = [
        ("estado", "En Ejecución"),
        ("estado", "Fin de Ejecución"),
        ("area", "Administración"),
        ("categories", "Gestión"),
        ("fase", "Preinversión"),
        ("fase", "Inversión"),
        ("financiamiento", "Subsecretaría"),
    ]
    
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        for tabla, buscar in ejemplos:
            if buscar in contenido:
                # Buscar la línea que contiene el texto
                for linea in contenido.split('\n'):
                    if tabla in linea.lower() and buscar in linea:
                        # Mostrar fragmento de la línea
                        idx = linea.find(buscar)
                        inicio = max(0, idx - 20)
                        fin = min(len(linea), idx + len(buscar) + 20)
                        fragmento = linea[inicio:fin]
                        print(f"   ✓ {tabla}: ...{fragmento}...")
                        break
    except Exception as e:
        print(f"❌ Error al mostrar ejemplos: {e}")

if __name__ == "__main__":
    # Archivo de entrada
    archivo_backup = "BACKUP_LIMPIO_UTF8_20251103_114447.sql"
    
    # Corregir encoding
    exito = corregir_encoding(archivo_backup)
    
    if exito:
        # Obtener nombre del archivo corregido
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archivo_corregido = f"BACKUP_LIMPIO_UTF8_20251103_114447_CORREGIDO_{timestamp}.sql"
        
        # Verificar correcciones
        verificar_correcciones(archivo_corregido)
        
        # Mostrar ejemplos
        mostrar_ejemplos(archivo_corregido)
        
        print("\n" + "=" * 80)
        print("🎉 PROCESO COMPLETADO")
        print("=" * 80)
        print(f"\n📝 Para aplicar el backup corregido, ejecuta:")
        print(f"   docker-compose exec -T proyectos_db mysql -u root -p123456 proyectosDB < {archivo_corregido}")
        print("\n⚠️  IMPORTANTE: Esto sobrescribirá los datos actuales de la base de datos")
        print("   Asegúrate de hacer un backup antes si tienes datos importantes")
    else:
        print("\n❌ El proceso falló. Revisa los errores anteriores.")
