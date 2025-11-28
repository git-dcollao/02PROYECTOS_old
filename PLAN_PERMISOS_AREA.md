# 🚀 PLAN DE IMPLEMENTACIÓN: SISTEMA DE PERMISOS POR ÁREA

## 📋 Análisis de Requerimientos

### Funcionalidad Requerida:
- Restringir página `/trabajadores` por área
- Solo administradores del área pueden ver/administrar sus trabajadores
- Soporte para trabajadores con múltiples áreas
- Soporte para múltiples roles por trabajador

## 🏗️ Arquitectura Propuesta

### 1. **Modelo de Datos Actual**
```python
# ✅ YA EXISTE
class Area(db.Model):
    id, nombre, descripcion, activo
    trabajadores = relationship('Trabajador')

class Trabajador(db.Model):
    area_id = ForeignKey('area.id')  # ✅ YA EXISTE
    rol = Enum(UserRole)             # ✅ YA EXISTE
    area = relationship('Area')      # ✅ YA EXISTE
```

### 2. **Extensiones Necesarias**

#### Opción A: Tabla Many-to-Many (Recomendada)
```python
# NUEVA TABLA: trabajador_areas
class TrabajadorArea(db.Model):
    trabajador_id = ForeignKey('trabajador.id')
    area_id = ForeignKey('area.id')
    rol_en_area = Enum(RolArea)  # ADMIN_AREA, MIEMBRO, etc.
    es_principal = Boolean       # Área principal del trabajador
```

#### Opción B: Mantener Simple (Más rápida)
```python
# Solo usar area_id existente + nuevo campo rol_area
class Trabajador(db.Model):
    # ... campos existentes
    es_admin_area = Boolean  # Si es admin de su área
```

### 3. **Sistema de Autorización**

```python
# DECORADOR DE PERMISOS
@area_permission_required(['admin_area', 'superadmin'])
def trabajadores():
    # Filtrar trabajadores según área del usuario
    pass

# FUNCIÓN DE FILTRADO
def get_trabajadores_permitidos(current_user):
    if current_user.rol == UserRole.SUPERADMIN:
        return Trabajador.query.all()
    elif current_user.es_admin_area:
        return Trabajador.query.filter_by(area_id=current_user.area_id).all()
    else:
        return []  # Sin permisos
```

### 4. **Interfaz de Usuario**

```html
<!-- FILTROS POR ÁREA -->
<div class="area-filter">
    <select id="areaFilter">
        {% for area in areas_permitidas %}
        <option value="{{ area.id }}">{{ area.nombre }}</option>
        {% endfor %}
    </select>
</div>

<!-- TABLA CON TRABAJADORES FILTRADOS -->
<table>
    {% for trabajador in trabajadores_filtrados %}
    <tr>
        <td>{{ trabajador.nombre }}</td>
        <td>{{ trabajador.area.nombre }}</td>
        <td>
            {% if can_edit_trabajador(trabajador) %}
            <button>Editar</button>
            {% endif %}
        </td>
    </tr>
    {% endfor %}
</table>
```

## 🎯 Preguntas Pendientes

1. **Modelo de Datos**: ¿Prefieres many-to-many completo o mantener simple?
2. **Roles**: ¿Crear nuevo rol ADMIN_AREA o usar flag booleano?
3. **Permisos**: ¿Qué acciones específicas por rol?
4. **UI/UX**: ¿Filtros por área, pestañas, o vista unificada?

## 📝 Siguiente Pasos

1. Definir modelo exacto según respuestas
2. Crear migraciones de base de datos
3. Implementar sistema de autorización
4. Actualizar controladores
5. Modificar interfaz de usuario
6. Crear tests unitarios

---
**Tiempo estimado**: 2-3 horas
**Complejidad**: Media-Alta
**Impacto**: Alto (mejora significativa de seguridad)
