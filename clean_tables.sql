SET FOREIGN_KEY_CHECKS=0;

-- Limpiar páginas y permisos
TRUNCATE TABLE page_permissions;
TRUNCATE TABLE pages;

-- Limpiar áreas y trabajadores
TRUNCATE TABLE trabajador_areas;
DELETE FROM trabajador WHERE id > 0;
TRUNCATE TABLE area;

SET FOREIGN_KEY_CHECKS=1;

SELECT 'Tablas limpiadas exitosamente' AS resultado;
