# 🚀 Guía de Despliegue en Servidor de Producción

**Servidor**: 10.20.10.3  
**Fecha**: 15 de enero de 2026  
**Cambios**: Corrección de cálculo de progreso desde actividad raíz

---

## 📋 Pre-requisitos

### En tu Máquina Local:
- ✅ Código actualizado y commiteado en Git
- ✅ Push realizado a GitHub
- ✅ Acceso SSH al servidor 10.20.10.3

### En el Servidor de Producción:
- ✅ Docker y Docker Compose instalados
- ✅ Git configurado
- ✅ Repositorio clonado en el servidor
- ✅ Archivo `.env` con configuración de producción

---

## 🔐 Paso 1: Conectar al Servidor

### Desde PowerShell (Windows):

```powershell
# Conectar vía SSH
ssh usuario@10.20.10.3

# O si tienes clave SSH configurada
ssh -i ruta/a/tu/clave.pem usuario@10.20.10.3
```

### Verificar Ubicación del Proyecto:
```bash
# Listar directorios
ls -la

# Navegar al proyecto (ajustar ruta según tu servidor)
cd /opt/proyectos
# O
cd /home/usuario/02PROYECTOS
# O
cd ~/proyectos
```

---

## 📥 Paso 2: Actualizar Código en el Servidor

### Opción A: Pull desde GitHub (Recomendado)

```bash
# Verificar estado actual
git status

# Ver rama actual
git branch

# Hacer pull de los últimos cambios
git pull origin master

# Verificar que se descargaron los cambios
git log --oneline -5
```

### Opción B: Si hay conflictos

```bash
# Guardar cambios locales (si existen)
git stash

# Pull del código actualizado
git pull origin master

# Aplicar cambios guardados (si necesario)
git stash pop
```

---

## 🐳 Paso 3: Actualizar Contenedores Docker

### ⚠️ IMPORTANTE: Crear Backup ANTES de Actualizar

```bash
# Opción 1: Usar la interfaz web (Recomendado)
# Ir a: http://10.20.10.3:5050/admin/backup
# Crear backup manual con nombre: "PRE_ACTUALIZACION_15ENE2026"

# Opción 2: Backup manual desde terminal
docker-compose exec mysql mysqldump -u root -p proyectosDB | gzip > backup_pre_actualizacion_$(date +%Y%m%d_%H%M%S).sql.gz
```

### Actualización con Reinicio Simple (Más Rápido)

```bash
# Si solo cambiaste código Python (sin dependencias ni Dockerfile)
docker-compose restart proyectos_app

# Verificar que inició correctamente
docker-compose logs -f proyectos_app
# Presiona Ctrl+C para salir de los logs
```

### Actualización con Reconstrucción (Más Segura)

```bash
# Detener contenedores (mantiene volúmenes de datos)
docker-compose down

# Reconstruir imagen con nuevo código
docker-compose build

# Iniciar contenedores
docker-compose up -d

# Ver logs en tiempo real
docker-compose logs -f proyectos_app
```

---

## ✅ Paso 4: Verificar el Despliegue

### 1. Verificar que los Contenedores Están Corriendo

```bash
# Ver estado de contenedores
docker-compose ps

# Deberías ver algo como:
# NAME                    STATUS              PORTS
# proyectos_app           Up                  0.0.0.0:5050->5000/tcp
# mysql                   Up                  0.0.0.0:3308->3306/tcp
```

### 2. Verificar Logs por Errores

```bash
# Ver últimas 50 líneas de logs
docker-compose logs --tail=50 proyectos_app

# Buscar errores
docker-compose logs proyectos_app | grep -i error
docker-compose logs proyectos_app | grep "❌"
```

### 3. Verificar Endpoint de Health Check

```bash
# Desde el servidor
curl http://localhost:5050/health

# Desde tu máquina local
curl http://10.20.10.3:5050/health
```

Respuesta esperada:
```json
{
  "status": "OK",
  "database": "connected",
  "timestamp": "2026-01-15T..."
}
```

### 4. Probar en el Navegador

Abrir en tu navegador:

```
http://10.20.10.3:5050/login
```

**Pruebas Críticas:**

- [ ] Login funciona correctamente
- [ ] Ir a: http://10.20.10.3:5050/proyectos_estado_4
- [ ] Verificar que "Progreso Real" muestra valores
- [ ] Abrir un proyecto en detalle
- [ ] **CRÍTICO**: Confirmar que el progreso en listado y detalle es IGUAL

### 5. Verificar Logs de la Corrección

```bash
# Buscar logs de actividad raíz
docker-compose logs proyectos_app | grep "Progreso obtenido de actividad raíz"
```

Deberías ver líneas como:
```
✅ Progreso obtenido de actividad raíz (EDT: 1): 35.0%
```

Si ves esto, significa que la corrección está funcionando:
```
⚠️ No se encontró actividad raíz para proyecto X
```

---

## 🔄 Paso 5: Rollback en Caso de Problemas

### Si algo sale mal, puedes revertir:

#### Opción 1: Volver a Versión Anterior del Código

```bash
# Ver últimos commits
git log --oneline -10

# Volver al commit anterior
git checkout HASH_DEL_COMMIT_ANTERIOR

# Reconstruir contenedores
docker-compose down
docker-compose build
docker-compose up -d
```

#### Opción 2: Restaurar Backup de Base de Datos

```bash
# Usar interfaz web:
# http://10.20.10.3:5050/admin/backup
# Seleccionar "Restaurar" en el backup "PRE_ACTUALIZACION_15ENE2026"

# O desde terminal:
gunzip -c backup_pre_actualizacion_*.sql.gz | docker-compose exec -T mysql mysql -u root -p proyectosDB
```

---

## 📊 Monitoreo Post-Despliegue

### Ver Logs en Tiempo Real

```bash
# Logs de la aplicación
docker-compose logs -f proyectos_app

# Logs de la base de datos
docker-compose logs -f mysql
```

### Ver Recursos del Sistema

```bash
# CPU y Memoria de contenedores
docker stats

# Espacio en disco
df -h

# Ver procesos Docker
docker ps -a
```

### Verificar Conexiones a la Base de Datos

```bash
# Conectar a MySQL
docker-compose exec mysql mysql -u root -p proyectosDB

# Dentro de MySQL, ejecutar:
SHOW PROCESSLIST;
SHOW STATUS LIKE 'Threads_connected';
EXIT;
```

---

## 🔧 Troubleshooting

### Problema: "Permission denied" al hacer git pull

```bash
# Verificar permisos
ls -la

# Cambiar propietario si es necesario
sudo chown -R $USER:$USER .

# Intentar pull nuevamente
git pull origin master
```

### Problema: Puerto 5050 ya en uso

```bash
# Ver qué está usando el puerto
sudo netstat -tulpn | grep 5050

# Detener proceso anterior
sudo kill -9 PID_DEL_PROCESO

# O cambiar puerto en docker-compose.yml
nano docker-compose.yml
# Cambiar: "5051:5000" en lugar de "5050:5000"
```

### Problema: Contenedor no inicia

```bash
# Ver logs completos
docker-compose logs proyectos_app

# Ver eventos de Docker
docker events

# Reiniciar Docker
sudo systemctl restart docker
docker-compose up -d
```

### Problema: Base de datos no responde

```bash
# Verificar estado de MySQL
docker-compose exec mysql mysql -u root -p -e "SELECT 1;"

# Reiniciar solo MySQL
docker-compose restart mysql

# Esperar 30 segundos y reiniciar app
sleep 30
docker-compose restart proyectos_app
```

---

## 📝 Checklist Final

### Antes del Despliegue:
- [ ] Backup de base de datos creado
- [ ] Código commiteado y pusheado a GitHub
- [ ] Revisión de cambios con `git log` y `git diff`
- [ ] Variables de entorno verificadas en `.env`

### Durante el Despliegue:
- [ ] Conexión SSH exitosa al servidor
- [ ] Git pull ejecutado sin errores
- [ ] Contenedores reconstruidos/reiniciados
- [ ] Logs verificados sin errores críticos

### Después del Despliegue:
- [ ] Health check respondiendo OK
- [ ] Login funcional
- [ ] Listado de proyectos carga correctamente
- [ ] Progreso muestra valores consistentes (12.1% vs 13% corregido)
- [ ] Validación de avances funciona
- [ ] Logs muestran "✅ Progreso obtenido de actividad raíz"

---

## 🚨 Contactos de Emergencia

### Si hay Problemas Críticos:

1. **Revisar logs inmediatamente**:
   ```bash
   docker-compose logs --tail=100 proyectos_app
   ```

2. **Restaurar backup**:
   ```bash
   # Ir a: http://10.20.10.3:5050/admin/backup
   # Restaurar último backup funcional
   ```

3. **Revertir código**:
   ```bash
   git checkout COMMIT_ANTERIOR
   docker-compose restart proyectos_app
   ```

---

## 📞 Comandos Rápidos de Referencia

```bash
# Conectar al servidor
ssh usuario@10.20.10.3

# Navegar al proyecto
cd /ruta/al/proyecto

# Actualizar código
git pull origin master

# Reinicio rápido (sin rebuild)
docker-compose restart proyectos_app

# Reinicio completo (con rebuild)
docker-compose down && docker-compose build && docker-compose up -d

# Ver logs
docker-compose logs -f proyectos_app

# Ver estado
docker-compose ps

# Backup manual
docker-compose exec mysql mysqldump -u root -p proyectosDB | gzip > backup_$(date +%Y%m%d_%H%M%S).sql.gz

# Restaurar backup
gunzip -c backup_XXXXXX.sql.gz | docker-compose exec -T mysql mysql -u root -p proyectosDB
```

---

## ⏱️ Tiempo Estimado de Despliegue

| Método | Tiempo | Downtime |
|--------|--------|----------|
| **Restart simple** | ~30 segundos | ~5 segundos |
| **Rebuild completo** | ~2-3 minutos | ~30 segundos |
| **Con rollback** | ~5-10 minutos | ~1-2 minutos |

---

## 🎯 Resultado Esperado

Después del despliegue exitoso:

✅ **Corrección Aplicada**:
- Progreso del proyecto se obtiene de actividad raíz (nivel_esquema=1)
- Valores consistentes entre listado y detalle
- No más discrepancias (12.1% vs 13%)

✅ **Sistema Funcionando**:
- Login operativo
- Listado de proyectos carga
- Validación de avances funciona
- Historial de correcciones preservado

✅ **Performance**:
- Carga más rápida (no calcula, solo lee)
- Logs limpios sin warnings innecesarios

---

**Actualizado**: 15/01/2026  
**Versión**: 2.1 - Progreso desde Actividad Raíz  
**Estado**: ✅ Listo para Despliegue en Producción
