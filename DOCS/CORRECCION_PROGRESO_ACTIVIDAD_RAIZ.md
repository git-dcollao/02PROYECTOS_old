# 🎯 Corrección: Obtención del Progreso del Proyecto desde Actividad Raíz

**Fecha**: 15 de enero de 2026  
**Archivos Modificados**: `app/controllers_main.py`  
**Endpoints Afectados**: `/proyectos_estado_4`, `/proyecto_detalle/<proyecto_id>`

---

## ❌ Problema Identificado

Anteriormente, ambos endpoints calculaban el progreso del proyecto mediante un **promedio aritmético simple** de TODAS las actividades:

```python
# ❌ INCORRECTO - Calculaba promedio de todas las actividades
progreso_total = sum([float(act.progreso) for act in actividades_proyecto if act.progreso is not None])
progreso_promedio = round(progreso_total / total_actividades, 1)
```

### Problemas de este enfoque:

1. **❌ Duplicación de cálculos**: El progreso ya está calculado y propagado en la jerarquía EDT
2. **❌ Valores inconsistentes**: Diferentes momentos de consulta daban valores diferentes (12.1% vs 13%)
3. **❌ No respeta la jerarquía**: Suma actividades padre e hijas, contando dos veces el mismo progreso
4. **❌ No pondera correctamente**: Trata igual una tarea de 1 día que una de 30 días

### Ejemplo del problema:

```
Proyecto con 3 actividades:
- Actividad raíz (EDT: 1) - Progreso calculado: 13%
- Sub-actividad 1 (EDT: 1.1) - Progreso: 20%
- Sub-actividad 2 (EDT: 1.2) - Progreso: 6%

Cálculo INCORRECTO anterior:
(13 + 20 + 6) / 3 = 13% ✅ Por casualidad coincide

Pero si hay más niveles:
- EDT 1 (raíz) - 13%
- EDT 1.1 - 20%
- EDT 1.1.1 - 30%
- EDT 1.1.2 - 10%
- EDT 1.2 - 6%

Cálculo INCORRECTO:
(13 + 20 + 30 + 10 + 6) / 5 = 15.8% ❌ INCORRECTO

Valor CORRECTO (desde EDT 1):
13% ✅ Ya está calculado y propagado
```

---

## ✅ Solución Implementada

Ahora ambos endpoints **obtienen el progreso directamente de la actividad raíz** (nivel EDT 1):

```python
# ✅ CORRECTO - Obtiene progreso de la actividad raíz
actividad_raiz = next(
    (act for act in actividades_proyecto if act.nivel_esquema == 1),
    None
)

if actividad_raiz and actividad_raiz.progreso is not None:
    progreso_promedio = round(float(actividad_raiz.progreso), 1)
else:
    # Fallback para casos legacy sin actividad raíz
    if total_actividades > 0:
        progreso_total = sum([float(act.progreso) for act in actividades_proyecto if act.progreso is not None])
        progreso_promedio = round(progreso_total / total_actividades, 1)
    else:
        progreso_promedio = 0
```

---

## 🔄 Flujo Completo del Progreso

### 1. Trabajador Reporta Avance
```
Trabajador A reporta 60% en actividad EDT 1.1.1
    ↓
Tabla: avance_actividad
    progreso_actual = 60%
```

### 2. Supervisor Valida
```
Supervisor valida el 60%
    ↓
calcular_progreso_actividad(1.1.1)
    → Calcula promedio ponderado por horas de trabajadores
    → Resultado: 53% (considera asignaciones)
    ↓
Actualiza: actividad_proyecto.progreso (EDT 1.1.1) = 53%
```

### 3. Propagación Jerárquica
```
recalcular_padres_recursivo("1.1.1")
    ↓
Calcula EDT 1.1 (padre)
    → Promedio ponderado por duración de hijas (1.1.1, 1.1.2, etc.)
    → Resultado: 45%
    → Actualiza: actividad_proyecto.progreso (EDT 1.1) = 45%
    ↓
Calcula EDT 1 (raíz)
    → Promedio ponderado por duración de hijas (1.1, 1.2, 1.3, etc.)
    → Resultado: 35%
    → Actualiza: actividad_proyecto.progreso (EDT 1) = 35%
```

### 4. Consulta del Progreso del Proyecto
```
GET /proyectos_estado_4 o /proyecto_detalle/123
    ↓
Busca actividad_proyecto WHERE nivel_esquema = 1
    ↓
Retorna actividad_raiz.progreso = 35%
```

---

## 📊 Ventajas del Nuevo Enfoque

### 1. **Consistencia Absoluta** 🎯
- Mismo valor en listado y detalle
- No importa cuándo se consulte
- Una única fuente de verdad

### 2. **Rendimiento Mejorado** ⚡
- No calcula nada, solo lee un valor
- Mucho más rápido (1 lectura vs N sumas)
- Menos carga en la base de datos

### 3. **Respeta la Arquitectura** 🏗️
- Usa el sistema de jerarquía EDT correctamente
- No duplica cálculos ya realizados
- Mantiene la integridad del modelo

### 4. **Ponderación Correcta** ⚖️
- El progreso raíz ya considera:
  - ✅ Duración de cada actividad
  - ✅ Horas asignadas a trabajadores
  - ✅ Porcentaje de asignación
  - ✅ Jerarquía completa

---

## 🔧 Cambios Adicionales

### Filtrado de Actividades Activas
En `/proyecto_detalle` se agregó el filtro `activo=True`:

```python
# ANTES
actividades = db.session.query(ActividadProyecto)\
    .filter(ActividadProyecto.requerimiento_id == proyecto_id)\
    .all()

# AHORA
actividades = db.session.query(ActividadProyecto)\
    .filter(ActividadProyecto.requerimiento_id == proyecto_id)\
    .filter(ActividadProyecto.activo == True)\  # ✅ Solo activas
    .all()
```

Esto asegura que solo se consideren actividades activas, igual que en `/proyectos_estado_4`.

---

## 📝 Logging Mejorado

Se agregó logging en `/proyecto_detalle` para debugging:

```python
if actividad_raiz and actividad_raiz.progreso is not None:
    progreso_promedio = round(float(actividad_raiz.progreso), 1)
    print(f"✅ Progreso obtenido de actividad raíz (EDT: {actividad_raiz.edt}): {progreso_promedio}%")
else:
    print(f"⚠️ No se encontró actividad raíz para proyecto {proyecto_id}, calculando promedio")
```

Esto ayuda a identificar:
- ✅ Cuándo se usa correctamente la actividad raíz
- ⚠️ Cuándo se usa el fallback (proyectos legacy)

---

## 🧪 Casos de Prueba

### Caso 1: Proyecto con Jerarquía Completa
```
EDT 1 (raíz) → progreso = 35%
├─ EDT 1.1 → progreso = 45%
│  ├─ EDT 1.1.1 → progreso = 53%
│  └─ EDT 1.1.2 → progreso = 37%
└─ EDT 1.2 → progreso = 25%

ANTES: (35 + 45 + 53 + 37 + 25) / 5 = 39% ❌
AHORA: 35% (de EDT 1) ✅
```

### Caso 2: Proyecto Legacy sin Actividad Raíz
```
Actividades sin nivel_esquema = 1
↓
Usa fallback: calcula promedio simple
↓
Muestra warning en logs
```

### Caso 3: Proyecto sin Actividades
```
No hay actividades
↓
progreso_promedio = 0%
```

---

## 🎯 Impacto en la Interfaz

### Antes:
```
Listado:  12.1% (calculado al cargar)
Detalle:  13.0% (calculado al abrir modal)
❌ Inconsistente
```

### Ahora:
```
Listado:  13.0% (leído de EDT 1)
Detalle:  13.0% (leído de EDT 1)
✅ Consistente
```

---

## 🚀 Mejoras Futuras Sugeridas

### 1. Agregar Índice en `nivel_esquema`
```sql
CREATE INDEX idx_actividad_proyecto_nivel_esquema 
ON actividad_proyecto(requerimiento_id, nivel_esquema, activo);
```

Esto optimizará la búsqueda de la actividad raíz.

### 2. Cachear el Progreso en `requerimiento`
Agregar un campo `progreso_calculado` en la tabla `requerimiento`:

```python
# Al validar avances
proyecto.progreso_calculado = actividad_raiz.progreso
db.session.commit()

# En las consultas
progreso_promedio = proyecto.progreso_calculado or 0
```

Esto eliminaría la necesidad de buscar la actividad raíz.

### 3. Validación en el Sistema
Agregar validación para asegurar que todo proyecto tenga una actividad raíz:

```python
def validar_estructura_proyecto(proyecto_id):
    actividad_raiz = ActividadProyecto.query.filter_by(
        requerimiento_id=proyecto_id,
        nivel_esquema=1,
        activo=True
    ).first()
    
    if not actividad_raiz:
        raise ValueError(f"Proyecto {proyecto_id} sin actividad raíz (nivel_esquema=1)")
```

---

## 📚 Referencias

- [Sistema de Cálculo de Avances](./explicacion_calculo_%_avances.md)
- [Mejora del Historial de Correcciones](./MEJORA_HISTORIAL_CORRECCIONES.md)
- [Jerarquía EDT en `controllers_main.py`](../app/controllers_main.py#L4259-L4306)

---

**Implementado por**: Sistema de Gestión de Proyectos  
**Versión**: 2.1 - Progreso desde Actividad Raíz  
**Estado**: ✅ Completado y Probado
