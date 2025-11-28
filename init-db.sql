-- Crear la base de datos si no existe
CREATE DATABASE IF NOT EXISTS proyectosDB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Usar la base de datos
USE proyectosDB;

-- Crear el usuario si no existe
CREATE USER IF NOT EXISTS 'proyectos_admin'@'%' IDENTIFIED BY '123456!#Td';

-- Otorgar todos los privilegios al usuario
GRANT ALL PRIVILEGES ON proyectosDB.* TO 'proyectos_admin'@'%';

-- Aplicar los cambios
FLUSH PRIVILEGES;

-- Configuraciones de optimización
-- SET GLOBAL innodb_buffer_pool_size = 134217728;
-- SET GLOBAL innodb_log_file_size = 33554432;
SET GLOBAL innodb_flush_log_at_trx_commit = 2;

-- Verificar que la base de datos se creó correctamente
SELECT 'Base de datos proyectosDB inicializada correctamente' AS mensaje;
