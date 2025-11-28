-- ============================================================
-- SCRIPT DE CORRECCIÓN COMPLETA DE CODIFICACIÓN UTF-8
-- ============================================================

SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;
SET FOREIGN_KEY_CHECKS=0;

-- ============================================================
-- 1. CORREGIR TABLA: area
-- ============================================================
UPDATE `area` SET 
    `nombre` = REPLACE(REPLACE(REPLACE(`nombre`, 'AdministraciÃ³n', 'Administración'), 'Ã¡', 'á'), 'Ã³', 'ó'),
    `descripcion` = REPLACE(REPLACE(REPLACE(REPLACE(`descripcion`, 'Ãrea', 'Área'), 'AdministraciÃ³n', 'Administración'), 'gestiÃ³n', 'gestión'), 'Ã¡', 'á')
WHERE `nombre` LIKE '%Ã%' OR `descripcion` LIKE '%Ã%';

-- ============================================================
-- 2. CORREGIR TABLA: pages (menú y páginas)
-- ============================================================
UPDATE `pages` SET 
    `name` = REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(
        `name`, 
        'GestiÃ³n', 'Gestión'),
        'AdministraciÃ³n', 'Administración'),
        'SesiÃ³n', 'Sesión'),
        'Ãreas', 'Áreas'),
        'TipologÃ­as', 'Tipologías'),
        'ConfiguraciÃ³n', 'Configuración'),
    `description` = REPLACE(REPLACE(REPLACE(
        COALESCE(`description`, ''),
        'GestiÃ³n', 'Gestión'),
        'AdministraciÃ³n', 'Administración'),
        'Ãrea', 'Área')
WHERE `name` LIKE '%Ã%' OR `description` LIKE '%Ã%';

-- ============================================================
-- 3. CORREGIR TABLA: categories (categorías de permisos)
-- ============================================================
UPDATE `categories` SET 
    `name` = REPLACE(REPLACE(REPLACE(
        `name`,
        'GestiÃ³n', 'Gestión'),
        'AdministraciÃ³n', 'Administración'),
        'Ã¡', 'á'),
    `description` = REPLACE(REPLACE(REPLACE(
        COALESCE(`description`, ''),
        'GestiÃ³n', 'Gestión'),
        'AdministraciÃ³n', 'Administración'),
        'Ã¡', 'á')
WHERE `name` LIKE '%Ã%' OR `description` LIKE '%Ã%';

-- ============================================================
-- 4. CORREGIR TABLA: estado
-- ============================================================
UPDATE `estado` SET 
    `nombre` = REPLACE(REPLACE(REPLACE(REPLACE(
        `nombre`,
        'SolicitudÃ', 'Solicitud'),
        'EjecuciÃ³n', 'Ejecución'),
        'finalizaciÃ³n', 'finalización'),
        'revisiÃ³n', 'revisión'),
    `descripcion` = REPLACE(REPLACE(
        COALESCE(`descripcion`, ''),
        'SolicitudÃ', 'Solicitud'),
        'EjecuciÃ³n', 'Ejecución')
WHERE `nombre` LIKE '%Ã%' OR `descripcion` LIKE '%Ã%';

-- ============================================================
-- 5. CORREGIR TABLA: tipologia
-- ============================================================
UPDATE `tipologia` SET 
    `nombre` = REPLACE(REPLACE(REPLACE(
        `nombre`,
        'TipologÃ­a', 'Tipología'),
        'construcciÃ³n', 'construcción'),
        'infraestructuraÃ', 'infraestructura'),
    `descripcion` = REPLACE(REPLACE(
        COALESCE(`descripcion`, ''),
        'TipologÃ­a', 'Tipología'),
        'Ã¡', 'á')
WHERE `nombre` LIKE '%Ã%' OR `descripcion` LIKE '%Ã%';

-- ============================================================
-- 6. CORREGIR TABLA: fase
-- ============================================================
UPDATE `fase` SET 
    `nombre` = REPLACE(REPLACE(REPLACE(
        `nombre`,
        'DiseÃ±o', 'Diseño'),
        'EjecuciÃ³n', 'Ejecución'),
        'FinalizaciÃ³n', 'Finalización'),
    `descripcion` = REPLACE(REPLACE(
        COALESCE(`descripcion`, ''),
        'DiseÃ±o', 'Diseño'),
        'EjecuciÃ³n', 'Ejecución')
WHERE `nombre` LIKE '%Ã%' OR `descripcion` LIKE '%Ã%';

-- ============================================================
-- 7. CORREGIR TABLA: financiamiento
-- ============================================================
UPDATE `financiamiento` SET 
    `nombre` = REPLACE(REPLACE(
        `nombre`,
        'pÃºblico', 'público'),
        'inversiÃ³n', 'inversión'),
    `descripcion` = REPLACE(REPLACE(
        COALESCE(`descripcion`, ''),
        'pÃºblico', 'público'),
        'inversiÃ³n', 'inversión')
WHERE `nombre` LIKE '%Ã%' OR `descripcion` LIKE '%Ã%';

-- ============================================================
-- 8. CORREGIR TABLA: especialidad
-- ============================================================
UPDATE `especialidad` SET 
    `nombre` = REPLACE(REPLACE(REPLACE(
        `nombre`,
        'ElÃ©ctrica', 'Eléctrica'),
        'hidrÃ¡ulica', 'hidráulica'),
        'construcciÃ³n', 'construcción'),
    `descripcion` = REPLACE(REPLACE(
        COALESCE(`descripcion`, ''),
        'ElÃ©ctrica', 'Eléctrica'),
        'construcciÃ³n', 'construcción')
WHERE `nombre` LIKE '%Ã%' OR `descripcion` LIKE '%Ã%';

-- ============================================================
-- 9. CORREGIR TABLA: sector
-- ============================================================
UPDATE `sector` SET 
    `nombre` = REPLACE(REPLACE(REPLACE(
        `nombre`,
        'EducaciÃ³n', 'Educación'),
        'AdministraciÃ³n', 'Administración'),
        'Ã¡', 'á'),
    `descripcion` = REPLACE(REPLACE(
        COALESCE(`descripcion`, ''),
        'EducaciÃ³n', 'Educación'),
        'Ã¡', 'á')
WHERE `nombre` LIKE '%Ã%' OR `descripcion` LIKE '%Ã%';

-- ============================================================
-- 10. CORREGIR TABLA: tiporecinto
-- ============================================================
UPDATE `tiporecinto` SET 
    `nombre` = REPLACE(REPLACE(
        `nombre`,
        'educaciÃ³n', 'educación'),
        'administraciÃ³n', 'administración'),
    `descripcion` = REPLACE(
        COALESCE(`descripcion`, ''),
        'Ã¡', 'á')
WHERE `nombre` LIKE '%Ã%' OR `descripcion` LIKE '%Ã%';

-- ============================================================
-- 11. CORREGIR TABLA: recinto
-- ============================================================
UPDATE `recinto` SET 
    `nombre` = REPLACE(REPLACE(
        `nombre`,
        'Municipalidad', 'Municipalidad'),
        'Ã±', 'ñ'),
    `descripcion` = REPLACE(REPLACE(
        COALESCE(`descripcion`, ''),
        'administraciÃ³n', 'administración'),
        'Ã¡', 'á')
WHERE `nombre` LIKE '%Ã%' OR `descripcion` LIKE '%Ã%';

-- ============================================================
-- 12. CORREGIR TABLA: requerimiento (proyectos)
-- ============================================================
UPDATE `requerimiento` SET 
    `nombre` = REPLACE(REPLACE(REPLACE(
        `nombre`,
        'construcciÃ³n', 'construcción'),
        'remodelacionÃ', 'remodelación'),
        'Ã±', 'ñ'),
    `descripcion` = REPLACE(REPLACE(
        COALESCE(`descripcion`, ''),
        'construcciÃ³n', 'construcción'),
        'Ã¡', 'á')
WHERE `nombre` LIKE '%Ã%' OR `descripcion` LIKE '%Ã%';

-- ============================================================
-- 13. CORREGIR TABLA: trabajador (usuarios)
-- ============================================================
UPDATE `trabajador` SET 
    `nombre` = REPLACE(REPLACE(
        `nombre`,
        'AdministraciÃ³n', 'Administración'),
        'Ã±', 'ñ'),
    `profesion` = REPLACE(
        COALESCE(`profesion`, ''),
        'ingenierÃ­a', 'ingeniería')
WHERE `nombre` LIKE '%Ã%' OR `profesion` LIKE '%Ã%';

-- ============================================================
-- CORRECCIONES ADICIONALES GLOBALES
-- ============================================================

-- Reemplazos comunes en todas las tablas que puedan tener texto
-- (Agregar más según sea necesario)

-- Correcciones de vocales con tilde
SET @fix_a = 'Ã¡';
SET @fix_e = 'Ã©';
SET @fix_i = 'Ã­';
SET @fix_o = 'Ã³';
SET @fix_u = 'Ãº';
SET @fix_n = 'Ã±';
SET @fix_A = 'Ã';

-- Aplicar a área
UPDATE `area` SET 
    `nombre` = REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(`nombre`, @fix_a, 'á'), @fix_e, 'é'), @fix_i, 'í'), @fix_o, 'ó'), @fix_u, 'ú'), @fix_n, 'ñ'), @fix_A, 'Á'),
    `descripcion` = REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(COALESCE(`descripcion`, ''), @fix_a, 'á'), @fix_e, 'é'), @fix_i, 'í'), @fix_o, 'ó'), @fix_u, 'ú'), @fix_n, 'ñ'), @fix_A, 'Á');

-- Aplicar a pages
UPDATE `pages` SET 
    `name` = REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(`name`, @fix_a, 'á'), @fix_e, 'é'), @fix_i, 'í'), @fix_o, 'ó'), @fix_u, 'ú'), @fix_n, 'ñ'), @fix_A, 'Á'),
    `description` = REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(COALESCE(`description`, ''), @fix_a, 'á'), @fix_e, 'é'), @fix_i, 'í'), @fix_o, 'ó'), @fix_u, 'ú'), @fix_n, 'ñ'), @fix_A, 'Á');

-- Aplicar a categories
UPDATE `categories` SET 
    `name` = REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(`name`, @fix_a, 'á'), @fix_e, 'é'), @fix_i, 'í'), @fix_o, 'ó'), @fix_u, 'ú'), @fix_n, 'ñ'), @fix_A, 'Á'),
    `description` = REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(COALESCE(`description`, ''), @fix_a, 'á'), @fix_e, 'é'), @fix_i, 'í'), @fix_o, 'ó'), @fix_u, 'ú'), @fix_n, 'ñ'), @fix_A, 'Á');

SET FOREIGN_KEY_CHECKS=1;
COMMIT;

-- ============================================================
-- VERIFICACIÓN
-- ============================================================
SELECT '✅ CORRECCIÓN COMPLETADA' AS status;
SELECT 'Verificando áreas...' AS step;
SELECT id, nombre, descripcion FROM `area` LIMIT 5;
SELECT 'Verificando páginas...' AS step;
SELECT id, name, route FROM `pages` WHERE name LIKE '%ión%' OR name LIKE '%Gest%' LIMIT 5;
SELECT 'Verificando categorías...' AS step;
SELECT id, name FROM `categories` LIMIT 5;
