# 📋 Procedimientos Operativos - Sistema de Gestión de Proyectos

**Servidor**: 10.20.10.3  
**Última actualización**: 10 de Febrero de 2026

---

## 🔄 Restauración de Backups

### ⚠️ PROCEDIMIENTO OBLIGATORIO POST-RESTAURACIÓN

**Después de restaurar cualquier backup**, SIEMPRE ejecutar:

```bash
# 1. Conectar al servidor
ssh admintd@10.20.10.3

# 2. Ir al directorio del proyecto
cd ~/docker/PROYECTOS

# 3. Reiniciar SOLO la aplicación (mantiene MySQL corriendo)
docker-compose restart proyectos_app

# 4. Esperar a que la aplicación inicie (30 segundos)
sleep 30

# 5. Verificar estado
docker-compose ps

# Debe mostrar:
# proyectos_app   Up (healthy)
# mysql_db        Up (healthy)
```

### 🌐 Pasos para los Usuarios

**Después de que el administrador reinicie la aplicación**:

1. **Cerrar sesión** en la aplicación
2. **Cerrar completamente el navegador** (no solo la pestaña)
3. **Limpiar caché**: `Ctrl+Shift+Delete` → Marcar "Caché" y "Cookies" → Aceptar
4. **Abrir navegador nuevo**
5. **Ir a** `http://10.20.10.3:5050`
6. **Iniciar sesión** nuevamente

### ❓ ¿Por qué es necesario?

- **MySQL**: Los datos se restauran correctamente ✅
- **Flask**: Mantiene datos antiguos en caché hasta reiniciar ❌
- **Navegador**: Puede tener sesiones antiguas en cookies ❌

**Sin reiniciar la app**, verás datos antiguos aunque el backup se haya restaurado.

---

## 🚀 Reinicio de Servicios

### Reiniciar Solo la Aplicación (Mantiene BD)

```bash
docker-compose restart proyectos_app
```

**Cuándo usar**: 
- Después de restaurar backups
- Cuando la interfaz web no responde
- Después de cambios en el código

### Reiniciar Todo el Sistema

```bash
docker-compose restart
```

**Cuándo usar**:
- Cuando MySQL no responde
- Problemas de conectividad
- Mantenimiento programado

### Reinicio Completo (Con reconstrucción)

```bash
docker-compose down
docker-compose up -d --build
```

**Cuándo usar**:
- Después de actualizar código desde GitHub
- Cambios en Dockerfile o requirements.txt
- Problemas graves que no se resuelven con restart

---

## 📊 Monitoreo y Diagnóstico

### Ver Estado de Contenedores

```bash
docker-compose ps
```

**Estado esperado**:
```
NAME            STATUS
proyectos_app   Up (healthy)
mysql_db        Up (healthy)
```

### Ver Logs en Tiempo Real

```bash
# Logs de la aplicación
docker-compose logs -f proyectos_app

# Logs de MySQL
docker-compose logs -f proyectos_db

# Últimas 100 líneas
docker-compose logs --tail=100 proyectos_app
```

### Verificar Health Check

```bash
# Desde el servidor
curl http://localhost:5050/health

# Debería responder:
# {"status":"healthy"}
```

### Verificar Conectividad MySQL

```bash
docker-compose exec proyectos_db mysql -u proyectos_admin -p'123456!#Td' -e "SELECT 1;"
```

---

## 💾 Gestión de Backups

### Crear Backup Manual (Interfaz Web)

1. Ir a `http://10.20.10.3:5050/admin/backup`
2. Clic en **"Crear Backup"**
3. Ingresar nombre descriptivo
4. Esperar confirmación

### Crear Backup Manual (Terminal)

```bash
docker-compose exec -T proyectos_db mysqldump \
  -u proyectos_admin \
  -p'123456!#Td' \
  proyectosDB | gzip > ~/backups_manual/backup_$(date +%Y%m%d_%H%M%S).sql.gz

echo "✅ Backup creado en ~/backups_manual/"
ls -lh ~/backups_manual/
```

### Verificar Espacio en Disco

```bash
# Ver espacio disponible
df -h | grep -E '(Filesystem|docker|home)'

# Ver tamaño de backups
du -sh ~/docker/PROYECTOS/backups/

# Listar backups por tamaño
ls -lhS ~/docker/PROYECTOS/backups/*.sql.gz | head -10
```

---

## 🔧 Problemas Comunes

### Problema: "Los datos no aparecen después de restaurar"

**Causa**: Caché de Flask

**Solución**:
```bash
docker-compose restart proyectos_app
```

Luego los usuarios deben cerrar sesión y limpiar caché del navegador.

---

### Problema: "Contenedor proyectos_app en estado Restarting"

**Diagnóstico**:
```bash
docker-compose logs proyectos_app --tail=50
```

**Causas comunes**:
1. **Permisos**: Directorio `logs/` sin permisos de escritura
   ```bash
   chmod -R 777 ~/docker/PROYECTOS/logs
   docker-compose restart proyectos_app
   ```

2. **Base de datos no disponible**: Esperar a que MySQL esté healthy
   ```bash
   docker-compose ps
   # Esperar a que mysql_db muestre "Up (healthy)"
   ```

3. **Error en código Python**: Ver logs para detalles

---

### Problema: "Puerto 5050 ya en uso"

**Diagnóstico**:
```bash
sudo netstat -tulpn | grep 5050
```

**Solución**:
```bash
# Detener contenedor actual
docker-compose down

# Verificar que se liberó el puerto
sudo netstat -tulpn | grep 5050

# Levantar de nuevo
docker-compose up -d
```

---

### Problema: "Cannot connect to MySQL"

**Verificar estado de MySQL**:
```bash
docker-compose ps proyectos_db
```

**Si no está corriendo**:
```bash
docker-compose up -d proyectos_db
```

**Si está corriendo pero no responde**:
```bash
docker-compose restart proyectos_db
sleep 15
docker-compose ps
```

---

## 🔐 Seguridad

### Cambiar Contraseña de MySQL

```bash
# 1. Detener aplicación
docker-compose stop proyectos_app

# 2. Conectar a MySQL
docker-compose exec proyectos_db mysql -u root -p'ROOT_PASSWORD'

# 3. Cambiar contraseña
ALTER USER 'proyectos_admin'@'%' IDENTIFIED BY 'NUEVA_CONTRASEÑA_SEGURA';
FLUSH PRIVILEGES;
EXIT;

# 4. Actualizar .env
nano ~/docker/PROYECTOS/.env
# Cambiar: MYSQL_PW=NUEVA_CONTRASEÑA_SEGURA

# 5. Reiniciar
docker-compose restart
```

### Cambiar SECRET_KEY de Flask

```bash
# 1. Generar nueva clave
python3 -c "import secrets; print(secrets.token_hex(32))"

# 2. Editar .env
nano ~/docker/PROYECTOS/.env
# Cambiar: SECRET_KEY=NUEVA_CLAVE_GENERADA

# 3. Reiniciar aplicación
docker-compose restart proyectos_app
```

---

## 📈 Mantenimiento Preventivo

### Limpieza de Logs Antiguos (Mensual)

```bash
# Ver tamaño de logs
du -sh ~/docker/PROYECTOS/logs/

# Limpiar logs mayores a 30 días
find ~/docker/PROYECTOS/logs/ -name "*.log" -mtime +30 -delete

# O comprimir en lugar de eliminar
find ~/docker/PROYECTOS/logs/ -name "*.log" -mtime +30 -exec gzip {} \;
```

### Limpieza de Backups Antiguos (Trimestral)

```bash
# Mantener solo últimos 20 backups
cd ~/docker/PROYECTOS/backups/
ls -t *.sql.gz | tail -n +21 | xargs -r rm

echo "✅ Backups antiguos eliminados"
ls -lh *.sql.gz | wc -l
```

### Verificación de Integridad (Semanal)

```bash
# Test completo del sistema
echo "=== TEST DE SALUD DEL SISTEMA ==="

# 1. Estado de contenedores
echo "📦 Estado de contenedores:"
docker-compose ps

# 2. Health check
echo ""
echo "🏥 Health check:"
curl http://localhost:5050/health

# 3. Conexión MySQL
echo ""
echo "💾 Conexión MySQL:"
docker-compose exec -T proyectos_db mysql -u proyectos_admin -p'123456!#Td' -e "SELECT COUNT(*) as total_trabajadores FROM proyectosDB.trabajador;"

# 4. Espacio en disco
echo ""
echo "💿 Espacio en disco:"
df -h | grep -E '(Filesystem|docker|home)'

# 5. Logs recientes
echo ""
echo "📋 Logs recientes (últimos errores):"
docker-compose logs --tail=100 | grep -i error | tail -5

echo ""
echo "=== FIN TEST ==="
```

---

## 📞 Contactos de Emergencia

**Administrador del Sistema**: Daniel Collao  
**Repositorio GitHub**: https://github.com/git-dcollao/02PROYECTOS.git  
**Documentación Completa**: `~/docker/PROYECTOS/DOCS/`  

---

**Última revisión**: 10 de Febrero de 2026  
**Versión del documento**: 1.0
