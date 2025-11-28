#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para eliminar tablas EtapaN1, EtapaN2, EtapaN3, EtapaN4
Fecha: 2025-11-05
Propósito: Eliminar tablas de etapas jerárquicas obsoletas
"""

import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from sqlalchemy import text
from config import DevelopmentConfig

def eliminar_tablas_etapas():
    """Eliminar tablas EtapaN1-N4 de la base de datos"""
    
    app = create_app(DevelopmentConfig)
    
    with app.app_context():
        try:
            print("🔄 Iniciando eliminación de tablas EtapaN...")
            print("-" * 60)
            
            # Deshabilitar verificación de foreign keys temporalmente
            db.session.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
            db.session.commit()
            print("⚠️  Foreign key checks deshabilitadas temporalmente")
            
            # Lista de tablas a eliminar (orden inverso de dependencias)
            tablas = ['etapan4', 'etapan3', 'etapan2', 'etapan1']
            
            for tabla in tablas:
                try:
                    # Verificar si la tabla existe
                    result = db.session.execute(text(
                        f"SELECT COUNT(*) as count FROM information_schema.tables "
                        f"WHERE table_schema = DATABASE() AND table_name = '{tabla}'"
                    ))
                    existe = result.fetchone()[0] > 0
                    
                    if existe:
                        # Obtener conteo de registros antes de eliminar
                        count_result = db.session.execute(text(f"SELECT COUNT(*) FROM {tabla}"))
                        num_registros = count_result.fetchone()[0]
                        
                        # Eliminar tabla
                        db.session.execute(text(f"DROP TABLE IF EXISTS {tabla}"))
                        db.session.commit()
                        
                        print(f"✅ Tabla '{tabla}' eliminada ({num_registros} registros)")
                    else:
                        print(f"⏭️  Tabla '{tabla}' no existe - omitiendo")
                        
                except Exception as e:
                    print(f"❌ Error al eliminar tabla '{tabla}': {str(e)}")
                    db.session.rollback()
            
            # Volver a habilitar verificación de foreign keys
            db.session.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
            db.session.commit()
            print("✅ Foreign key checks rehabilitadas")
            
            print("-" * 60)
            print("🎉 Proceso completado exitosamente")
            
            # Verificar tablas restantes
            print("\n📋 Verificando tablas restantes en la base de datos...")
            result = db.session.execute(text("SHOW TABLES"))
            tablas_restantes = [row[0] for row in result]
            
            # Filtrar solo tablas que puedan ser relevantes
            tablas_etapa = [t for t in tablas_restantes if 'etapa' in t.lower()]
            
            if tablas_etapa:
                print(f"   Tablas con 'etapa' encontradas: {', '.join(tablas_etapa)}")
            else:
                print("   ✅ No se encontraron tablas EtapaN restantes")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Error general: {str(e)}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            return False

if __name__ == '__main__':
    print("=" * 60)
    print("ELIMINACIÓN DE TABLAS ETAPAN1, ETAPAN2, ETAPAN3, ETAPAN4")
    print("=" * 60)
    print()
    
    confirmacion = input("⚠️  ¿Está seguro de que desea eliminar estas tablas? (si/no): ")
    
    if confirmacion.lower() in ['si', 'sí', 's', 'yes', 'y']:
        print()
        exito = eliminar_tablas_etapas()
        
        if exito:
            print("\n✅ Tablas eliminadas correctamente")
            print("💡 Recuerde ejecutar las migraciones si es necesario:")
            print("   docker-compose exec proyectos_app flask db migrate -m 'Eliminar tablas EtapaN'")
            print("   docker-compose exec proyectos_app flask db upgrade")
        else:
            print("\n❌ Hubo errores durante la eliminación")
            sys.exit(1)
    else:
        print("\n⏹️  Operación cancelada por el usuario")
        sys.exit(0)
