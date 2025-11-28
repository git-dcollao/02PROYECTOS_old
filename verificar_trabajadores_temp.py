#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from datetime import datetime

# Añadir el directorio de la aplicación al path de Python
sys.path.insert(0, '/app')

from app import create_app
from app.models import Trabajador, db

def main():
    print("🔍 VERIFICANDO TRABAJADORES CON EMAILS TEMPORALES")
    print("=" * 60)
    
    app = create_app()
    with app.app_context():
        try:
            # Buscar trabajadores con emails temporales
            trabajadores_temp = Trabajador.query.filter(
                Trabajador.email.like('%@temp.com')
            ).all()
            
            print(f"\n📊 TRABAJADORES CON EMAILS TEMPORALES: {len(trabajadores_temp)}")
            print("-" * 40)
            
            if trabajadores_temp:
                for trabajador in trabajadores_temp:
                    print(f"ID: {trabajador.id}")
                    print(f"Nombre: {trabajador.nombre}")
                    print(f"Nombrecorto: {trabajador.nombrecorto}")
                    print(f"Email: {trabajador.email}")
                    print(f"Custom Role ID: {trabajador.custom_role_id}")
                    print(f"Sector ID: {trabajador.sector_id}")
                    print(f"Recinto ID: {trabajador.recinto_id}")
                    print(f"Created at: {trabajador.created_at}")
                    print("-" * 40)
            else:
                print("❌ No hay trabajadores con emails temporales")
            
            # Verificar específicamente el trabajador ARQ02
            arq02 = Trabajador.query.filter_by(nombrecorto='ARQ02').first()
            if arq02:
                print("\n🎯 TRABAJADOR ARQ02 ENCONTRADO:")
                print(f"ID: {arq02.id}")
                print(f"Nombre: {arq02.nombre}")
                print(f"Nombrecorto: {arq02.nombrecorto}")
                print(f"Email: {arq02.email}")
                print(f"Custom Role ID: {arq02.custom_role_id}")
                print(f"Created at: {arq02.created_at}")
                print("✅ Este trabajador ya existe en la base de datos")
            else:
                print("\n❌ TRABAJADOR ARQ02 NO ENCONTRADO")
            
            # Contar todos los trabajadores
            total_trabajadores = Trabajador.query.count()
            print(f"\n📈 TOTAL DE TRABAJADORES EN DB: {total_trabajadores}")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    main()