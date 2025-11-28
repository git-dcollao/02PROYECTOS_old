-- Script para corregir codificación UTF-8 en la base de datos
-- Ejecutar dentro del contenedor MySQL con charset utf8mb4

SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;

-- Actualizar áreas con codificación correcta
UPDATE `area` SET `nombre` = 'Administración' WHERE `id` = 1;
UPDATE `area` SET `descripcion` = 'Área de administración general' WHERE `id` = 1;
UPDATE `area` SET `nombre` = 'SALUD' WHERE `id` = 5;
UPDATE `area` SET `descripcion` = 'Área de gestión de salud' WHERE `id` = 5;

-- Actualizar páginas con codificación correcta
UPDATE `pages` SET `name` = 'Gestión de Permisos' WHERE `route` = '/permissions/';
UPDATE `pages` SET `name` = 'Iniciar Sesión' WHERE `route` = '/auth/login';
UPDATE `pages` SET `name` = 'Cerrar Sesión' WHERE `route` = '/auth/logout';
UPDATE `pages` SET `name` = 'Administración' WHERE `route` LIKE '/admin%';
UPDATE `pages` SET `name` = 'Configuración' WHERE `name` LIKE '%Config%';

-- Actualizar tipologías si existen
UPDATE `tipologia` SET `nombre` = REPLACE(`nombre`, 'TipologÃ­a', 'Tipología');
UPDATE `tipologia` SET `nombre` = REPLACE(`nombre`, 'Ãrea', 'Área');

-- Actualizar descripciones generales que puedan tener caracteres corruptos
UPDATE `area` SET `descripcion` = REPLACE(`descripcion`, 'Ãrea', 'Área');
UPDATE `area` SET `descripcion` = REPLACE(`descripcion`, 'Administraci Ã³n', 'Administración');
UPDATE `area` SET `descripcion` = REPLACE(`descripcion`, 'gesti Ã³n', 'gestión');

-- Actualizar estados
UPDATE `estado` SET `nombre` = REPLACE(`nombre`, 'Solic', 'Solicitud');
UPDATE `estado` SET `nombre` = REPLACE(`nombre`, 'itud', 'itud');

COMMIT;

SELECT 'Codificación corregida exitosamente' AS resultado;
