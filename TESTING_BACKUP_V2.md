# Testing Backup Manager V2
**Fecha:** 20 de noviembre de 2025  
**URL:** http://localhost:5050/admin/backup/v2

## ✅ Checklist de Funcionalidades

### 1. Carga Inicial
- [ ] La página carga con el diseño completo (menú lateral, header, breadcrumbs)
- [ ] Se muestran las 4 tarjetas de estadísticas
- [ ] Se carga la lista de backups existentes (9 backups encontrados)
- [ ] El estado de la BD muestra "Conectado"
- [ ] La paginación funciona (10 items por página)

### 2. Crear Backup
- [ ] Click en "Crear Backup" abre el modal
- [ ] El formulario tiene todos los campos:
  - [ ] Nombre personalizado (opcional)
  - [ ] Descripción (opcional)
  - [ ] Checkbox "Incluir Datos"
  - [ ] Checkbox "Comprimir Backup"
- [ ] Al crear backup:
  - [ ] Muestra loading overlay
  - [ ] Notificación de éxito
  - [ ] Se actualiza la lista automáticamente
  - [ ] El nuevo backup aparece en la tabla

### 3. Restaurar Backup
- [ ] Click en botón "Restaurar" (verde) abre modal de confirmación
- [ ] Modal de confirmación muestra:
  - [ ] Nombre del backup
  - [ ] Checkbox "Limpiar base de datos antes"
  - [ ] Checkbox "Entiendo las consecuencias"
  - [ ] Campo texto para escribir "RESTAURAR"
  - [ ] Campo de password
- [ ] Botón "Restaurar Ahora" solo se habilita cuando:
  - [ ] Checkbox marcado
  - [ ] Texto = "RESTAURAR" exacto
  - [ ] Password tiene al menos 6 caracteres
- [ ] Al confirmar restauración:
  - [ ] Se cierra modal de confirmación
  - [ ] Se abre modal de progreso
  - [ ] Barra de progreso actualiza cada 2 segundos
  - [ ] Muestra estadísticas:
    - [ ] % completado
    - [ ] Tiempo transcurrido
    - [ ] Tiempo estimado
    - [ ] Statements ejecutados/saltados/timeouts/reintentos
    - [ ] Throughput (stmt/s)
  - [ ] Muestra fase actual
  - [ ] Al completar (100%):
    - [ ] Mensaje de éxito/error
    - [ ] Botón "Cerrar"
    - [ ] Se recarga la lista de backups

### 4. Descargar Backup
- [ ] Click en botón "Descargar" (azul)
- [ ] Notificación "Descarga iniciada"
- [ ] El archivo se descarga correctamente

### 5. Eliminar Backup
- [ ] Click en botón "Eliminar" (rojo) abre modal
- [ ] Modal muestra:
  - [ ] Nombre del backup
  - [ ] Código de seguridad autogenerado (6 caracteres)
  - [ ] Campo para ingresar código
- [ ] Botón "Confirmar Eliminación" deshabilitado inicialmente
- [ ] Al escribir código correcto:
  - [ ] Botón se habilita
  - [ ] Click elimina el backup
  - [ ] Notificación de éxito
  - [ ] Se actualiza la lista

### 6. Subir Backup
- [ ] Click en "Subir Backup" abre modal
- [ ] Modal muestra:
  - [ ] Zona de drag & drop
  - [ ] Botón para seleccionar archivo
- [ ] Drag & drop funciona:
  - [ ] Al arrastrar archivo: zona cambia de color
  - [ ] Al soltar: se procesa el archivo
- [ ] Selector de archivos:
  - [ ] Acepta .sql, .gz, .zip
  - [ ] Muestra preview del archivo (nombre y tamaño)
- [ ] Al subir:
  - [ ] Barra de progreso muestra %
  - [ ] Notificación de éxito
  - [ ] Se actualiza la lista

### 7. Búsqueda y Filtros
- [ ] Campo de búsqueda filtra en tiempo real
- [ ] Búsqueda funciona en:
  - [ ] Nombre de archivo
  - [ ] Descripción
- [ ] Resultados se actualizan instantáneamente
- [ ] Paginación se adapta a resultados filtrados

### 8. Paginación
- [ ] Muestra máximo 10 items por página
- [ ] Botones anterior/siguiente funcionan
- [ ] Números de página clickeables
- [ ] Ellipsis (...) para rangos largos
- [ ] Contador "X-Y de Z" correcto
- [ ] Scroll automático al inicio al cambiar página

### 9. UI/UX
- [ ] Diseño responsive (mobile, tablet, desktop)
- [ ] Animaciones suaves (fade-in, hover effects)
- [ ] Notificaciones toast aparecen y desaparecen automáticamente
- [ ] Loading overlays en operaciones lentas
- [ ] Estados hover en botones
- [ ] Badges de estado (success/error)
- [ ] Iconos Font Awesome cargados

### 10. Seguridad
- [ ] Solo usuarios SUPERADMIN pueden acceder
- [ ] CSRF tokens en todas las peticiones POST/DELETE
- [ ] Password requerida para restauraciones
- [ ] Código de seguridad para eliminaciones
- [ ] Confirmación explícita de consecuencias

## 🐛 Bugs Encontrados

_(Espacio para documentar bugs durante testing)_

---

## 📊 Resultados del Testing

**Estado General:** [ ] Aprobado / [ ] Con observaciones / [ ] Rechazado

**Notas:**
- 
-
-

**Testeado por:** [Nombre]  
**Fecha:** [Fecha]
