# -*- coding: utf-8 -*-
"""
Controllers Package
==================

Este paquete contiene todos los controladores del sistema organizados por módulos.

Módulos disponibles:
- requerimientos_controller: Gestión completa de requerimientos
- controllers_main (monolítico): Todas las rutas del sistema principal
"""

__version__ = '1.0.0'
__author__ = 'Sistema de Proyectos'

# Importaciones para facilitar el acceso
__all__ = []

try:
    from .requerimientos_controller import requerimientos_bp
    __all__.append('requerimientos_bp')
except ImportError as e:
    print(f"⚠️ Advertencia al importar requerimientos_controller: {e}")

# Importar controllers_bp desde controllers_main.py en app/
try:
    from ..controllers_main import controllers_bp
    __all__.append('controllers_bp')
except ImportError as e:
    print(f"⚠️ No se pudo importar controllers_bp: {e}")
