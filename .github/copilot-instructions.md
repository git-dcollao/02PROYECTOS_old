# Instrucciones para Agentes de IA - Sistema de Gestión de Proyectos

## 🏗️ Arquitectura del Proyecto

### Stack Tecnológico Principal
- **Framework**: Flask 3.0.0 con factory pattern (`create_app()`)
- **ORM**: SQLAlchemy 2.0.23 con Flask-Migrate para migraciones
- **Base de Datos**: MySQL 8.0 (Puerto 3308:3306 en Docker)
- **Autenticación**: Flask-Login + Argon2 para hashing de contraseñas
- **Seguridad**: Flask-WTF CSRF protection (habilitada globalmente)
- **Contenedores**: Docker Compose (app en puerto 5050)

### Estructura de Directorios Crítica
```
app/
├── __init__.py           # Application factory - inicialización central
├── models.py             # ~1750 líneas - modelos monolíticos (Trabajador, Requerimiento, Proyecto, etc.)
├── controllers/          # Blueprints separados por módulo funcional
├── routes/               # Rutas específicas (auth, admin, permissions, emergency)
├── utils/                # Utilidades (dynamic_routes, area_permissions)
├── services/             # Lógica de negocio (menu_service)
└── templates/            # Jinja2 templates con herencia de bases/base.html
```

**⚠️ NOTA CRÍTICA**: `app/models.py` es un archivo monolítico de 1750+ líneas. Existe un único archivo modular en `app/models/administrador_recinto.py` pero el resto permanece en el archivo principal.

## 🔐 Sistema de Permisos (CRÍTICO)

### Modelo de Permisos Unificado
**SIEMPRE usar estos métodos del modelo `Trabajador` (UserMixin):**

```python
# ✅ CORRECTO - Sistema unificado
if current_user.is_superadmin():
    # Usuario con rol SUPERADMIN (único rol inmutable del sistema)
    
if current_user.has_page_permission('/ruta-pagina'):
    # Verificar permisos granulares por página vía tabla user_page_permissions
```

**❌ NUNCA usar:**
- Consultas hardcodeadas: `CustomRole.query.filter(...)`
- Verificaciones directas de roles personalizados
- Lógica de permisos fuera del modelo User

### Tres Niveles de Acceso a Datos
1. **SUPERADMIN**: Acceso total sin filtros
2. **Con permisos de página**: Datos filtrados por `recinto_id` asignado al trabajador
3. **Sin permisos**: Redirección al dashboard con flash message de error

### Patrón Estándar en Endpoints
```python
@blueprint.route('/ruta', methods=['GET', 'POST'])
@login_required
def endpoint():
    # 1. VERIFICAR PERMISOS
    if not (current_user.is_superadmin() or current_user.has_page_permission('/ruta')):
        flash('No tiene permisos para acceder a esta página', 'error')
        return redirect(url_for('main.dashboard'))
    
    # 2. FILTRAR DATOS SEGÚN NIVEL
    if current_user.is_superadmin():
        query = Model.query.all()
    else:
        query = Model.query.filter_by(recinto_id=current_user.recinto_id)
```

## 🎨 Sistema de Estilos Unificado (OBLIGATORIO)

### Arquitectura CSS Global
**CADA página DEBE incluir primero el CSS global:**
```html
<link rel="stylesheet" href="{{ url_for('static', filename='css/modal-styles.css') }}">
<link rel="stylesheet" href="{{ url_for('static', filename='css/nombre-pagina.css') }}">
```

### Clases Globales para Modales
```html
<!-- ESTRUCTURA OBLIGATORIA - Altura automática en todos los modales -->
<div class="modal fade modal-app modal-size-medium modal-auto-height" id="modalId">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header modal-header-app">
                <h5 class="modal-title"><i class="fas fa-icon"></i> Título</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body modal-body-app">
                <form class="modal-edit-form"><!-- Contenido --></form>
            </div>
            <div class="modal-footer modal-footer-app"><!-- Botones --></div>
        </div>
    </div>
</div>
```

**Tamaños disponibles**: `modal-size-small` (400px), `modal-size-medium` (600px), `modal-size-large` (800px), `modal-size-fullscreen` (95%)

**⚠️ OBLIGATORIO**: `modal-auto-height` en TODOS los modales - elimina espacios vacíos y ajusta al contenido

## 🚀 Flujos de Desarrollo Clave

### Crear Nueva Página/Módulo
1. **Controller**: `app/controllers/[modulo]_controller.py` con Blueprint
2. **CSS**: `app/static/css/[modulo].css` (incluir modal-styles.css primero)
3. **Template**: `app/templates/[nombre].html` extendiendo `bases/base.html`
4. **Registro**: Agregar blueprint en `app/__init__.py`
5. **Permisos**: Crear entrada en tabla `pages` y configurar en `/permissions/`

### Sistema de Rutas Dinámicas
Ubicado en `app/utils/dynamic_routes.py` - permite crear rutas desde templates HTML sin código Python adicional. Usar para páginas simples sin lógica compleja.

### Gestión de Backups (Ejemplo del Log)
- **Ruta**: `/admin/backup` (requiere autenticación)
- **Endpoints**: `/admin/backup/list`, `/admin/backup/stats`
- **Logging**: Módulo dedicado con logger `backup` en `app/routes/admin_routes.py`

## 📊 Modelo de Datos Principal

### Entidades Core
- **Trabajador**: Usuario del sistema con UserMixin, roles (SUPERADMIN único inmutable), `custom_role_id`, permisos por página
- **Requerimiento**: Solicitudes de trabajo con estados, prioridades (matriz urgencia/importancia), asignación a trabajadores
- **Proyecto**: Conversión de requerimientos aceptados, con fases, etapas jerárquicas (N1-N4), financiamiento
- **Area/Sector/Recinto**: Jerarquía organizacional (⚠️ en migración de Areas → Sectores/Recintos)
- **Especialidad/Equipo**: Gestión de recursos humanos y equipos de trabajo

### Relaciones Importantes
- Many-to-Many: `requerimiento_trabajador_especialidad` (asignaciones con fecha y estado activo)
- Many-to-Many: `trabajador_areas` (temporal durante migración a sector/recinto)
- Jerarquía Organizacional: Sector → TipoRecinto → Recinto

### Mixins y Utilidades
- **TimestampMixin**: `created_at`, `updated_at` automáticos
- **Enums**: `UserRole` (solo SUPERADMIN), `Prioridad.cuadrante` (1-4)
- **Validaciones**: Argon2 para passwords, formato RUT chileno, colores hexadecimales

## 🐛 Manejo de Errores Común

### Error HTTP 400 (Solicitud Incorrecta)
**Causas típicas en este proyecto:**
1. CSRF token inválido (verificar `csrf.exempt()` en endpoints API)
2. Session expirada (PERMANENT_SESSION_LIFETIME = 3600s)
3. Formulario con datos malformados
4. JSON con Content-Type incorrecto

**Debug**: Revisar logs en `app/__init__.py` → `@app.errorhandler(400)` con logging detallado

### Error 404 para `.well-known/appspecific/com.chrome.devtools.json`
**Es normal** - Chrome DevTools lo solicita automáticamente. El manejador 404 lo registra como WARNING pero no afecta funcionalidad.

### Problemas de Permisos
- Verificar `user_page_permissions` en DB
- Confirmar `current_user.is_active == True`
- Revisar implementación de `has_page_permission()` en `app/models.py` líneas 453+

## 🔧 Comandos Docker Esenciales

```bash
# Iniciar sistema
docker-compose up --build

# Reiniciar solo la app (sin reconstruir)
docker-compose restart proyectos_app

# Migraciones (dentro del contenedor)
docker-compose exec proyectos_app flask db migrate -m "descripción"
docker-compose exec proyectos_app flask db upgrade

# Logs en tiempo real
docker-compose logs -f proyectos_app

# Acceso a shell de la app
docker-compose exec proyectos_app bash
```

**Healthcheck**: `/health` endpoint disponible para verificar estado

## 📝 Convenciones de Código

### Logging Estandarizado
```python
# Inicio de endpoint
print(f"🔍 Endpoint {request.endpoint} llamado por {current_user.email}")

# Éxito con timing
duration = time.time() - start_time
print(f"✅ Página {request.endpoint} cargada en {duration:.3f}s")

# Error con traceback
print(f"❌ Error en {request.endpoint}: {str(e)}")
import traceback
traceback.print_exc()
```

### Blueprint Registration Pattern
```python
# En app/__init__.py
with app.app_context():
    from app.routes.auth_routes import auth_bp
    app.register_blueprint(auth_bp)
```

### UTF-8 Enforcement (MySQL)
```python
@app.before_request
def before_request():
    db.session.execute(text("SET NAMES 'utf8mb4'"))
    db.session.execute(text("SET CHARACTER SET utf8mb4"))
```

## 🚨 Anti-Patrones a Evitar

1. **NO hardcodear credenciales** - usar variables de entorno (.env, .env.local)
2. **NO duplicar estilos CSS** - usar clases globales de modal-styles.css
3. **NO crear modelos fuera de app/models.py** (excepto casos justificados)
4. **NO olvidar @login_required** en rutas protegidas
5. **NO usar alturas fijas en modales** - siempre incluir `modal-auto-height`
6. **NO ignorar la verificación de permisos** - patrón estándar obligatorio

## 📚 Referencias Rápidas

- **Instrucciones detalladas**: `.github/instructions/InstruccionesPROMPT.md` (849 líneas)
- **Configuración**: `config.py` - múltiples ambientes (Development, Testing, Production, Docker)
- **Inicialización**: `init_app.py` - lógica de startup con wait_for_db
- **Seeds**: `app/seeds.py` - datos iniciales del sistema
- **Documentación**: Carpeta `./DOCS` (según convención del proyecto)
- **Tests**: Carpeta `./tests` (pytest + pytest-flask)

---

**Prioridad al código**: Esta aplicación valoriza funcionalidad robusta, seguridad rigurosa y consistencia visual por encima de features experimentales. Al modificar código, siempre priorizar compatibilidad con el sistema de permisos existente y mantener la cohesión de estilos globales.
