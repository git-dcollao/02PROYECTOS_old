#!/usr/bin/env python3
"""
Script para probar el sistema de completitud con observaciones requeridas
"""
import os
import sys

# Agregar el directorio del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Requerimiento

def probar_observaciones_requeridas():
    app = create_app()
    
    with app.app_context():
        print("=== PRUEBA: OBSERVACIONES REQUERIDAS PARA 100% ===")
        
        # Obtener requerimientos en preparación (estado 2)
        requerimientos = Requerimiento.query.filter_by(id_estado=2).all()
        
        if not requerimientos:
            print("❌ No hay requerimientos en preparación")
            return
        
        print(f"📋 Analizando {len(requerimientos)} requerimientos en preparación...")
        print()
        
        for req in requerimientos:
            print(f"🎯 Requerimiento #{req.id}: {req.nombre}")
            
            # Calcular completitud con nueva lógica (observaciones requeridas)
            completitud = 0
            campos_estado = {}
            campos_para_estado = []
            
            # Campo 1: Tipología (15%)
            if req.id_tipologia:
                completitud += 15
                campos_estado['Tipología'] = '✅ (15%)'
                campos_para_estado.append(True)
            else:
                campos_estado['Tipología'] = '❌ (0%)'
                campos_para_estado.append(False)
            
            # Campo 2: Financiamiento (15%)
            if req.id_financiamiento:
                completitud += 15
                campos_estado['Financiamiento'] = '✅ (15%)'
                campos_para_estado.append(True)
            else:
                campos_estado['Financiamiento'] = '❌ (0%)'
                campos_para_estado.append(False)
            
            # Campo 3: Tipo Proyecto (15%)
            if req.id_tipoproyecto:
                completitud += 15
                campos_estado['Tipo Proyecto'] = '✅ (15%)'
                campos_para_estado.append(True)
            else:
                campos_estado['Tipo Proyecto'] = '❌ (0%)'
                campos_para_estado.append(False)
            
            # Campo 4: Prioridad (15%)
            if req.id_prioridad:
                completitud += 15
                campos_estado['Prioridad'] = '✅ (15%)'
                campos_para_estado.append(True)
            else:
                campos_estado['Prioridad'] = '❌ (0%)'
                campos_para_estado.append(False)
            
            # Campo 5: Grupo (15%)
            if req.id_grupo:
                completitud += 15
                campos_estado['Grupo'] = '✅ (15%)'
                campos_para_estado.append(True)
            else:
                campos_estado['Grupo'] = '❌ (0%)'
                campos_para_estado.append(False)
            
            # Campo 6: Equipo de Trabajo (15%)
            equipos_count = req.equipos_trabajo.count()
            if equipos_count > 0:
                completitud += 15
                campos_estado['Equipo Trabajo'] = f'✅ (15%) - {equipos_count} miembros'
                campos_para_estado.append(True)
            else:
                campos_estado['Equipo Trabajo'] = '❌ (0%) - Sin miembros'
                campos_para_estado.append(False)
            
            # Campo 7: Observaciones (10%) - AHORA REQUERIDAS
            if req.observacion and req.observacion.strip():
                completitud += 10
                campos_estado['Observaciones'] = '✅ (10%) - REQUERIDAS'
                campos_para_estado.append(True)
            else:
                campos_estado['Observaciones'] = '❌ (0%) - REQUERIDAS'
                campos_para_estado.append(False)
            
            # Mostrar detalle
            print(f"   📊 Completitud Total: {completitud}%")
            for campo, estado in campos_estado.items():
                print(f"      {campo}: {estado}")
            
            # Verificar si puede cambiar de estado (TODOS los campos incluyendo observaciones)
            puede_avanzar = all(campos_para_estado)
            
            if puede_avanzar:
                print(f"   🚀 Estado: ✅ PUEDE AVANZAR (100% completo)")
            else:
                campos_faltantes = []
                nombres_campos = ['Tipología', 'Financiamiento', 'Tipo Proyecto', 'Prioridad', 'Grupo', 'Equipo Trabajo', 'Observaciones']
                for i, campo_ok in enumerate(campos_para_estado):
                    if not campo_ok:
                        campos_faltantes.append(nombres_campos[i])
                
                print(f"   ⏳ Estado: ❌ FALTAN CAMPOS: {', '.join(campos_faltantes)}")
            
            print()
        
        print("=== NUEVA LÓGICA DE COMPLETITUD ===")
        print("🔄 CAMBIOS IMPLEMENTADOS:")
        print("   • Observaciones ahora son REQUERIDAS para cambio de estado")
        print("   • Solo con 100% de completitud se puede avanzar")
        print("   • Todos los 7 campos son obligatorios")
        print()
        print("📋 Campos y Ponderación (TODOS REQUERIDOS):")
        print("   • Tipología: 15%")
        print("   • Financiamiento: 15%")
        print("   • Tipo de Proyecto: 15%")
        print("   • Prioridad: 15%")
        print("   • Grupo: 15%")
        print("   • Equipo de Trabajo: 15%")
        print("   • Observaciones: 10% (AHORA REQUERIDAS)")
        print("   ─────────────────────")
        print("   📊 TOTAL: 100% REQUERIDO PARA AVANZAR")
        print()
        print("✅ VALIDACIONES ACTUALIZADAS:")
        print("   • Frontend: JavaScript valida observaciones")
        print("   • Backend: Python requiere observaciones para cambio de estado")
        print("   • Template: Campo marcado como required con *")

if __name__ == "__main__":
    probar_observaciones_requeridas()
