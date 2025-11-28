-- Corrección de doble codificación UTF-8
SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;
SET FOREIGN_KEY_CHECKS=0;

-- Reemplazos de doble codificación a UTF-8 correcto
-- ó = \xC3\xB3 en UTF-8, pero si se lee como Latin-1 se convierte en Ã³
-- Y si eso se vuelve a codificar, se convierte en Ã³ (lo que vemos)

-- TABLA: area
UPDATE `area` SET 
    `nombre` = CONVERT(CAST(CONVERT(`nombre` USING latin1) AS BINARY) USING utf8mb4),
    `descripcion` = CONVERT(CAST(CONVERT(COALESCE(`descripcion`, '') USING latin1) AS BINARY) USING utf8mb4);

-- TABLA: pages
UPDATE `pages` SET 
    `name` = CONVERT(CAST(CONVERT(`name` USING latin1) AS BINARY) USING utf8mb4),
    `description` = CONVERT(CAST(CONVERT(COALESCE(`description`, '') USING latin1) AS BINARY) USING utf8mb4);

-- TABLA: categories
UPDATE `categories` SET 
    `name` = CONVERT(CAST(CONVERT(`name` USING latin1) AS BINARY) USING utf8mb4),
    `description` = CONVERT(CAST(CONVERT(COALESCE(`description`, '') USING latin1) AS BINARY) USING utf8mb4);

-- TABLA: estado
UPDATE `estado` SET 
    `nombre` = CONVERT(CAST(CONVERT(`nombre` USING latin1) AS BINARY) USING utf8mb4),
    `descripcion` = CONVERT(CAST(CONVERT(COALESCE(`descripcion`, '') USING latin1) AS BINARY) USING utf8mb4);

-- TABLA: tipologia
UPDATE `tipologia` SET 
    `nombre` = CONVERT(CAST(CONVERT(`nombre` USING latin1) AS BINARY) USING utf8mb4),
    `descripcion` = CONVERT(CAST(CONVERT(COALESCE(`descripcion`, '') USING latin1) AS BINARY) USING utf8mb4);

-- TABLA: fase
UPDATE `fase` SET 
    `nombre` = CONVERT(CAST(CONVERT(`nombre` USING latin1) AS BINARY) USING utf8mb4),
    `descripcion` = CONVERT(CAST(CONVERT(COALESCE(`descripcion`, '') USING latin1) AS BINARY) USING utf8mb4);

-- TABLA: sector
UPDATE `sector` SET 
    `nombre` = CONVERT(CAST(CONVERT(`nombre` USING latin1) AS BINARY) USING utf8mb4),
    `descripcion` = CONVERT(CAST(CONVERT(COALESCE(`descripcion`, '') USING latin1) AS BINARY) USING utf8mb4);

-- TABLA: especialidad
UPDATE `especialidad` SET 
    `nombre` = CONVERT(CAST(CONVERT(`nombre` USING latin1) AS BINARY) USING utf8mb4),
    `descripcion` = CONVERT(CAST(CONVERT(COALESCE(`descripcion`, '') USING latin1) AS BINARY) USING utf8mb4);

-- TABLA: financiamiento
UPDATE `financiamiento` SET 
    `nombre` = CONVERT(CAST(CONVERT(`nombre` USING latin1) AS BINARY) USING utf8mb4),
    `descripcion` = CONVERT(CAST(CONVERT(COALESCE(`descripcion`, '') USING latin1) AS BINARY) USING utf8mb4);

-- TABLA: trabajador
UPDATE `trabajador` SET 
    `nombre` = CONVERT(CAST(CONVERT(`nombre` USING latin1) AS BINARY) USING utf8mb4),
    `profesion` = CONVERT(CAST(CONVERT(COALESCE(`profesion`, '') USING latin1) AS BINARY) USING utf8mb4);

-- TABLA: requerimiento
UPDATE `requerimiento` SET 
    `nombre` = CONVERT(CAST(CONVERT(`nombre` USING latin1) AS BINARY) USING utf8mb4),
    `descripcion` = CONVERT(CAST(CONVERT(COALESCE(`descripcion`, '') USING latin1) AS BINARY) USING utf8mb4);

SET FOREIGN_KEY_CHECKS=1;
COMMIT;

SELECT 'Corrección de doble codificación completada' AS resultado;
