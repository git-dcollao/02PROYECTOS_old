#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corregir el encoding de los textos en la tabla pages.
Reemplaza los caracteres corruptos (????) por los caracteres correctos en español.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Page

def fix_encoding():
    """Corrige el encoding de todos los textos en la tabla pages"""
    
    app = create_app()
    
    with app.app_context():
        print("🔧 Iniciando corrección de encoding en tabla 'pages'...")
        print("=" * 70)
        
        # Mapeo de textos corruptos a textos correctos
        corrections = {
            # Páginas específicas
            'P????gina principal del sistema': 'Página principal del sistema',
            'Panel de control y estad????sticas': 'Panel de control y estadísticas',
            'Gesti????n de actividades de proyecto': 'Gestión de actividades de proyecto',
            'Visualizaci????n de cronogramas': 'Visualización de cronogramas',
            'Gesti????n de estados de proyecto': 'Gestión de estados de proyecto',
            'Gesti????n de prioridades': 'Gestión de prioridades',
            'Gesti????n de fases de proyecto': 'Gestión de fases de proyecto',
            'Tipolog????as': 'Tipologías',
            'Gesti????n de tipolog????as': 'Gestión de tipologías',
            'Gesti????n de tipos de financiamiento': 'Gestión de tipos de financiamiento',
            'Gesti????n de tipos de proyecto': 'Gestión de tipos de proyecto',
            'Gesti????n de sectores': 'Gestión de sectores',
            'Gesti????n de tipos de recinto': 'Gestión de tipos de recinto',
            'Gesti????n de recintos': 'Gestión de recintos',
            'Gesti????n de equipos de trabajo': 'Gestión de equipos de trabajo',
            'Gesti????n de especialidades': 'Gestión de especialidades',
            '????reas': 'Áreas',
            'Gesti????n de ????reas organizacionales': 'Gestión de áreas organizacionales',
            'Gesti????n de grupos de trabajo': 'Gestión de grupos de trabajo',
            'Gesti????n de usuarios del sistema': 'Gestión de usuarios del sistema',
            'Iniciar Sesi??n': 'Iniciar Sesión',
            'P????gina de inicio de sesi????n': 'Página de inicio de sesión',
            'Cerrar Sesi????n': 'Cerrar Sesión',
            'Cerrar sesi????n del usuario': 'Cerrar sesión del usuario',
            'Editar informaci????n personal del perfil': 'Editar información personal del perfil',
            'P????gina Mi Perfil': 'Página Mi Perfil',
            'Gesti????n de requerimientos': 'Gestión de requerimientos',
            'Administraci??n': 'Administración',
            'Configurar par????metros del sistema': 'Configurar parámetros del sistema',
            'Ver logs y auditor????a': 'Ver logs y auditoría',
            'Gesti????n de respaldos': 'Gestión de respaldos',
            'Gesti????n de Administradores': 'Gestión de Administradores',
            'Asignar recintos espec????ficos a cada administrador': 'Asignar recintos específicos a cada administrador',
            'Gesti????n de Usuarios por Recinto': 'Gestión de Usuarios por Recinto',
            'Completar proyectos (versi????n anterior)': 'Completar proyectos (versión anterior)',
            'Completar informaci????n de proyectos': 'Completar información de proyectos',
            'Gesti??n de Permisos': 'Gestión de Permisos',
        }
        
        pages = Page.query.all()
        updated_count = 0
        
        for page in pages:
            updated = False
            
            # Corregir name
            if page.name in corrections:
                old_name = page.name
                page.name = corrections[old_name]
                print(f"✓ [name] ID {page.id}: '{old_name}' → '{page.name}'")
                updated = True
            
            # Corregir description
            if page.description and page.description in corrections:
                old_desc = page.description
                page.description = corrections[old_desc]
                print(f"✓ [desc] ID {page.id}: '{old_desc}' → '{page.description}'")
                updated = True
            
            if updated:
                updated_count += 1
        
        # Guardar cambios
        if updated_count > 0:
            try:
                db.session.commit()
                print("=" * 70)
                print(f"✅ {updated_count} páginas actualizadas exitosamente")
                print("=" * 70)
                
                # Verificar algunas páginas
                print("\n📋 Verificación de páginas corregidas:")
                test_pages = Page.query.filter(Page.id.in_([1, 2, 6, 19])).all()
                for page in test_pages:
                    print(f"   ID {page.id}: {page.name} - {page.description}")
                    
            except Exception as e:
                db.session.rollback()
                print(f"❌ Error al guardar: {e}")
                return False
        else:
            print("ℹ️  No se encontraron textos para corregir")
        
        return True

if __name__ == '__main__':
    success = fix_encoding()
    sys.exit(0 if success else 1)
