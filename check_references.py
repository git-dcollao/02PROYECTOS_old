#!/usr/bin/env python3
from app import create_app, db
from app.models import *

def main():
    app = create_app()
    
    with app.app_context():
        print('=== VERIFICANDO REFERENCIAS DE BASE DE DATOS ===')
        
        # Verificar Fases
        
        # Verificar Sectores
        print(f'\n🔍 Sectores: {Sector.query.count()} registros')
        if Sector.query.count() > 0:
            for s in Sector.query.all():
                print(f'   ID:{s.id} - {s.nombre}')
        
        # Verificar EtapasN1
        
        # Verificar si existen registros dependientes
        print(f'\n🔍 Tipologías: {Tipologia.query.count()} registros')
        print(f'🔍 TiposRecinto: {TipoRecinto.query.count()} registros')
        
        # Analizar problemas específicos
        print('\n📋 ANALIZANDO PROBLEMAS DE REFERENCIAS:')
        
        # 1. Tipologías intentan referenciar id_fase=1
        
        # 2. TiposRecinto intentan referenciar id_sector=2
        sector_2 = Sector.query.filter_by(id=2).first()
        print(f'   - ¿Existe Sector con ID=2? {"✅ Sí" if sector_2 else "❌ No"}')
        if sector_2:
            print(f'     Sector ID=2: {sector_2.nombre}')
        
        # 3. EtapasN2 intentan referenciar id_etapaN1=1
        
        # 4. Trabajadores intentan referenciar sector_id=1
        sector_1 = Sector.query.filter_by(id=1).first()
        print(f'   - ¿Existe Sector con ID=1? {"✅ Sí" if sector_1 else "❌ No"}')
        if sector_1:
            print(f'     Sector ID=1: {sector_1.nombre}')
        
        print('\n=== FIN DE VERIFICACIÓN ===')

if __name__ == '__main__':
    main()