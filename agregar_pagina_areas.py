#!/usr/bin/env python3
"""
Script para agregar la página de áreas al sistema de permisos
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import Page, Category, PagePermission
from sqlalchemy import text
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def agregar_pagina_areas():
    """Agrega la página de áreas al sistema de permisos"""
    
    app = create_app()
    
    with app.app_context():
        try:
            # Buscar la categoría de Configuración
            categoria_config = Category.query.filter_by(name='Configuración').first()
            
            if not categoria_config:
                logger.error("❌ No se encontró la categoría 'Configuración'")
                return False
            
            # Verificar si la página ya existe
            pagina_existente = Page.query.filter_by(name='Áreas').first()
            
            if pagina_existente:
                logger.info("ℹ️ La página 'Áreas' ya existe")
                return True
            
            # Crear la nueva página
            nueva_pagina = Page(
                name='Áreas',
                route='/areas',
                category_id=categoria_config.id,
                description='Gestión de áreas organizacionales'
            )
            
            db.session.add(nueva_pagina)
            db.session.flush()  # Para obtener el ID
            
            # Agregar permisos para ADMIN y SUPERADMIN
            roles_con_acceso = ['ADMIN', 'SUPERADMIN']
            
            for rol in roles_con_acceso:
                permiso = PagePermission(
                    page_id=nueva_pagina.id,
                    role=rol
                )
                db.session.add(permiso)
            
            db.session.commit()
            
            logger.info("✅ Página 'Áreas' agregada exitosamente al sistema de permisos")
            logger.info(f"✅ Permisos otorgados a: {', '.join(roles_con_acceso)}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error al agregar página de áreas: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    print("🚀 Agregando página de áreas al sistema de permisos...")
    
    if agregar_pagina_areas():
        print("✅ Página de áreas agregada exitosamente")
    else:
        print("❌ Error al agregar página de áreas")
        sys.exit(1)
