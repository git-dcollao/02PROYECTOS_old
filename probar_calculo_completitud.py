#!/usr/bin/env python3
"""
Script para probar el nuevo cálculo de completitud
"""
import os
import sys

# Agregar el directorio del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Requerimiento

def probar_calculo_completitud():
    app = create_app()
    
    with app.app_context():
        print("=== PRUEBA DEL NUEVO CÁLCULO DE COMPLETITUD ===")
        
        # Obtener requerimientos en preparación (estado 2)
        requerimientos = Requerimiento.query.filter_by(id_estado=2).all()
        
        if not requerimientos:
            print("❌ No hay requerimientos en preparación")
            return
        
        print(f"📋 Analizando {len(requerimientos)} requerimientos en preparación...")
        print()
        
        for req in requerimientos:
            print(f"🎯 Requerimiento #{req.id}: {req.nombre}")
            
            # Calcular completitud según nueva lógica
            completitud = 0
            campos_estado = {}
            
            # Campo 1: Tipología (15%)
            if req.id_tipologia:
                completitud += 15
                campos_estado['Tipología'] = '✅ (15%)'
            else:
                campos_estado['Tipología'] = '❌ (0%)'
            
            # Campo 2: Financiamiento (15%)
            if req.id_financiamiento:
                completitud += 15
                campos_estado['Financiamiento'] = '✅ (15%)'
            else:
                campos_estado['Financiamiento'] = '❌ (0%)'
            
            # Campo 3: Tipo Proyecto (15%)
            if req.id_tipoproyecto:
                completitud += 15
                campos_estado['Tipo Proyecto'] = '✅ (15%)'
            else:
                campos_estado['Tipo Proyecto'] = '❌ (0%)'
            
            # Campo 4: Prioridad (15%)
            if req.id_prioridad:
                completitud += 15
                campos_estado['Prioridad'] = '✅ (15%)'
            else:
                campos_estado['Prioridad'] = '❌ (0%)'
            
            # Campo 5: Grupo (15%)
            if req.id_grupo:
                completitud += 15
                campos_estado['Grupo'] = '✅ (15%)'
            else:
                campos_estado['Grupo'] = '❌ (0%)'
            
            # Campo 6: Equipo de Trabajo (15%)
            if req.equipos_trabajo.count() > 0:
                completitud += 15
                campos_estado['Equipo Trabajo'] = f'✅ (15%) - {req.equipos_trabajo.count()} miembros'
            else:
                campos_estado['Equipo Trabajo'] = '❌ (0%) - Sin miembros'
            
            # Campo 7: Observaciones (10%)
            if req.observacion and req.observacion.strip():
                completitud += 10
                campos_estado['Observaciones'] = '✅ (10%)'
            else:
                campos_estado['Observaciones'] = '❌ (0%)'
            
            # Mostrar detalle
            print(f"   📊 Completitud Total: {completitud}%")
            for campo, estado in campos_estado.items():
                print(f"      {campo}: {estado}")
            
            # Verificar si puede cambiar de estado
            puede_avanzar = all([
                req.id_tipologia,
                req.id_financiamiento,
                req.id_tipoproyecto,
                req.id_prioridad,
                req.id_grupo,
                req.equipos_trabajo.count() > 0
            ])
            
            if puede_avanzar:
                print(f"   🚀 Estado: Puede avanzar a ejecución")
            else:
                print(f"   ⏳ Estado: Faltan campos requeridos para avanzar")
            
            print()
        
        print("=== RESUMEN DEL SISTEMA DE COMPLETITUD ===")
        print("📋 Campos y Ponderación:")
        print("   • Tipología: 15%")
        print("   • Financiamiento: 15%")
        print("   • Tipo de Proyecto: 15%")
        print("   • Prioridad: 15%")
        print("   • Grupo: 15%")
        print("   • Equipo de Trabajo: 15%")
        print("   • Observaciones: 10%")
        print("   ─────────────────────")
        print("   📊 TOTAL: 100%")
        print()
        print("🔄 Lógica de Estados:")
        print("   • Progreso Visual: Se muestra todos los campos (incluye observaciones)")
        print("   • Cambio de Estado: Solo campos requeridos (sin observaciones)")
        print("   • Color Verde: 100% completitud")
        print("   • Color Amarillo: Menos de 100%")

if __name__ == "__main__":
    probar_calculo_completitud()
