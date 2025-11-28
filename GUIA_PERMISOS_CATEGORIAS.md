# 📖 GUÍA COMPLETA: GESTIÓN DE CATEGORÍAS Y PERMISOS

## 🎯 **Métodos para Agregar Categorías y Modificar Permisos**

### **1️⃣ MÉTODOS DISPONIBLES**

#### **A) Línea de Comandos (Recomendado)**
```bash
# Ver todas las opciones
python category_manager.py --help

# Listar categorías actuales
python category_manager.py list-categories

# Listar todas las páginas
python category_manager.py list-pages

# Listar páginas de una categoría específica
python category_manager.py list-pages --category "Usuarios"
```

#### **B) Interfaz Web (En desarrollo)**
- URL: `http://localhost:5050/permissions/`
- Botón "➕ Agregar Página" 
- Edición en línea con checkboxes de roles

#### **C) Edición Directa de JSON**
- Archivo: `page_permissions.json`
- Estructura JSON manual

---

### **2️⃣ AGREGAR NUEVAS CATEGORÍAS**

#### **🔧 Usando category_manager.py**

```bash
# Agregar nueva categoría
python category_manager.py add-category "Finanzas"
python category_manager.py add-category "Recursos Humanos" 
python category_manager.py add-category "Inventario"
python category_manager.py add-category "Seguridad"
```

#### **📝 Categorías Predefinidas con Colores**

| Categoría | Color Bootstrap | Icono | Uso |
|-----------|----------------|--------|-----|
| General | `success` (verde) | `fa-home` | Páginas principales |
| Usuarios | `primary` (azul) | `fa-users` | Gestión de usuarios |
| Proyectos | `info` (celeste) | `fa-project-diagram` | Gestión de proyectos |
| Reportes | `warning` (amarillo) | `fa-chart-bar` | Informes y estadísticas |
| Configuración | `secondary` (gris) | `fa-cogs` | Configuraciones del sistema |
| Demo | `dark` (negro) | `fa-flask` | Páginas de prueba |

#### **🎨 Agregar Categoría con Color Personalizado**

Para agregar una nueva categoría con color personalizado, edita el archivo `app/templates/permissions/index.html` y busca la función `getCategoryColor()`:

```javascript
function getCategoryColor(category) {
    const colors = {
        'General': 'success',
        'Usuarios': 'primary', 
        'Proyectos': 'info',
        'Reportes': 'warning',
        'Configuración': 'secondary',
        'Demo': 'dark',
        // AGREGAR NUEVAS CATEGORÍAS AQUÍ:
        'Finanzas': 'danger',        // Rojo
        'Recursos Humanos': 'success', // Verde
        'Inventario': 'info',         // Celeste
        'Seguridad': 'warning'        // Amarillo
    };
    return colors[category] || 'light';
}
```

---

### **3️⃣ AGREGAR NUEVAS PÁGINAS**

#### **🔧 Usando category_manager.py**

```bash
# Formato básico
python category_manager.py add-page "ruta.pagina" "Nombre de la Página" "Categoría" --roles ROLE1 ROLE2

# Ejemplos prácticos:
python category_manager.py add-page "finance.budget" "Presupuesto" "Finanzas" --roles SUPERADMIN ADMIN --description "Gestión de presupuestos anuales"

python category_manager.py add-page "hr.employees" "Empleados" "Recursos Humanos" --roles SUPERADMIN ADMIN SUPERVISOR --description "Lista de empleados"

python category_manager.py add-page "inventory.stock" "Inventario" "Inventario" --roles ADMIN SUPERVISOR --description "Control de stock"

python category_manager.py add-page "security.logs" "Logs de Seguridad" "Seguridad" --roles SUPERADMIN --description "Registros de seguridad del sistema"
```

#### **📋 Roles Disponibles (Orden Jerárquico)**

| Rol | Nivel | Descripción |
|-----|--------|-------------|
| `USUARIO` | 1 | Acceso básico, solo lectura |
| `SUPERVISOR` | 2 | Gestión de equipos |
| `ADMIN` | 3 | Administración del sistema |
| `SUPERADMIN` | 4 | Acceso total |

---

### **4️⃣ MODIFICAR PERMISOS EXISTENTES**

#### **🔧 Usando category_manager.py**

```bash
# Cambiar permisos de una página existente
python category_manager.py update-permissions "auth.list_users" --roles SUPERADMIN ADMIN SUPERVISOR

# Ejemplos:
# Dar acceso a todos los roles
python category_manager.py update-permissions "main.dashboard" --roles SUPERADMIN ADMIN SUPERVISOR USUARIO

# Restringir a solo administradores
python category_manager.py update-permissions "auth.create_user" --roles SUPERADMIN ADMIN

# Solo superadministrador
python category_manager.py update-permissions "permissions.index" --roles SUPERADMIN
```

#### **🌐 Usando la Interfaz Web**

1. Accede a `http://localhost:5050/permissions/`
2. Inicia sesión como admin: `admin@sistema.com` / `admin123`
3. Busca la página en la tabla
4. Marca/desmarca los checkboxes de roles
5. Haz clic en el botón 💾 para guardar
6. O usa "Guardar Todo" para guardar cambios masivos

---

### **5️⃣ CONSULTAS Y LISTADOS**

#### **📋 Ver Estado Actual**

```bash
# Ver todas las categorías con estadísticas
python category_manager.py list-categories

# Ver todas las páginas
python category_manager.py list-pages

# Ver páginas de una categoría específica
python category_manager.py list-pages --category "Usuarios"
python category_manager.py list-pages --category "Finanzas"
```

---

### **6️⃣ ESTRUCTURA DEL ARCHIVO JSON**

#### **📄 Formato de page_permissions.json**

```json
{
  "ruta.de.la.pagina": {
    "name": "Nombre Descriptivo",
    "category": "Nombre de la Categoría",
    "roles": ["SUPERADMIN", "ADMIN", "SUPERVISOR"],
    "description": "Descripción de la página"
  }
}
```

#### **📝 Ejemplo Completo**

```json
{
  "finance.budget": {
    "name": "Presupuesto Anual",
    "category": "Finanzas",
    "roles": ["SUPERADMIN", "ADMIN"],
    "description": "Gestión y aprobación de presupuestos anuales"
  },
  "hr.employees": {
    "name": "Gestión de Empleados", 
    "category": "Recursos Humanos",
    "roles": ["SUPERADMIN", "ADMIN", "SUPERVISOR"],
    "description": "CRUD de información de empleados"
  }
}
```

---

### **7️⃣ MEJORES PRÁCTICAS**

#### **🎯 Nomenclatura de Rutas**
- Usa formato `módulo.acción`: `users.create`, `reports.monthly`
- Sé consistente: `finance.budget`, `finance.expenses`
- Evita espacios y caracteres especiales

#### **🏷️ Nomenclatura de Categorías**
- Usa nombres claros y descriptivos
- Mantén consistencia en el idioma
- Agrupa lógicamente por función de negocio

#### **🔐 Asignación de Roles**
- Principio de menor privilegio
- SUPERADMIN: Solo para configuraciones críticas
- ADMIN: Gestión general del sistema
- SUPERVISOR: Gestión de equipos
- USUARIO: Solo lectura y operaciones básicas

#### **📊 Organización**
- Máximo 10-15 páginas por categoría
- Usa subcategorías si es necesario
- Documenta cada página con descripción clara

---

### **8️⃣ INTEGRACIÓN CON EL SISTEMA**

#### **🔗 Usar Permisos en Vistas Flask**

```python
from app.routes.permissions_routes import permission_manager

@app.route('/mi-nueva-pagina')
@login_required
def mi_nueva_pagina():
    # Verificar permisos
    if not permission_manager.can_access_page(current_user.role, 'finance.budget'):
        flash('No tienes permisos para acceder a esta página', 'error')
        return redirect(url_for('main.index'))
    
    return render_template('finance/budget.html')
```

#### **🎨 Decorador de Permisos Personalizado**

```python
def require_page_permission(page_route):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not permission_manager.can_access_page(current_user.role, page_route):
                flash('Acceso denegado', 'error')
                return redirect(url_for('main.index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Uso:
@app.route('/presupuesto')
@login_required
@require_page_permission('finance.budget')
def budget():
    return render_template('finance/budget.html')
```

---

### **9️⃣ COMANDOS DE EJEMPLO RÁPIDO**

```bash
# Setup inicial - Ver estado actual
python category_manager.py list-categories
python category_manager.py list-pages

# Agregar categoría Finanzas
python category_manager.py add-category "Finanzas"

# Agregar páginas de finanzas
python category_manager.py add-page "finance.budget" "Presupuesto" "Finanzas" --roles SUPERADMIN ADMIN
python category_manager.py add-page "finance.expenses" "Gastos" "Finanzas" --roles SUPERADMIN ADMIN SUPERVISOR
python category_manager.py add-page "finance.reports" "Reportes Financieros" "Finanzas" --roles SUPERADMIN ADMIN

# Modificar permisos existentes
python category_manager.py update-permissions "main.dashboard" --roles SUPERADMIN ADMIN SUPERVISOR USUARIO

# Verificar cambios
python category_manager.py list-pages --category "Finanzas"
```

---

### **🔟 TROUBLESHOOTING**

#### **❌ Problemas Comunes**

1. **"Página ya existe"**: Usa `update-permissions` en lugar de `add-page`
2. **"Rol inválido"**: Solo usa: USUARIO, SUPERVISOR, ADMIN, SUPERADMIN
3. **"Error de permisos"**: Ejecuta como administrador si hay problemas de archivos
4. **"Categoría no aparece en web"**: Reinicia el contenedor: `docker-compose restart proyectos_app`

#### **🔄 Reiniciar Contenedor después de Cambios**

```bash
docker-compose restart proyectos_app
```

---

### **✨ PRÓXIMAS FUNCIONALIDADES**

- [ ] Interfaz web completa para gestión
- [ ] Importar/exportar configuraciones
- [ ] Historial de cambios de permisos
- [ ] Notificaciones de cambios de permisos
- [ ] API REST para integración externa
