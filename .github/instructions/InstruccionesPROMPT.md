---
applyTo: '**'
---
Provide project context and coding guidelines that AI should follow when generating code, answering questions, or reviewing changes.
# Instrucciones para el uso de IA en el proyecto
Este proyecto utiliza IA para asistir en la generación de código, revisión y otras tareas relacionadas. La IA en todo momento debe tener el Rol de Programador Senior. A continuación se detallan las instrucciones y pautas que deben seguirse al interactuar con el código del proyecto.
## Contexto del Proyecto
Este proyecto es una aplicación web desarrollada con Flask, que incluye funcionalidades de gestión de usuarios, roles y permisos. Se utiliza SQLAlchemy para la gestión de la base de datos y Flask-Login para la autenticación de usuarios. La seguridad es una prioridad, por lo que se implementan medidas como CSRF y validaciones de permisos.
## Pautas de Codificación
1. **Consistencia en el Estilo de Código**: Sigue las convenciones de estilo de Python (PEP 8) y las prácticas comunes de Flask. Utiliza nombres descriptivos para variables y funciones.
2. **Manejo de Errores**: 
   - **Manejadores específicos**: Implementar en `app/__init__.py` para CSRFError, 400, 403, 404, 500
   - **Logging seguro**: No fallar al intentar leer JSON/form data - usar try/except
   - **Respuestas diferenciadas**: JSON para APIs, redirects para páginas web
   - **Mensajes usuario-friendly**: Evitar stacktraces en producción
   - **Ubicación de logs**: Crear en la carpeta `./errores` tanto archivos como logs de errores
   - **Debugging**: Incluir información útil (URL, método, usuario) sin exponer datos sensibles
3. **Seguridad**: 
   - **Autenticación**: Todas las rutas críticas DEBEN tener `@login_required`
   - **Permisos**: Verificar permisos usando el sistema unificado (ver sección Gestión de Roles)
   - **CSRF**: Protección automática habilitada - manejar errores CSRFError adecuadamente
   - **Logging de seguridad**: Registrar intentos de acceso no autorizado
   - **Validación de entrada**: Sanitizar y validar todos los datos de entrada
   - **Manejo de errores**: Usar manejadores específicos para errores 400, 403, 404, 500
4. **Modularidad**: Organiza el código en módulos y funciones reutilizables. Evita la duplicación de código y promueve la reutilización.
5. **Documentación**: Documenta todas las funciones y clases con docstrings claros que expliquen su propósito, parámetros y valores de retorno.
Esta documentación quedara respaldada en la carpeta ./DOCS .
6. **Pruebas**: Escribe pruebas unitarias y de integración para las funcionalidades clave del proyecto. Asegúrate de que todas las pruebas pasen antes de fusionar cambios en la rama principal.
Deberan ser creadas en la carpeta ./tests
7. **Revisión de Código**: Antes de fusionar cualquier cambio, realiza una revisión de código para asegurar que cumple con las pautas establecidas y no introduce errores o vulnerabilidades.
## Arquitectura de Endpoints

### Patrón Estándar para Endpoints
```python
@controllers_bp.route('/ruta', methods=['GET', 'POST'])
@login_required
def nombre_endpoint():
    """
    Descripción clara del endpoint
    """
    try:
        # 1. Verificar permisos usando sistema unificado
        if not (current_user.is_superadmin() or current_user.has_page_permission('/ruta')):
            flash('No tiene permisos para acceder a esta página', 'error')
            return redirect(url_for('main.dashboard'))
        
        # 2. Logging para debugging
        print(f"🔍 Endpoint {request.endpoint} llamado por {current_user.email}")
        
        # 3. Lógica de negocio con filtrado por permisos
        # 4. Manejo de respuesta
        
    except Exception as e:
        # 5. Manejo de errores con logging
        print(f"❌ Error en {request.endpoint}: {str(e)}")
        import traceback
        traceback.print_exc()
        flash(f'Error interno: {str(e)}', 'error')
        return redirect(url_for('main.dashboard'))
```

### Filtrado de Datos Automático
- **Implementar en queries**: Filtrar automáticamente según nivel de usuario
- **Tres niveles**: SUPERADMIN (todo), con permisos (filtrado), sin permisos (propio/recinto)
- **Consistency**: Mismo patrón en todas las consultas de datos

### APIs vs Páginas Web
- **APIs**: Devolver JSON con códigos HTTP apropiados
- **Páginas**: Usar flash messages y redirects
- **Logging**: Consistent across both types

## Troubleshooting Común

### Error HTTP 400 "Solicitud incorrecta"
**Causas frecuentes:**
- CSRF token inválido o faltante
- Headers Content-Type incorrectos
- Datos de formulario malformados
- Session expiry durante request

**Debugging:**
1. Verificar logs de app/__init__.py (CSRFError handler)
2. Revisar Network tab en Developer Tools
3. Confirmar that jQuery sends CSRF token
4. Verificar estructura de datos en request

### Errores de Permisos
**Síntomas:**
- Usuarios ven páginas que no deberían
- Redirects inesperados a dashboard
- Flash messages de "No tiene permisos"

**Soluciones:**
1. Verificar implementación de `has_page_permission()`
2. Confirmar datos en tabla user_page_permissions
3. Revisar lógica SUPERADMIN vs permisos específicos
4. Debug con print statements del current_user

### Problemas de Autenticación
**Indicadores:**
- Login loops infinitos
- Session data perdida
- current_user.is_anonymous == True inesperadamente

**Fixes:**
1. Verificar SECRET_KEY en config
2. Confirmar user.is_active == True
3. Revisar session timeout settings
4. Check database user status

## Mejora Continua
Fomenta la mejora continua del código mediante:
- **Modernización gradual**: Migrar endpoints antiguos al sistema unificado de permisos
- **Refactoring**: Eliminar código duplicado y consultas hardcodeadas
- **Monitoring**: Implementar logging detallado para debugging
- **Performance**: Optimizar queries de base de datos
- **Security**: Revisar regularmente permisos y validaciones
## Gestión de Roles y Permisos
**CRÍTICO**: Utiliza EXCLUSIVAMENTE el sistema unificado de permisos modernizado:

### Sistema de Permisos Unificado
- **Usar SIEMPRE**: `current_user.is_superadmin()` y `current_user.has_page_permission('/ruta')`
- **NUNCA usar**: Consultas hardcodeadas como `CustomRole.query.filter()` o verificaciones de roles específicos
- **Patrón estándar**: 
  ```python
  if not (current_user.is_superadmin() or current_user.has_page_permission('/nombre-pagina')):
      flash('No tiene permisos para acceder a esta página', 'error')
      return redirect(url_for('main.dashboard'))
  ```

### Filtrado de Datos por Usuario
- **SUPERADMIN**: Ve todos los datos del sistema
- **Usuarios con permisos de página**: Ven datos filtrados según sus asignaciones de recinto
- **Usuarios regulares**: Ven solo datos de su recinto o que ellos crearon
- **Sin permisos**: Redirección automática al dashboard con mensaje de error

### Mantenimiento del Sistema
- Eliminar gradualmente dependencias de `CustomRole` hardcodeado
- Centralizar toda lógica de permisos en el modelo User
- Aprovechar la interfaz `/permissions/` existente para gestión de permisos
## Se utiliza Docker
Asegúrate de que el entorno de desarrollo y producción esté contenido en contenedores Docker para facilitar la implementación y escalabilidad.
Utilizar un archivo Dockerfile para definir la imagen del contenedor y un archivo docker-compose.yml para orquestar múltiples servicios si es necesario.

### Configuración de Puertos:
- **Aplicación Flask**: Puerto **5050** (http://localhost:5050)
- **Base de datos MySQL**: Puerto **3308:3306** (acceso externo: 3308, interno: 3306)
- **Comando de inicio**: `docker-compose up -d`
- **Comando de reinicio**: `docker-compose restart proyectos_app`

### URLs de Acceso:
- **Aplicación web**: http://localhost:5050
- **Conexión MySQL externa**: localhost:3308
## Uso de Variables de Entorno
Utiliza variables de entorno para gestionar configuraciones sensibles como claves de API, credenciales de base de datos y otros secretos.
Estas instrucciones deben ser seguidas por cualquier IA que interactúe con el código del proyecto para asegurar la coherencia, seguridad y calidad del código generado o modificado.
## Uso de CSS
Utiliza un enfoque modular para el CSS, organizando los estilos en archivos separados por componentes o secciones de la aplicación. Esto facilita el mantenimiento y la escalabilidad del diseño.

## Sistema de Estilos Consistentes 🎨
**CRÍTICO**: Esta aplicación requiere consistencia visual completa entre todas las páginas como una aplicación cohesiva.

### Arquitectura de Estilos Global
**Implementación obligatoria del sistema de estilos unificado:**

#### 📋 **Archivo Principal: `modal-styles.css`**
**Ubicación**: `app/static/css/modal-styles.css`
**Propósito**: Sistema global de estilos para modales y componentes reutilizables

**Estructura del archivo:**
```css
/* Variables CSS Globales */
:root {
    --modal-header-bg: #f8f9fa;
    --modal-primary-color: #007bff;
    --modal-success-color: #28a745;
    --modal-warning-color: #ffc107;
    --modal-danger-color: #dc3545;
    --modal-border-radius: 0.375rem;
    --modal-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
    --modal-transition: all 0.3s ease;
}

/* Sistema de Clases Globales */
.modal-app { /* Clase base para todos los modales de la app */ }
.modal-size-small { /* Modal pequeño - 400px */ }
.modal-size-medium { /* Modal mediano - 600px */ }
.modal-size-large { /* Modal grande - 800px */ }
.modal-size-fullscreen { /* Modal pantalla completa - 95% */ }
.modal-auto-height { /* Altura automática basada en contenido */ }
.modal-edit-form { /* Estilos específicos para formularios de edición */ }
```

#### 🏗️ **Estructura HTML Estandarizada**
**OBLIGATORIO**: Usar la siguiente estructura en TODOS los modales:
**NOTA**: `modal-auto-height` es OBLIGATORIO en todos los casos

```html
<!-- Modal con altura automática OBLIGATORIA -->
<div class="modal fade modal-app modal-size-[tamaño] modal-auto-height" id="modalId" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header modal-header-app">
                <h5 class="modal-title">
                    <i class="fas fa-icon"></i> <!-- Icono consistente -->
                    Título del Modal
                </h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body modal-body-app">
                <form class="modal-edit-form">
                    <!-- Contenido del formulario -->
                    <!-- El modal se ajustará automáticamente al contenido -->
                </form>
            </div>
            <div class="modal-footer modal-footer-app">
                <!-- Botones estandarizados -->
            </div>
        </div>
    </div>
</div>
```

**Ejemplos de uso correcto:**
```html
<!-- Modal pequeño para confirmación -->
<div class="modal fade modal-app modal-size-small modal-auto-height" id="confirmModal">

<!-- Modal mediano para formulario básico -->
<div class="modal fade modal-app modal-size-medium modal-auto-height" id="editModal">

<!-- Modal grande para formulario complejo -->
<div class="modal fade modal-app modal-size-large modal-auto-height" id="detailModal">

<!-- Modal fullscreen para edición completa -->
<div class="modal fade modal-app modal-size-fullscreen modal-auto-height" id="fullEditModal">
```

#### 📐 **Sistema de Tamaños Responsivos**
**OBLIGATORIO: Todos los modales DEBEN usar altura automática por defecto**

**Implementación automática de tamaños:**
- **Small (400px)**: Para confirmaciones simples + `modal-auto-height`
- **Medium (600px)**: Para formularios básicos + `modal-auto-height`
- **Large (800px)**: Para formularios complejos + `modal-auto-height`
- **Fullscreen (95%)**: Para edición detallada + `modal-auto-height`

**⚡ Altura Automática OBLIGATORIA:**
```css
.modal-auto-height .modal-dialog {
    max-height: calc(100vh - 3rem);
    height: auto; /* Se ajusta al contenido */
}
.modal-auto-height .modal-content {
    max-height: calc(100vh - 6rem);
    height: auto; /* Se ajusta al contenido */
}
.modal-auto-height .modal-body {
    max-height: calc(100vh - 200px);
    overflow-y: auto;
    min-height: auto; /* Sin altura mínima forzada */
}
```

**Beneficios de la altura automática:**
- ✅ **Sin espacios vacíos**: Modal se ajusta exactamente al contenido
- ✅ **Mejor UX**: No hay áreas grises innecesarias
- ✅ **Responsive**: Se adapta automáticamente en mobile/tablet
- ✅ **Consistente**: Mismo comportamiento en todos los modales
- ✅ **Eficiente**: Aprovecha mejor el espacio de pantalla

#### 🎯 **Clases de Utilidad Globales**
**Disponibles en toda la aplicación:**

**Layout y Espaciado:**
```css
.modal-grid-2 { /* Grid de 2 columnas responsive */ }
.modal-grid-3 { /* Grid de 3 columnas responsive */ }
.modal-spacing-sm { /* Espaciado pequeño */ }
.modal-spacing-md { /* Espaciado mediano */ }
.modal-spacing-lg { /* Espaciado grande */ }
```

**Componentes de Formulario:**
```css
.modal-input-group { /* Grupos de input consistentes */ }
.modal-select-group { /* Selects estandarizados */ }
.modal-textarea-auto { /* Textareas con altura automática */ }
.modal-btn-group { /* Grupos de botones alineados */ }
```

**Estados Visuales:**
```css
.modal-field-required::after { /* Asterisco rojo para campos requeridos */ }
.modal-field-invalid { /* Estilo para campos con errores */ }
.modal-field-valid { /* Estilo para campos válidos */ }
.modal-loading { /* Estado de carga con spinner */ }
```

#### 🔗 **Integración Obligatoria**
**En CADA template HTML:**

```html
<head>
    <!-- CSS Global OBLIGATORIO - DEBE IR PRIMERO -->
    <link rel="stylesheet" href="{{ url_for('static', filename='css/modal-styles.css') }}">
    
    <!-- CSS específico de página (opcional) -->
    <link rel="stylesheet" href="{{ url_for('static', filename='css/nombre-pagina.css') }}">
</head>
```

#### ⚡ **Responsive Design Automático**
**Breakpoints estandarizados:**
- **Mobile**: < 576px - Stack vertical automático
- **Tablet**: 576px - 768px - Grid adaptativo
- **Desktop**: > 768px - Layout completo

**Implementación automática:**
```css
@media (max-width: 767px) {
    .modal-grid-2, .modal-grid-3 { grid-template-columns: 1fr !important; }
    .modal-size-fullscreen .modal-dialog { margin: 0.5rem; }
    .modal-btn-group { flex-direction: column; gap: 0.5rem; }
}
```

#### 🎨 **Temas y Colores Consistentes**
**Variables CSS para consistencia:**
```css
:root {
    --app-primary: #007bff;
    --app-secondary: #6c757d;
    --app-success: #28a745;
    --app-warning: #ffc107;
    --app-danger: #dc3545;
    --app-light: #f8f9fa;
    --app-dark: #343a40;
}
```

#### 🔧 **Mantenimiento y Extensión**
**Reglas para nuevos componentes:**

1. **NUNCA duplicar estilos** - Usar clases globales existentes
2. **Extender, no reemplazar** - Crear nuevas clases que hereden de las globales
3. **Mantener consistencia** - Seguir patrones establecidos
4. **Documentar cambios** - Actualizar esta documentación al agregar nuevas clases

**Ejemplo de extensión correcta:**
```css
/* En archivo específico de página */
.modal-edit-form.requerimientos-form {
    /* Extensiones específicas para requerimientos */
    background: var(--app-light);
}

.modal-input-group.requerimientos-input {
    /* Personalizaciones que mantienen la base */
    border-left: 3px solid var(--app-primary);
}
```

#### ✅ **Checklist de Implementación**
**Para CADA nueva página o modal:**

- [ ] Incluir `modal-styles.css` ANTES que CSS específico
- [ ] Usar estructura HTML estandarizada con clases globales
- [ ] Aplicar tamaño de modal apropiado (`modal-size-*`)
- [ ] **OBLIGATORIO**: Implementar altura automática (`modal-auto-height`) en TODOS los modales
- [ ] Usar grid responsive para formularios (`modal-grid-*`)
- [ ] Aplicar estilos de botones consistentes
- [ ] Verificar que el modal se ajusta correctamente al contenido (sin espacios vacíos)
- [ ] Probar responsiveness en mobile/tablet/desktop
- [ ] Validar accesibilidad y usabilidad
- [ ] Confirmar que contenido largo muestra scroll automático

#### 🎯 **Objetivos del Sistema**
**Beneficios implementados:**
1. **Consistencia Visual**: Misma apariencia en toda la app
2. **Mantenimiento Reducido**: Cambios centralizados
3. **Desarrollo Rápido**: Clases reutilizables listas
4. **Responsive Automático**: Sin código adicional
5. **Escalabilidad**: Fácil agregar nuevas páginas
6. **Experiencia de Usuario**: Navegación predecible y familiar

**Este sistema es OBLIGATORIO para mantener la cohesión visual de la aplicación.**

## Uso de JavaScript
Emplea JavaScript de manera eficiente, utilizando frameworks o bibliotecas cuando sea apropiado para mejorar la interactividad y la experiencia del usuario. Asegúrate de que el código JavaScript esté bien estructurado y documentado.
Lo ideal es que permanezca en el front-end y no en el back-end.
## Uso de Plantillas HTML
Utiliza plantillas HTML para separar la lógica de presentación del código de la aplicación. Asegúrate de que las plantillas sean limpias, reutilizables y fáciles de mantener.
Emplea un motor de plantillas como Jinja2 para Flask, aprovechando sus características para incluir bloques reutilizables, herencia de plantillas y manejo de variables.
## Internacionalización
Si la aplicación está destinada a usuarios de diferentes regiones, implementa la internacionalización (i18n) para soportar múltiples idiomas y formatos regionales.
## Accesibilidad
Asegúrate de que la aplicación cumpla con las pautas de accesibilidad web (WCAG) para garantizar que sea usable por personas con discapacidades.
## Optimización del Rendimiento
Optimiza el rendimiento de la aplicación mediante técnicas como la minimización de archivos CSS y JavaScript, el uso de caché y la optimización de consultas a la base de datos.
## Monitoreo y Registro
Implementa un sistema de monitoreo y registro para rastrear el rendimiento de la aplicación y detectar problemas de manera proactiva. Utiliza herramientas como Prometheus, Grafana o ELK Stack para recopilar y visualizar métricas y registros.
## Actualización de Dependencias
Mantén las dependencias del proyecto actualizadas para beneficiarte de las últimas características, mejoras de rendimiento y correcciones de seguridad. Utiliza herramientas como Dependabot o Renovate para automatizar este proceso.
## Cumplimiento Legal
Asegúrate de que la aplicación cumpla con las leyes y regulaciones aplicables, como GDPR para la protección de datos personales. Implementa políticas de privacidad y términos de servicio claros para los usuarios.
## Colaboración en Equipo
Fomenta una cultura de colaboración en el equipo de desarrollo mediante el uso de herramientas de gestión de proyectos, comunicación efectiva y revisiones de código regulares.
Utiliza plataformas como GitHub, Jira o Trello para organizar tareas, rastrear el progreso y facilitar la comunicación entre los miembros del equipo.
## Control de Versiones
Utiliza un sistema de control de versiones como Git para gestionar el código fuente del proyecto. Asegúrate de seguir una estrategia de ramificación clara, como Git Flow o GitHub Flow, para facilitar la colaboración y la integración continua.
## Integración Continua y Despliegue Continuo (CI/CD)
Implementa pipelines de CI/CD para automatizar la construcción, prueba y despliegue de la aplicación. Utiliza herramientas como GitHub Actions, Jenkins o GitLab CI para configurar estos procesos.
Esto asegura que los cambios en el código se integren de manera fluida y se desplieguen rápidamente a los entornos de desarrollo, prueba y producción.
## Documentación
Mantén una documentación completa y actualizada del proyecto, incluyendo guías de instalación, configuración, uso y contribución. Utiliza herramientas como GitHub Wiki para organizar y presentar la documentación de manera accesible.

## Arquitectura de Archivos CSS y Controllers

### Organización de CSS
**OBLIGATORIO**: Cada página DEBE tener su propio archivo CSS dedicado:
- **Ubicación**: `app/static/css/[nombre-pagina].css`
- **Nomenclatura**: Usar nombres descriptivos que coincidan con la funcionalidad
- **Estructura**: Organizar estilos por componentes dentro del archivo
- **Importación**: Incluir en el template usando `{{ url_for('static', filename='css/[nombre-pagina].css') }}`

**Si no existe el archivo CSS**: Crear automáticamente con estructura base:
```css
/* [Nombre de la Página] - Estilos Específicos */

/* ==== LAYOUT PRINCIPAL ==== */
.container-[nombre] {
    /* Estilos del contenedor principal */
}

/* ==== COMPONENTES ==== */
.header-[nombre] {
    /* Estilos del header específico */
}

.table-[nombre] {
    /* Estilos de tablas específicos */
}

.form-[nombre] {
    /* Estilos de formularios específicos */
}

/* ==== ESTADOS Y INTERACCIONES ==== */
.btn-[nombre]:hover {
    /* Estilos de hover */
}

/* ==== RESPONSIVE ==== */
@media (max-width: 768px) {
    /* Estilos responsive */
}
```

### Organización de Controllers
**OBLIGATORIO**: Cada módulo funcional DEBE tener su propio controller separado:
- **Ubicación**: `app/controllers/[nombre-modulo]_controller.py`
- **Nomenclatura**: Usar nombres descriptivos seguidos de `_controller`
- **Importación**: Registrar blueprint en `app/__init__.py`
- **Estructura**: Un controller por área funcional (ej: requerimientos, usuarios, proyectos)

**Si no existe el controller**: Crear automáticamente con estructura base:
```python
"""
[Nombre del Módulo] Controller
Maneja todas las operaciones CRUD y lógica de negocio para [módulo]
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.models import db, [ModelosPrincipal]
from app.utils.area_permissions import verificar_permiso
import time

# Blueprint definition
[nombre]_bp = Blueprint('[nombre]', __name__)

@[nombre]_bp.route('/[ruta-principal]', methods=['GET'], endpoint='index')
@login_required
def index():
    """
    Página principal del módulo [nombre]
    """
    start_time = time.time()
    
    try:
        # 1. Verificar permisos
        if not (current_user.is_superadmin() or current_user.has_page_permission('/[ruta-principal]')):
            flash('No tiene permisos para acceder a esta página', 'error')
            return redirect(url_for('main.dashboard'))
        
        # 2. Logging
        print(f"🔍 Acceso a {request.endpoint} por usuario {current_user.id}")
        
        # 3. Lógica de negocio
        # TODO: Implementar consultas y filtrado
        
        # 4. Render template
        duration = time.time() - start_time
        print(f"✅ Página {request.endpoint} cargada en {duration:.3f}s")
        
        return render_template('[nombre].html', 
                             css_file='[nombre].css',
                             js_file='[nombre].js')
        
    except Exception as e:
        # 5. Manejo de errores
        print(f"❌ Error en {request.endpoint}: {str(e)}")
        import traceback
        traceback.print_exc()
        flash(f'Error interno: {str(e)}', 'error')
        return redirect(url_for('main.dashboard'))

# TODO: Agregar endpoints CRUD adicionales (create, read, update, delete)
```

## Páginas de la Aplicación - Especificaciones Detalladas

### 📊 **Páginas de Dashboard y Navegación**

#### `dashboard.html` - Panel Principal
**Propósito**: Dashboard ejecutivo con métricas clave y navegación principal
**Controller**: `app/controllers/dashboard_controller.py` (crear si no existe)
**CSS**: `app/static/css/dashboard.css` (crear si no existe)
**Funcionalidades**:
- Mostrar métricas principales (proyectos activos, requerimientos pendientes, trabajadores)
- Gráficos de estado de proyectos y requerimientos
- Accesos rápidos a funciones principales
- Panel de notificaciones y alertas
- Filtros por recinto para usuarios no-admin

#### `home.html` - Página de Inicio
**Propósito**: Página de bienvenida y acceso inicial
**Controller**: `app/controllers/home_controller.py` (crear si no existe)
**CSS**: `app/static/css/home.css` ✅ (existe)
**Funcionalidades**:
- Bienvenida personalizada por usuario
- Resumen de actividades recientes
- Navegación rápida por rol
- Estado del sistema

### 🏗️ **Páginas de Gestión de Proyectos**

#### `requerimiento-aceptar.html` - Aceptación de Requerimientos
**Propósito**: Interfaz para aceptar y asignar requerimientos
**Controller**: `app/controllers/requerimientos_controller.py` (crear si no existe)
**CSS**: `app/static/css/requerimientos.css` ✅ (existe)
**Funcionalidades**:
- Lista de requerimientos pendientes de aceptación
- Formulario de aceptación con asignación de recursos
- Filtros por estado, fecha, prioridad
- Validaciones de disponibilidad de trabajadores
- Sistema de aprobación jerárquica

#### `requerimiento-completar.html` - Completar Requerimientos
**Propósito**: Interfaz para marcar requerimientos como completados
**Controller**: `app/controllers/requerimientos_controller.py` (usar existente)
**CSS**: `app/static/css/requerimientos.css` ✅ (existe)
**Funcionalidades**:
- Lista de requerimientos en progreso
- Formulario de completar con evidencias
- Upload de archivos/fotos
- Validación de requisitos completados
- Generación de reportes de finalización

#### `proyecto-aceptar.html` - Aceptación de Proyectos
**Propósito**: Interfaz para aceptar y planificar proyectos
**Controller**: `app/controllers/proyectos_controller.py` (crear si no existe)
**CSS**: `app/static/css/proyectos.css` (crear si no existe)
**Funcionalidades**:
- Lista de proyectos pendientes
- Formulario de aceptación con planificación
- Asignación de equipos y recursos
- Definición de cronograma y etapas
- Validaciones de viabilidad

#### `proyecto-completar.html` - Completar Proyectos
**Propósito**: Gestión de finalización de proyectos
**Controller**: `app/controllers/proyectos_controller.py` (usar existente)
**CSS**: `app/static/css/proyecto-completar.css` ✅ (existe)
**Funcionalidades**:
- Seguimiento de avance por etapas
- Validación de entregables
- Cierre administrativo
- Generación documentación final
- Evaluación post-proyecto

#### `proyecto-llenar.html` - Formulario de Proyectos
**Propósito**: Creación y edición de proyectos
**Controller**: `app/controllers/proyectos_controller.py` (usar existente)
**CSS**: `app/static/css/proyectos.css` (crear si no existe)
**Funcionalidades**:
- Formulario completo de creación
- Wizard paso a paso
- Validaciones en tiempo real
- Guardado temporal (drafts)
- Previsualización antes de envío

### 📈 **Páginas de Seguimiento y Control**

#### `avance-actividades.html` - Control de Avances
**Propósito**: Seguimiento detallado de actividades y progreso
**Controller**: `app/controllers/avances_controller.py` (crear si no existe)
**CSS**: `app/static/css/avance-actividades.css` ✅ (existe)
**Funcionalidades**:
- Timeline de actividades por proyecto
- Registro de avances con porcentajes
- Comparación planificado vs real
- Alertas de retrasos
- Reportes de productividad

#### `avance-actividades-all.html` - Vista General de Avances
**Propósito**: Vista consolidada de todos los avances
**Controller**: `app/controllers/avances_controller.py` (usar existente)
**CSS**: `app/static/css/avance-actividades.css` ✅ (usar existente)
**Funcionalidades**:
- Dashboard consolidado de avances
- Filtros por proyecto, trabajador, fecha
- Métricas de rendimiento global
- Exportación de reportes
- Análisis comparativo

#### `control-actividades.html` - Control de Actividades
**Propósito**: Gestión y control operativo de actividades
**Controller**: `app/controllers/control_controller.py` (crear si no existe)
**CSS**: `app/static/css/control-actividades.css` (crear si no existe)
**Funcionalidades**:
- Lista de actividades programadas
- Asignación y reasignación de tareas
- Control de tiempo y recursos
- Estado de actividades en tiempo real
- Intervenciones y correcciones

#### `historial-avances.html` - Historial de Avances
**Propósito**: Registro histórico y auditoría de avances
**Controller**: `app/controllers/historial_controller.py` (crear si no existe)
**CSS**: `app/static/css/historial.css` (crear si no existe)
**Funcionalidades**:
- Log completo de cambios y avances
- Filtros por período, usuario, proyecto
- Trazabilidad de modificaciones
- Exportación de historiales
- Análisis de tendencias

### 📊 **Páginas de Planificación**

#### `gantt-*.html` - Diagramas de Gantt
**Propósito**: Visualización y gestión de cronogramas
**Controller**: `app/controllers/gantt_controller.py` (crear si no existe)
**CSS**: `app/static/css/gantt.css` (crear si no existe)
**Funcionalidades**:
- Diagrama interactivo de Gantt
- Drag & drop para reprogramación
- Vista por proyecto y general
- Dependencias entre tareas
- Exportación a PDF/Excel

### 👥 **Páginas de Gestión de Recursos Humanos**

#### `trabajadores.html` - Gestión de Trabajadores
**Propósito**: CRUD de trabajadores y gestión de equipos
**Controller**: `app/controllers/trabajadores_controller.py` (crear si no existe)
**CSS**: `app/static/css/trabajadores.css` (crear si no existe)
**Funcionalidades**:
- Lista paginada de trabajadores
- Formularios de alta/baja/modificación
- Asignación de especialidades y recintos
- Control de disponibilidad
- Gestión de permisos y roles

#### `trabajadores_admin.html` - Administración de Trabajadores
**Propósito**: Panel administrativo para gestión avanzada
**Controller**: `app/controllers/trabajadores_admin_controller.py` (crear si no existe)
**CSS**: `app/static/css/trabajadores-admin.css` (crear si no existe)
**Funcionalidades**:
- Vista administrativa completa
- Bulk operations (operaciones masivas)
- Reportes de nómina y asistencia
- Configuración de roles y permisos
- Auditoría de cambios

#### `equipo.html` - Gestión de Equipos
**Propósito**: Organización y gestión de equipos de trabajo
**Controller**: `app/controllers/equipos_controller.py` (crear si no existe)
**CSS**: `app/static/css/equipos.css` (crear si no existe)
**Funcionalidades**:
- Creación y edición de equipos
- Asignación de líderes y miembros
- Balance de cargas de trabajo
- Métricas de rendimiento por equipo
- Rotación y reasignaciones

### 🏢 **Páginas de Configuración Organizacional**

#### `areas.html` - Gestión de Áreas
**Propósito**: CRUD de áreas organizacionales
**Controller**: `app/controllers/areas_controller.py` (crear si no existe)
**CSS**: `app/static/css/areas.css` (crear si no existe)
**Funcionalidades**:
- Lista y edición de áreas
- Jerarquía organizacional
- Asignación de responsables
- Métricas por área
- Configuración de permisos por área

#### `recintos.html` - Gestión de Recintos
**Propósito**: CRUD de recintos y ubicaciones
**Controller**: `app/controllers/recintos_controller.py` (crear si no existe)
**CSS**: `app/static/css/recintos.css` (crear si no existe)
**Funcionalidades**:
- Registro de recintos y ubicaciones
- Tipos de recinto y características
- Asignación de administradores
- Capacidades y recursos disponibles
- Mapeo y geolocalización

#### `sector.html` - Gestión de Sectores
**Propósito**: CRUD de sectores operativos
**Controller**: `app/controllers/sectores_controller.py` (crear si no existe)
**CSS**: `app/static/css/sectores.css` (crear si no existe)
**Funcionalidades**:
- Definición de sectores operativos
- Asignación de recursos por sector
- Cobertura geográfica
- Métricas de rendimiento sectorial
- Coordinación inter-sectorial

### ⚙️ **Páginas de Configuración del Sistema**

#### `especialidades.html` - Gestión de Especialidades
**Propósito**: CRUD de especialidades técnicas
**Controller**: `app/controllers/especialidades_controller.py` (crear si no existe)
**CSS**: `app/static/css/especialidades.css` (crear si no existe)
**Funcionalidades**:
- Catálogo de especialidades técnicas
- Requisitos y certificaciones
- Niveles de competencia
- Asignación a trabajadores
- Demanda vs disponibilidad

#### `estados.html` - Gestión de Estados
**Propósito**: Configuración de estados del sistema
**Controller**: `app/controllers/estados_controller.py` (crear si no existe)
**CSS**: `app/static/css/estados.css` (crear si no existe)
**Funcionalidades**:
- Estados de proyectos y requerimientos
- Flujos de trabajo (workflows)
- Transiciones permitidas
- Colores y iconografía
- Notificaciones por cambio de estado

#### `etapas.html` - Gestión de Etapas
**Propósito**: Configuración de etapas de proyecto
**Controller**: `app/controllers/etapas_controller.py` (crear si no existe)
**CSS**: `app/static/css/etapas.css` (crear si no existe)
**Funcionalidades**:
- Definición de etapas estándar
- Secuencias y dependencias
- Criterios de avance
- Templates de etapas
- Métricas por etapa

### 💰 **Páginas de Gestión Financiera**

#### `financiamientos.html` - Gestión de Financiamientos
**Propósito**: Control de presupuestos y financiamiento
**Controller**: `app/controllers/financiamientos_controller.py` (crear si no existe)
**CSS**: `app/static/css/financiamientos.css` (crear si no existe)
**Funcionalidades**:
- Registro de fuentes de financiamiento
- Presupuestos por proyecto
- Control de gastos y desviaciones
- Reportes financieros
- Alertas de límites presupuestarios

#### `prioridades.html` - Gestión de Prioridades
**Propósito**: Sistema de priorización de trabajos
**Controller**: `app/controllers/prioridades_controller.py` (crear si no existe)
**CSS**: `app/static/css/prioridades.css` (crear si no existe)
**Funcionalidades**:
- Matriz de priorización
- Criterios de urgencia e importancia
- Asignación automática de prioridades
- Rebalanceo dinámico
- Reportes de cumplimiento por prioridad

## Reglas Clave que debes seguir siempre
📁 Estructura de Archivos Obligatoria:
1. Tests → tests
- Todos los archivos de prueba van en tests
- Naming: test_[modulo]_[funcionalidad].py
- Incluir tests unitarios E integración

2. CSS → app/static/css/[nombre-pagina].css
- **OBLIGATORIO**: Incluir SIEMPRE `modal-styles.css` ANTES del CSS específico
- **Estructura**: `<link rel="stylesheet" href="{{ url_for('static', filename='css/modal-styles.css') }}">`
- Cada página debe tener su propio CSS en caso de ser necesario, ya que deben tener un estilo parecido por ser una APP
- Crear automáticamente si no existe
- Estructura modular por componentes
- **Usar clases globales**: modal-app, modal-size-*, modal-auto-height, modal-edit-form
- **Mantener consistencia**: Seguir patrones del sistema global de estilos

3. Controllers → app/controllers/[modulo]_controller.py
- Un controller por área funcional
-Blueprint separado para cada módulo
- Registrar en __init__.py

4. Documentación → DOCS
- Toda documentación va en carpeta DOCS
- Docstrings obligatorios en funciones

5. Logs de Error → ./errores/
- Crear carpeta errores para logs
- Manejo específico de errores por tipo

🎨 Sistema de Estilos Consistentes:
- **OBLIGATORIO**: Incluir modal-styles.css en TODAS las páginas
- **NUNCA duplicar estilos**: Usar clases globales existentes
- **Estructura HTML**: Seguir patrón estandarizado con clases modal-app
- **Responsiveness**: Usar modal-grid-* para layouts automáticos
- **Tamaños**: Aplicar modal-size-* según necesidad del contenido
- **Altura automática OBLIGATORIA**: TODOS los modales deben usar modal-auto-height
- **Sin espacios vacíos**: Los modales se deben ajustar exactamente al contenido
- **Mantener cohesión**: La app debe verse uniforme en todas las páginas

🛡️ Seguridad y Permisos:
- SIEMPRE usar @login_required
- SIEMPRE verificar permisos con current_user.is_superadmin() o current_user.has_page_permission()
- NUNCA usar consultas hardcodeadas de roles
- Implementar manejo específico de CSRFError

🏗️ Arquitectura de Endpoints:
@blueprint.route('/ruta', methods=['GET', 'POST'])
@login_required
def endpoint():
    """Docstring obligatorio"""
    try:
        # 1. Verificar permisos
        # 2. Logging
        # 3. Lógica de negocio
        # 4. Render template
    except Exception as e:
        # 5. Manejo de errores
