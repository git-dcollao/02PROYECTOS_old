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
    print("🔧 PROBANDO VERIFICACIÓN ROBUSTA DE TRABAJADORES")
    print("=" * 60)
    
    app = create_app()
    with app.app_context():
        try:
            # Verificar trabajador ARQ02 específicamente
            print("🔍 1. Verificando trabajador ARQ02 por NOMBRECORTO...")
            arq02_por_nombre = Trabajador.query.filter_by(nombrecorto='ARQ02').first()
            
            print("🔍 2. Verificando trabajador ARQ02 por EMAIL...")
            email_esperado = "arq02@temp.com"
            arq02_por_email = Trabajador.query.filter_by(email=email_esperado).first()
            
            print("\n📊 RESULTADOS:")
            print(f"Por nombrecorto 'ARQ02': {'✅ Encontrado' if arq02_por_nombre else '❌ No encontrado'}")
            print(f"Por email '{email_esperado}': {'✅ Encontrado' if arq02_por_email else '❌ No encontrado'}")
            
            if arq02_por_nombre:
                print(f"\n📝 DATOS TRABAJADOR (por nombrecorto):")
                print(f"   ID: {arq02_por_nombre.id}")
                print(f"   Nombre: {arq02_por_nombre.nombre}")
                print(f"   Nombrecorto: {arq02_por_nombre.nombrecorto}")
                print(f"   Email: {arq02_por_nombre.email}")
                
            if arq02_por_email:
                print(f"\n📝 DATOS TRABAJADOR (por email):")
                print(f"   ID: {arq02_por_email.id}")
                print(f"   Nombre: {arq02_por_email.nombre}")
                print(f"   Nombrecorto: {arq02_por_email.nombrecorto}")
                print(f"   Email: {arq02_por_email.email}")
                
            # Verificar si son el mismo registro
            if arq02_por_nombre and arq02_por_email:
                if arq02_por_nombre.id == arq02_por_email.id:
                    print("\n✅ COHERENCIA: Ambas búsquedas devuelven el MISMO trabajador")
                else:
                    print("\n❌ PROBLEMA: Búsquedas devuelven trabajadores DIFERENTES")
                    print("   Esto indica duplicados en la base de datos")
            
            # Buscar todos los trabajadores con email temporal
            print("\n🔍 3. Verificando TODOS los trabajadores con emails @temp.com...")
            trabajadores_temp = Trabajador.query.filter(
                Trabajador.email.like('%@temp.com')
            ).order_by(Trabajador.created_at.desc()).all()
            
            print(f"\n📊 TRABAJADORES CON EMAILS TEMPORALES: {len(trabajadores_temp)}")
            
            for i, trabajador in enumerate(trabajadores_temp, 1):
                print(f"\n{i}. ID: {trabajador.id}")
                print(f"   Nombre: {trabajador.nombre}")
                print(f"   Nombrecorto: {trabajador.nombrecorto}")
                print(f"   Email: {trabajador.email}")
                print(f"   Creado: {trabajador.created_at}")
                
            # Simular la lógica que usará la función mejorada
            print("\n" + "="*60)
            print("🧪 SIMULANDO LÓGICA DE VERIFICACIÓN MEJORADA")
            print("="*60)
            
            recurso = "ARQ02"
            print(f"\n🔍 Procesando recurso: '{recurso}'")
            
            # Paso 1: Buscar por nombrecorto
            trabajador = Trabajador.query.filter_by(nombrecorto=recurso).first()
            print(f"   Búsqueda por nombrecorto: {'✅ Encontrado' if trabajador else '❌ No encontrado'}")
            
            # Paso 2: Buscar por email si no se encontró por nombrecorto
            email_esperado = f"{recurso.lower().replace(' ', '.')}@temp.com"
            trabajador_por_email = Trabajador.query.filter_by(email=email_esperado).first()
            print(f"   Búsqueda por email: {'✅ Encontrado' if trabajador_por_email else '❌ No encontrado'}")
            
            # Paso 3: Determinar qué trabajador usar
            if trabajador_por_email:
                trabajador = trabajador_por_email
                print(f"   📝 Usando trabajador encontrado por EMAIL: ID {trabajador.id}")
            elif trabajador:
                print(f"   📝 Usando trabajador encontrado por NOMBRECORTO: ID {trabajador.id}")
            else:
                print(f"   📝 NO HAY TRABAJADOR EXISTENTE - Se crearían nuevos datos")
                
            if trabajador:
                print(f"\n✅ RESULTADO: Se usará trabajador existente ID {trabajador.id}")
                print(f"   Nombre: {trabajador.nombre}")
                print(f"   Nombrecorto: {trabajador.nombrecorto}")
                print(f"   Email: {trabajador.email}")
                print("   🚫 NO se creará trabajador duplicado")
            else:
                print(f"\n🆕 RESULTADO: Se crearía nuevo trabajador para '{recurso}'")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    main()