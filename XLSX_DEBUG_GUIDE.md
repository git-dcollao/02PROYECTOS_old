# Guía de Depuración para Archivos XLSX

## Problema Solucionado

Se ha solucionado el problema donde al subir archivos XLSX mostraba "0 actividades procesadas" con "10 filas con errores".

## Mejoras Implementadas

### 1. Corrección de Campos del Modelo
- ❌ **Problema**: Se intentaba usar `fecha_creacion` y `fecha_actualizacion` que no existen
- ✅ **Solución**: Los campos timestamp se manejan automáticamente por `TimestampMixin` (`created_at`, `updated_at`)

### 2. Validaciones Mejoradas
- Validación de longitud de campos (EDT: máx 50 chars, Nombre: máx 500 chars)
- Validación de fechas requeridas (no pueden ser nulas)
- Validación de progreso en rango válido (0-999.99%)
- Validación de columnas mínimas requeridas

### 3. Logging Mejorado
- Muestra las primeras 2 filas del archivo para debug
- Detalla errores específicos con stack trace
- Resumen final del procesamiento
- Lista las columnas disponibles vs requeridas

### 4. Manejo de Errores Específicos
- Error al crear actividad con detalles completos
- Error de commit a base de datos con traceback
- Verificación de filas vacías

## Columnas Requeridas en el XLSX

### Obligatorias:
- **EDT** / **WBS** / **E.D.T.**: Código único de la actividad
- **Nombre de tarea** / **Actividad** / **Task Name**: Nombre descriptivo
- **Comienzo** / **Inicio** / **Start**: Fecha de inicio
- **Fin** / **End** / **Finish**: Fecha de finalización

### Opcionales:
- **Duración** / **Duration**: Días de duración
- **Progreso** / **Progress** / **% Completado**: Porcentaje de avance
- **Recursos** / **Resource Names**: Trabajadores asignados
- **Nivel de esquema** / **Level**: Nivel jerárquico

## Formato de Datos Esperado

### Fechas:
- Formato: DD/MM/YYYY, MM/DD/YYYY, o YYYY-MM-DD
- Ejemplo: 01/12/2024, 2024-12-01

### EDT:
- Máximo 50 caracteres
- Debe ser único por proyecto
- Ejemplo: 1.1, A-001, FASE1-ACT01

### Progreso:
- Valores entre 0% y 100%
- Puede incluir símbolo % o ser decimal (0.5 = 50%)

### Recursos:
- Nombres o códigos de trabajadores separados por comas
- Ejemplo: "JPerez, MRodriguez"

## Cómo Verificar Problemas

### 1. Revisar Console de Navegador
1. Presiona F12 en el navegador
2. Ve a la pestaña "Console"
3. Busca mensajes que empiecen con 📊, ❌, ✅

### 2. Revisar Logs del Servidor
Los logs mostrarán:
```
📊 Procesando X filas del archivo Gantt
📋 Columnas disponibles en el archivo: [...]
📄 Primeras 2 filas del archivo para referencia:
📋 Columnas encontradas después del mapeo: {...}
✅ Actividad creada con ID: X - EDT: X - Nombre: X
📊 Resultado final del procesamiento:
```

### 3. Errores Comunes y Soluciones

#### "No se encontraron las columnas requeridas"
- Verificar que las columnas tengan nombres válidos
- Asegurar que el archivo tenga las 4 columnas obligatorias

#### "EDT muy largo (máximo 50 caracteres)"
- Reducir el texto del código EDT
- Usar abreviaciones

#### "Fechas requeridas son nulas"
- Verificar formato de fechas
- Asegurar que no hay celdas vacías en fechas

#### "Progreso fuera de rango"
- Valores de progreso deben estar entre 0% y 100%

## Ejemplo de Archivo XLSX Válido

| EDT | Nombre de tarea | Comienzo | Fin | Duración | Progreso | Recursos |
|-----|----------------|----------|-----|----------|----------|----------|
| 1.1 | Análisis de Requisitos | 01/01/2024 | 05/01/2024 | 5 | 100% | JPeez |
| 1.2 | Diseño del Sistema | 06/01/2024 | 15/01/2024 | 10 | 75% | MRodriguez |
| 2.1 | Desarrollo Backend | 16/01/2024 | 30/01/2024 | 15 | 50% | LGarcia |

## Contacto para Soporte

Si el problema persiste después de verificar esta guía, revisar:
1. Logs del servidor (archivo de log o console)
2. Console del navegador (F12)
3. Formato exacto del archivo XLSX
