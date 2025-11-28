#!/usr/bin/env python3
"""
🔧 HERRAMIENTA DE GESTIÓN DE CATEGORÍAS Y PERMISOS
=================================================

Este script permite agregar nuevas categorías y modificar permisos de páginas
de forma fácil y segura.

Uso:
    python category_manager.py --help
    python category_manager.py add-category "Mi Nueva Categoría"
    python category_manager.py add-page "mi.ruta" "Nombre Página" "Mi Categoría" --roles ADMIN SUPERVISOR
    python category_manager.py update-permissions "auth.list_users" --roles SUPERADMIN ADMIN SUPERVISOR
    python category_manager.py list-categories
    python category_manager.py list-pages --category "Usuarios"
"""

import json
import os
import argparse
import sys
from typing import Dict, List, Optional

class PermissionsManager:
    """Gestor de permisos y categorías"""
    
    def __init__(self, permissions_file: str = "page_permissions.json"):
        self.permissions_file = permissions_file
        self.valid_roles = ['USUARIO', 'SUPERVISOR', 'ADMIN', 'SUPERADMIN']
        self.default_categories = {
            'General': {'color': 'success', 'icon': 'fas fa-home'},
            'Usuarios': {'color': 'primary', 'icon': 'fas fa-users'},
            'Proyectos': {'color': 'info', 'icon': 'fas fa-project-diagram'},
            'Reportes': {'color': 'warning', 'icon': 'fas fa-chart-bar'},
            'Configuración': {'color': 'secondary', 'icon': 'fas fa-cogs'},
            'Demo': {'color': 'dark', 'icon': 'fas fa-flask'}
        }
        
    def load_permissions(self) -> Dict:
        """Cargar permisos desde archivo JSON"""
        if not os.path.exists(self.permissions_file):
            return {}
        
        try:
            with open(self.permissions_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error al cargar permisos: {e}")
            return {}
    
    def save_permissions(self, permissions: Dict) -> bool:
        """Guardar permisos en archivo JSON"""
        try:
            with open(self.permissions_file, 'w', encoding='utf-8') as f:
                json.dump(permissions, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"❌ Error al guardar permisos: {e}")
            return False
    
    def get_categories(self) -> List[str]:
        """Obtener lista de categorías existentes"""
        permissions = self.load_permissions()
        categories = set()
        
        for page_data in permissions.values():
            categories.add(page_data.get('category', 'Sin Categoría'))
        
        return sorted(list(categories))
    
    def add_category(self, category_name: str) -> bool:
        """Agregar una nueva categoría (conceptualmente)"""
        categories = self.get_categories()
        
        if category_name in categories:
            print(f"⚠️  La categoría '{category_name}' ya existe")
            return False
        
        print(f"✅ Categoría '{category_name}' lista para usar")
        print(f"💡 Para usar esta categoría, agrega páginas con: --category \"{category_name}\"")
        return True
    
    def add_page(self, page_route: str, page_name: str, category: str, 
                 roles: List[str], description: str = "") -> bool:
        """Agregar una nueva página con permisos"""
        permissions = self.load_permissions()
        
        # Validar roles
        invalid_roles = [r for r in roles if r not in self.valid_roles]
        if invalid_roles:
            print(f"❌ Roles inválidos: {invalid_roles}")
            print(f"✅ Roles válidos: {self.valid_roles}")
            return False
        
        # Verificar si la página ya existe
        if page_route in permissions:
            print(f"⚠️  La página '{page_route}' ya existe")
            return False
        
        # Agregar la nueva página
        permissions[page_route] = {
            "name": page_name,
            "category": category,
            "roles": roles,
            "description": description or f"Página {page_name}"
        }
        
        if self.save_permissions(permissions):
            print(f"✅ Página '{page_name}' agregada exitosamente")
            print(f"   - Ruta: {page_route}")
            print(f"   - Categoría: {category}")
            print(f"   - Roles: {', '.join(roles)}")
            return True
        
        return False
    
    def update_permissions(self, page_route: str, new_roles: List[str]) -> bool:
        """Actualizar permisos de una página existente"""
        permissions = self.load_permissions()
        
        if page_route not in permissions:
            print(f"❌ La página '{page_route}' no existe")
            return False
        
        # Validar roles
        invalid_roles = [r for r in new_roles if r not in self.valid_roles]
        if invalid_roles:
            print(f"❌ Roles inválidos: {invalid_roles}")
            print(f"✅ Roles válidos: {self.valid_roles}")
            return False
        
        old_roles = permissions[page_route]['roles']
        permissions[page_route]['roles'] = new_roles
        
        if self.save_permissions(permissions):
            print(f"✅ Permisos actualizados para '{permissions[page_route]['name']}'")
            print(f"   - Roles anteriores: {', '.join(old_roles)}")
            print(f"   - Roles nuevos: {', '.join(new_roles)}")
            return True
        
        return False
    
    def list_categories(self):
        """Listar todas las categorías con estadísticas"""
        permissions = self.load_permissions()
        categories_count = {}
        
        for page_data in permissions.values():
            category = page_data.get('category', 'Sin Categoría')
            categories_count[category] = categories_count.get(category, 0) + 1
        
        print("\n📁 CATEGORÍAS EXISTENTES:")
        print("=" * 50)
        
        for category, count in sorted(categories_count.items()):
            color_info = self.default_categories.get(category, {'color': 'light', 'icon': 'fas fa-folder'})
            print(f"• {category:20} ({count} páginas) - Color: {color_info['color']}")
        
        print(f"\nTotal: {len(categories_count)} categorías")
    
    def list_pages(self, category_filter: Optional[str] = None):
        """Listar páginas, opcionalmente filtradas por categoría"""
        permissions = self.load_permissions()
        
        if category_filter:
            print(f"\n📋 PÁGINAS EN CATEGORÍA '{category_filter}':")
        else:
            print("\n📋 TODAS LAS PÁGINAS:")
        print("=" * 80)
        
        for page_route, page_data in sorted(permissions.items()):
            if category_filter and page_data.get('category') != category_filter:
                continue
                
            name = page_data.get('name', 'Sin nombre')
            category = page_data.get('category', 'Sin categoría')
            roles = ', '.join(page_data.get('roles', []))
            description = page_data.get('description', 'Sin descripción')
            
            print(f"🔗 {page_route}")
            print(f"   Nombre: {name}")
            print(f"   Categoría: {category}")
            print(f"   Roles: {roles}")
            print(f"   Descripción: {description}")
            print()

def main():
    parser = argparse.ArgumentParser(description="Gestor de permisos y categorías")
    subparsers = parser.add_subparsers(dest='command', help='Comandos disponibles')
    
    # Comando para agregar categoría
    cat_parser = subparsers.add_parser('add-category', help='Agregar nueva categoría')
    cat_parser.add_argument('name', help='Nombre de la categoría')
    
    # Comando para agregar página
    page_parser = subparsers.add_parser('add-page', help='Agregar nueva página')
    page_parser.add_argument('route', help='Ruta de la página (ej: auth.new_page)')
    page_parser.add_argument('name', help='Nombre descriptivo de la página')
    page_parser.add_argument('category', help='Categoría de la página')
    page_parser.add_argument('--roles', nargs='+', required=True, 
                           help='Roles con acceso (USUARIO SUPERVISOR ADMIN SUPERADMIN)')
    page_parser.add_argument('--description', help='Descripción de la página')
    
    # Comando para actualizar permisos
    update_parser = subparsers.add_parser('update-permissions', help='Actualizar permisos de página')
    update_parser.add_argument('route', help='Ruta de la página')
    update_parser.add_argument('--roles', nargs='+', required=True,
                             help='Nuevos roles con acceso')
    
    # Comando para listar categorías
    subparsers.add_parser('list-categories', help='Listar categorías existentes')
    
    # Comando para listar páginas
    list_parser = subparsers.add_parser('list-pages', help='Listar páginas')
    list_parser.add_argument('--category', help='Filtrar por categoría')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    manager = PermissionsManager()
    
    if args.command == 'add-category':
        manager.add_category(args.name)
        
    elif args.command == 'add-page':
        manager.add_page(args.route, args.name, args.category, 
                        args.roles, args.description or "")
        
    elif args.command == 'update-permissions':
        manager.update_permissions(args.route, args.roles)
        
    elif args.command == 'list-categories':
        manager.list_categories()
        
    elif args.command == 'list-pages':
        manager.list_pages(args.category)

if __name__ == "__main__":
    main()
