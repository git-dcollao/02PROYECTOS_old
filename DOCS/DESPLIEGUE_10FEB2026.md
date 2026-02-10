# 🚀 Guía de Despliegue en Producción - 10 de Febrero de 2026

**Servidor**: 10.20.10.3  
**Usuario**: admintd  
**Ruta del Proyecto**: ~/docker/PROYECTOS  
**Puerto**: 5050  
**Repositorio**: https://github.com/git-dcollao/02PROYECTOS.git  
**Estrategia**: Reemplazo completo con despliegue limpio

---

## ✅ Pre-Verificación Local (Ya Completado)

- ✅ Repositorio: `https://github.com/git-dcollao/02PROYECTOS.git`
- ✅ Rama: `master`
- ✅ Estado: Limpio, sincronizado con GitHub
- ✅ Último commit: `8015737` - mejoras y reparaciones en subidas de control

---

## 📋 PLAN DE DESPLIEGUE COMPLETO

### **FASE 1: Conectar al Servidor**

```bash
# Desde PowerShell en tu máquina local
ssh admintd@10.20.10.3
```

**Contraseña**: [Tu contraseña de admintd]

---

### **FASE 2: Backup de Seguridad (Opcional pero Recomendado)**

```bash
# Ubicarse en el directorio del proyecto
cd ~/docker/PROYECTOS

# Crear directorio de backup temporal
mkdir -p ~/backups_temp

# Backup del .env actual (contiene configuraciones importantes)
cp .env ~/backups_temp/.env.backup_10feb2026

# Backup de la base de datos actual (por si acaso)
docker-compose exec -T proyectos_db mysqldump \
  -u proyectos_admin \
  -p123456\!#Td \
  proyectosDB | gzip > ~/backups_temp/db_backup_10feb2026.sql.gz

# Verificar que se crearon los backups
ls -lh ~/backups_temp/

echo "✅ Backups creados exitosamente"
```

---

### **FASE 3: Detener Contenedores Actuales**

```bash
# Asegurarse de estar en el directorio correcto
cd ~/docker/PROYECTOS

# Ver contenedores en ejecución
docker-compose ps

# Detener y eliminar contenedores
docker-compose down

# Verificar que se detuvieron
docker ps | grep proyectos
docker ps | grep mysql_db

echo "✅ Contenedores detenidos"
```

---

### **FASE 4: Limpiar Base de Datos (Despliegue Limpio)**

```bash
# ADVERTENCIA: Esto eliminará TODA la base de datos actual
# Eliminar volumen de MySQL
docker volume ls | grep mysql_data

docker volume rm proyectos_mysql_data

# Si da error de volumen en uso, forzar:
docker volume rm -f proyectos_mysql_data

# Verificar que se eliminó
docker volume ls | grep mysql_data

echo "✅ Base de datos limpiada"
```

---

### **FASE 5: Actualizar Código desde GitHub**

```bash
# Verificar rama actual
git branch

# Ver estado antes de actualizar
git status

# Guardar cualquier cambio local del .env (no debería haber)
git stash

# Actualizar código desde GitHub
git pull origin master

# Ver los cambios descargados
git log --oneline -5

# Si hubo stash, aplicar cambios guardados
git stash pop

echo "✅ Código actualizado desde GitHub"
```

---

### **FASE 6: Verificar Archivo .env de Producción**

```bash
# Ver las primeras líneas del .env (sin mostrar contraseñas)
head -n 15 .env

# Verificar variables críticas (editar si es necesario)
nano .env
```

**Variables críticas a verificar:**

```bash
# Producción
FLASK_ENV=production
FLASK_DEBUG=0

# Base de datos
MYSQL_HOST=proyectos_db
MYSQL_PORT=3306
MYSQL_USER=proyectos_admin
MYSQL_PW=123456!#Td
MYSQL_DB=proyectosDB

# Seguridad
SECRET_KEY=[Debe ser una clave segura y única]
SESSION_COOKIE_SECURE=False  # False porque no usas HTTPS

# Aplicación
APP_PORT=5050
```

**⚠️ IMPORTANTE**: Si `SECRET_KEY` aún dice `dev-secret-key-change-in-production`, cámbiala por una clave segura:

```bash
# Generar una clave segura
python3 -c "import secrets; print(secrets.token_hex(32))"

# Copiar el resultado y pegarlo en SECRET_KEY en el .env
```

---

### **FASE 7: Reconstruir y Levantar Contenedores**

```bash
# Reconstruir la aplicación (asegura que usa el código nuevo)
docker-compose build --no-cache proyectos_app

# Levantar todos los servicios
docker-compose up -d

# Ver logs en tiempo real para verificar inicio correcto
docker-compose logs -f

# Presiona Ctrl+C cuando veas:
# ✅ "Aplicación Flask iniciada correctamente"
# ✅ "Servidor corriendo en puerto 5050"
```

**Qué esperar en los logs:**
```
🔄 Esperando base de datos...
✅ Base de datos disponible
🔄 Ejecutando migraciones...
✅ Migraciones aplicadas
🔄 Creando datos iniciales (seeds)...
✅ Seeds creados
🚀 Iniciando aplicación Flask...
✅ Servidor corriendo en puerto 5050
```

---

### **FASE 8: Verificar Estado de los Contenedores**

```bash
# Ver estado de los contenedores
docker-compose ps

# Verificar logs de la aplicación
docker-compose logs proyectos_app --tail=50

# Verificar logs de la base de datos
docker-compose logs proyectos_db --tail=30

# Ver contenedores en ejecución
docker ps | grep proyectos
```

**Estado esperado:**
```
NAME            STATUS         PORTS
proyectos_app   Up (healthy)   0.0.0.0:5050->5050/tcp
mysql_db        Up (healthy)   0.0.0.0:3308->3306/tcp
```

---

### **FASE 9: Pruebas de Funcionalidad**

#### **A) Desde el servidor (curl)**

```bash
# Test de health endpoint
curl http://localhost:5050/health

# Debería responder:
# {"status": "healthy"}

# Test de página principal (debería redirigir a login)
curl -I http://localhost:5050/

# Debería responder con código 302 (redirección)
```

#### **B) Desde tu navegador local**

Abrir: `http://10.20.10.3:5050`

**Verificaciones:**
1. ✅ Carga la página de login
2. ✅ No hay errores 500 en la consola
3. ✅ Los estilos CSS se cargan correctamente
4. ✅ Puedes hacer login con usuario de prueba

**Usuarios de Prueba** (si los seeds se ejecutaron):
```
Usuario: admin@ejemplo.com
Contraseña: admin123

Usuario: user@ejemplo.com
Contraseña: user123
```

---

### **FASE 10: Verificar Base de Datos**

```bash
# Conectar a MySQL
docker-compose exec proyectos_db mysql -u proyectos_admin -p123456\!#Td proyectosDB

# Dentro de MySQL, ejecutar:
SHOW TABLES;

# Verificar que existen las tablas principales
# Debería mostrar: trabajador, requerimiento, proyecto, areas, etc.

# Ver cantidad de usuarios creados
SELECT COUNT(*) FROM trabajador;

# Ver usuarios existentes
SELECT id, nombres, apellidos, email, rol FROM trabajador LIMIT 5;

# Salir de MySQL
EXIT;
```

---

### **FASE 11: Monitoreo Post-Despliegue**

```bash
# Ver logs en tiempo real (útil para detectar errores)
docker-compose logs -f proyectos_app

# Ver uso de recursos
docker stats proyectos_app mysql_db

# Ver redes Docker
docker network inspect proyectos_proyectos_network
```

---

## 🔧 Comandos Útiles Post-Despliegue

### **Reiniciar solo la aplicación (sin BD)**
```bash
docker-compose restart proyectos_app
```

### **Ver logs de errores**
```bash
docker-compose logs proyectos_app | grep -i error
docker-compose logs proyectos_db | grep -i error
```

### **Entrar al contenedor de la aplicación**
```bash
docker-compose exec proyectos_app bash

# Dentro del contenedor:
python --version
pip list
ls -la /app
exit
```

### **Ejecutar migraciones manualmente**
```bash
docker-compose exec proyectos_app flask db upgrade
```

### **Ejecutar seeds manualmente**
```bash
docker-compose exec proyectos_app python -c "from app import create_app, db; from app.seeds import run_seeds; app = create_app('production'); app.app_context().push(); run_seeds()"
```

### **Crear backup manual**
```bash
docker-compose exec -T proyectos_db mysqldump \
  -u proyectos_admin \
  -p123456\!#Td \
  proyectosDB | gzip > ~/backups_temp/backup_manual_$(date +%Y%m%d_%H%M%S).sql.gz
```

---

## 🚨 Resolución de Problemas

### **Problema: Contenedor proyectos_app no inicia**

```bash
# Ver logs detallados
docker-compose logs proyectos_app

# Verificar si es problema de permisos
ls -la ~/docker/PROYECTOS/logs
ls -la ~/docker/PROYECTOS/uploads

# Dar permisos si es necesario
chmod -R 755 ~/docker/PROYECTOS/logs
chmod -R 755 ~/docker/PROYECTOS/uploads
```

### **Problema: No puede conectar a la base de datos**

```bash
# Verificar que MySQL está corriendo
docker-compose ps proyectos_db

# Ver logs de MySQL
docker-compose logs proyectos_db

# Verificar conectividad desde la app
docker-compose exec proyectos_app ping proyectos_db

# Probar conexión manual
docker-compose exec proyectos_app python -c "import pymysql; conn = pymysql.connect(host='proyectos_db', user='proyectos_admin', password='123456!#Td', database='proyectosDB'); print('✅ Conexión exitosa')"
```

### **Problema: Puerto 5050 ya en uso**

```bash
# Ver qué está usando el puerto
sudo netstat -tulpn | grep 5050

# O con lsof
sudo lsof -i :5050

# Detener el proceso anterior si es necesario
docker stop proyectos_app
```

### **Problema: Volumen de MySQL no se elimina**

```bash
# Forzar eliminación
docker-compose down -v

# Listar volúmenes
docker volume ls

# Eliminar manualmente
docker volume rm proyectos_mysql_data

# Si persiste, limpiar todo
docker system prune -a --volumes
```

---

## 📊 Checklist Final

Antes de dar por terminado el despliegue, verificar:

- [ ] Contenedores corriendo: `docker-compose ps` muestra `Up (healthy)`
- [ ] Aplicación accesible: `http://10.20.10.3:5050` carga correctamente
- [ ] Login funciona: Puedes autenticarte con un usuario
- [ ] Base de datos poblada: Existen tablas y datos iniciales
- [ ] Logs sin errores críticos: No hay tracebacks en los logs
- [ ] Health check OK: `curl http://localhost:5050/health` responde
- [ ] Backup creado: Existe el archivo `~/backups_temp/.env.backup_10feb2026`
- [ ] .env configurado: `SECRET_KEY` no es la clave por defecto
- [ ] Permisos correctos: Directorios `logs` y `uploads` son escribibles

---

## 📝 Notas Importantes

1. **Despliegue Limpio**: Se eliminó toda la base de datos anterior
2. **Puerto 5050**: Ya está reservado para este proyecto
3. **Sin SSL**: Configuración local, no requiere HTTPS
4. **Backup**: Se creó backup del .env y BD antes de actualizar
5. **Repositorio**: Código actualizado desde `https://github.com/git-dcollao/02PROYECTOS.git`

---

## 🔄 Próximos Pasos (Opcional)

### **Configurar Monitoreo Continuo**

```bash
# Crear script de monitoreo
cat > ~/monitor_proyectos.sh << 'EOF'
#!/bin/bash
echo "📊 Estado de Proyecto Gestión:"
echo "================================"
docker-compose -f ~/docker/PROYECTOS/docker-compose.yml ps
echo ""
echo "💾 Uso de disco:"
df -h | grep -E '(Filesystem|docker)'
echo ""
echo "🔍 Últimas 10 líneas de logs:"
docker-compose -f ~/docker/PROYECTOS/docker-compose.yml logs --tail=10 proyectos_app
EOF

chmod +x ~/monitor_proyectos.sh

# Ejecutar cuando quieras ver el estado
~/monitor_proyectos.sh
```

### **Configurar Backup Automático**

```bash
# Crear script de backup automático
cat > ~/backup_proyectos.sh << 'EOF'
#!/bin/bash
BACKUP_DIR=~/backups_proyectos
mkdir -p $BACKUP_DIR
DATE=$(date +%Y%m%d_%H%M%S)

docker-compose -f ~/docker/PROYECTOS/docker-compose.yml exec -T proyectos_db mysqldump \
  -u proyectos_admin \
  -p123456\!#Td \
  proyectosDB | gzip > $BACKUP_DIR/backup_$DATE.sql.gz

# Mantener solo últimos 10 backups
ls -t $BACKUP_DIR/backup_*.sql.gz | tail -n +11 | xargs -r rm

echo "✅ Backup creado: backup_$DATE.sql.gz"
EOF

chmod +x ~/backup_proyectos.sh

# Programar en crontab (backup diario a las 2 AM)
crontab -e
# Agregar línea:
# 0 2 * * * ~/backup_proyectos.sh >> ~/backup_proyectos.log 2>&1
```

---

## ⚠️ IMPORTANTE: Procedimiento Después de Restaurar Backup

**Problema identificado**: Después de restaurar un backup, la aplicación puede servir datos en caché en lugar de los datos restaurados.

**Solución Obligatoria**:
```bash
# Después de CADA restauración de backup, ejecutar:
docker-compose restart proyectos_app

# Esperar 30 segundos
sleep 30

# Verificar que la aplicación esté corriendo
docker-compose ps

# Limpiar caché del navegador (Ctrl+Shift+Delete)
# Cerrar sesión y volver a iniciar sesión
```

**¿Por qué es necesario?**
- Flask mantiene sesiones y caché en memoria
- Al restaurar el backup, MySQL se actualiza pero Flask no
- Reiniciar la aplicación limpia toda la caché y sesiones

**Alternativa sin reinicio**:
```bash
# Desde la interfaz web
# 1. Restaurar backup
# 2. Cerrar sesión (Logout)
# 3. Cerrar completamente el navegador
# 4. Abrir navegador nuevo
# 5. Limpiar caché (Ctrl+Shift+Delete)
# 6. Iniciar sesión nuevamente
```

---

## 🆘 Contacto y Soporte

**Repositorio**: https://github.com/git-dcollao/02PROYECTOS.git  
**Documentación**: `~/docker/PROYECTOS/DOCS/`  
**Logs**: `~/docker/PROYECTOS/logs/app.log`

---

**Fecha de Despliegue**: 10 de Febrero de 2026  
**Versión**: Commit `8015737`  
**Responsable**: Daniel Collao  
**Última Actualización**: 10 de Febrero de 2026 - Fix caché post-restauración
