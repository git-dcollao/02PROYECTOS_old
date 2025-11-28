# Eliminación de Tablas EtapaN - Instrucciones

## 📋 Contexto

Las tablas `etapan1`, `etapan2`, `etapan3` y `etapan4` fueron parte de un sistema jerárquico de etapas de proyectos que ya no se utiliza en la versión actual del sistema. Estas tablas deben ser eliminadas para limpiar la base de datos.

## ✅ Estado Actual

- ✅ **Modelos eliminados**: Ya no existen en `app/models.py`
- ✅ **Seeds eliminados**: Ya no se crean en `app/seeds.py`
- ⏳ **Tablas en BD**: AÚN EXISTEN en la base de datos MySQL
- ✅ **Documentación actualizada**: Removida de `.github/copilot-instructions.md`

## 🛠️ Opciones para Eliminar las Tablas

### Opción 1: Script Python Interactivo (Recomendado)

**Ventajas:**
- Interactivo con confirmación
- Verifica existencia de tablas
- Muestra conteo de registros antes de eliminar
- Manejo de errores robusto

**Pasos:**

1. **Dentro del contenedor Docker:**
   ```bash
   docker-compose exec proyectos_app python eliminar_etapas_N.py
   ```

2. **Localmente (si tienes Python configurado):**
   ```bash
   python eliminar_etapas_N.py
   ```

3. **El script te pedirá confirmación:**
   ```
   ⚠️  ¿Está seguro de que desea eliminar estas tablas? (si/no):
   ```

4. **Responde `si` para continuar**

**Salida esperada:**
```
🔄 Iniciando eliminación de tablas EtapaN...
⚠️  Foreign key checks deshabilitadas temporalmente
✅ Tabla 'etapan4' eliminada (X registros)
✅ Tabla 'etapan3' eliminada (X registros)
✅ Tabla 'etapan2' eliminada (X registros)
✅ Tabla 'etapan1' eliminada (X registros)
✅ Foreign key checks rehabilitadas
🎉 Proceso completado exitosamente
```

### Opción 2: Script SQL Directo

**Ventajas:**
- Más rápido
- Puede ejecutarse desde cualquier cliente MySQL

**Pasos:**

1. **Acceder a MySQL:**
   ```bash
   # Desde Docker
   docker-compose exec proyectos_db mysql -u proyectos_admin -p proyectosDB
   
   # O usar Adminer
   # http://localhost:8080
   ```

2. **Ejecutar el script:**
   ```bash
   source eliminar_etapas_N.sql
   # O copiar y pegar el contenido
   ```

**Alternativa con archivo:**
```bash
# Desde PowerShell en tu máquina local
Get-Content eliminar_etapas_N.sql | docker-compose exec -T proyectos_db mysql -u proyectos_admin -p123456!#Td proyectosDB
```

### Opción 3: Cliente de Base de Datos (Adminer/PhpMyAdmin)

1. Acceder a Adminer: http://localhost:8080
2. Ir a la pestaña "SQL"
3. Copiar y pegar el contenido de `eliminar_etapas_N.sql`
4. Ejecutar

## ⚠️ Precauciones

### Antes de Ejecutar

1. **Hacer backup de la base de datos:**
   ```bash
   docker-compose exec proyectos_app python -c "from app.routes.admin_routes import crear_backup; crear_backup()"
   ```
   
   O manualmente:
   ```bash
   docker-compose exec proyectos_db mysqldump -u proyectos_admin -p123456!#Td proyectosDB > backup_antes_eliminar_etapas_$(date +%Y%m%d_%H%M%S).sql
   ```

2. **Verificar que no hay dependencias:**
   ```sql
   -- Ejecutar en MySQL para verificar foreign keys
   SELECT 
       TABLE_NAME,
       COLUMN_NAME,
       CONSTRAINT_NAME,
       REFERENCED_TABLE_NAME,
       REFERENCED_COLUMN_NAME
   FROM
       INFORMATION_SCHEMA.KEY_COLUMN_USAGE
   WHERE
       REFERENCED_TABLE_NAME IN ('etapan1', 'etapan2', 'etapan3', 'etapan4')
       AND TABLE_SCHEMA = 'proyectosDB';
   ```

### Después de Ejecutar

1. **Verificar eliminación:**
   ```sql
   SHOW TABLES LIKE 'etapan%';
   ```
   
   Resultado esperado: `Empty set` (no debe mostrar nada)

2. **Crear migración de Flask (opcional pero recomendado):**
   ```bash
   docker-compose exec proyectos_app flask db migrate -m "Eliminar tablas EtapaN obsoletas"
   docker-compose exec proyectos_app flask db upgrade
   ```

## 🔍 Verificación Final

Ejecutar estas consultas para confirmar:

```sql
-- 1. Verificar que no existen las tablas
SELECT COUNT(*) as tablas_etapan_restantes
FROM information_schema.tables 
WHERE table_schema = 'proyectosDB' 
AND table_name IN ('etapan1', 'etapan2', 'etapan3', 'etapan4');
-- Debe retornar: 0

-- 2. Listar todas las tablas actuales
SHOW TABLES;
```

## 🐛 Troubleshooting

### Error: "Cannot drop table because it is referenced by a foreign key constraint"

**Solución:** El script ya deshabilita `FOREIGN_KEY_CHECKS`, pero si persiste:

```sql
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS etapan4;
DROP TABLE IF EXISTS etapan3;
DROP TABLE IF EXISTS etapan2;
DROP TABLE IF EXISTS etapan1;
SET FOREIGN_KEY_CHECKS = 1;
```

### Error: "Table doesn't exist"

**Solución:** Las tablas ya fueron eliminadas previamente. Verificar con:
```sql
SHOW TABLES LIKE 'etapan%';
```

### Script Python no encuentra app

**Solución:** Ejecutar desde el directorio raíz del proyecto:
```bash
cd C:\Users\Daniel Collao\Documents\Repositories\02PROYECTOS
python eliminar_etapas_N.py
```

## 📝 Registro de Cambios

- **2025-11-05**: Creación de scripts de eliminación
- **Estado**: ✅ Modelos y seeds eliminados | ⏳ Pendiente eliminar tablas de BD

## ✅ Checklist

- [ ] Crear backup de la base de datos
- [ ] Verificar que no hay dependencias críticas
- [ ] Ejecutar script de eliminación (opción 1, 2 o 3)
- [ ] Verificar eliminación exitosa
- [ ] (Opcional) Crear migración de Flask
- [ ] Actualizar esta documentación con la fecha de ejecución

---

**Notas:**
- Los archivos `eliminar_etapas_N.py` y `eliminar_etapas_N.sql` pueden ser eliminados después de completar este proceso
- Esta es una operación irreversible - asegúrate de tener un backup
