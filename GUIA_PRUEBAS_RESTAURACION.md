# 🧪 GUÍA DE PRUEBAS - SISTEMA DE RESTAURACIÓN COMPLETA

## 🎯 Objetivo de la Prueba
Verificar que el nuevo sistema de restauración con limpieza completa funciona correctamente.

## 📋 Pre-requisitos
1. ✅ Aplicación corriendo en http://localhost:5050
2. ✅ Usuario con permisos de administrador
3. ✅ Al menos un archivo de backup disponible

## 🔍 Pasos de Prueba

### PASO 1: Verificar Estado Inicial
1. Ir a `/admin/backup`
2. **Verificar**: Lista de backups disponibles
3. **Anotar**: Cantidad actual de trabajadores en el sistema
   - Ir a la página de trabajadores
   - Contar registros actuales

### PASO 2: Probar Restauración Aditiva (Comportamiento Original)
1. Click en botón "Restaurar" (🔄) de cualquier backup
2. **NUEVO**: Debería aparecer un modal con opciones
3. Seleccionar: **"🔄 Restauración Aditiva"**
4. Click "Restaurar"
5. **Verificar**: 
   - Progreso aparece en modal
   - Los % van aumentando (0%, 5%, 35%, 45%, 90%, 100%)
   - Los datos se SUMAN a los existentes

### PASO 3: Probar Restauración Completa (Nueva Funcionalidad)
1. Click en botón "Restaurar" (🔄) de cualquier backup
2. Seleccionar: **"🧹 Restauración Completa"**
3. **Verificar**: Aparece advertencia en rojo sobre eliminación de datos
4. Click "Restaurar"
5. **Verificar**:
   - Progreso con fases adicionales: 50% (limpieza), 60% (limpieza completada)
   - Los datos existentes se ELIMINAN completamente
   - Solo quedan los datos del backup

## 🎛️ Consola del Navegador
Abrir DevTools (F12) → Console para ver logging detallado:

```javascript
// Logging esperado durante restauración completa:
🔄 [showRestoreOptions] Mostrando opciones para: archivo.sql
🔄 [executeRestore] Ejecutando restauración: archivo.sql, limpieza: true
🔄 [EnhancedBackupManager] Iniciando restauración: archivo.sql
🔍 [DEBUG] Limpieza de BD: SÍ
📡 [EnhancedBackupManager] Enviando petición de restauración...
🔄 [Polling] Ejecutando actualización programada...
📊 PROGRESO [50%] - Iniciando limpieza de tablas
📊 PROGRESO [60%] - Limpieza de base de datos completada
📊 PROGRESO [85%] - Statements ejecutados
📊 PROGRESO [100%] - Restauración completada exitosamente
```

## 🔍 Puntos Críticos a Verificar

### ✅ Modal de Opciones
- [x] Aparece modal al hacer click en "Restaurar"
- [x] Muestra las dos opciones claramente
- [x] Advertencia roja aparece al seleccionar restauración completa
- [x] Botones "Cancelar" y "Restaurar" funcionan

### ✅ Progreso en Tiempo Real
- [x] Modal de progreso aparece inmediatamente
- [x] Porcentajes se actualizan cada 2 segundos
- [x] Fases específicas para limpieza (50%, 60%) cuando corresponde
- [x] Mensaje final de éxito

### ✅ Comportamiento de Datos
- [x] **Aditiva**: Datos se suman (cantidad aumenta)
- [x] **Completa**: Datos se reemplazan (cantidad = la del backup)

### ✅ Logs del Servidor
En la consola de Docker Compose buscar:
```
📁 Iniciando restauración de archivo: archivo.sql
🧹 Limpieza de base de datos: SÍ/NO
🧹 Iniciando limpieza completa de la base de datos
🗑️ Tabla 'nombreTabla' limpiada
✅ Limpieza completa finalizada. X tablas limpiadas
```

## 🚨 Escenarios de Error a Probar

### Cancelación
1. Abrir modal de opciones
2. Click "Cancelar"
3. **Verificar**: Modal se cierra, no se ejecuta restauración

### Restauración en Progreso
1. Iniciar una restauración
2. Intentar iniciar otra
3. **Verificar**: Mensaje "Ya hay una operación en curso"

## 📊 Resultados Esperados

| Tipo Restauración | Estado BD Antes | Estado BD Después | Progreso Extra |
|-------------------|-----------------|-------------------|----------------|
| Aditiva | 6 trabajadores | 12 trabajadores | No (0→45→90→100%) |
| Completa | 6 trabajadores | 6 trabajadores | Sí (0→45→50→60→85→100%) |

## 🎯 Criterios de Éxito

✅ **FUNCIONALIDAD**
- Modal de opciones aparece y funciona
- Ambos tipos de restauración funcionan correctamente
- Progreso en tiempo real es preciso

✅ **EXPERIENCIA DE USUARIO**
- Interfaz intuitiva y clara
- Advertencias de seguridad efectivas
- Feedback visual adecuado

✅ **ROBUSTEZ**
- No hay errores en consola
- Manejo correcto de concurrencia
- Logs del servidor son informativos

---

## 🚀 ¡LISTO PARA PROBAR!

La aplicación debería estar disponible en http://localhost:5050
Sigue esta guía paso a paso y reporta cualquier comportamiento inesperado.