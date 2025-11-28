-- ============================================================================
-- Script para eliminar tablas EtapaN1, EtapaN2, EtapaN3, EtapaN4
-- ============================================================================
-- Fecha: 2025-11-05
-- Propósito: Eliminar tablas de etapas jerárquicas que ya no se utilizan
-- ============================================================================

-- IMPORTANTE: Este script deshabilitará temporalmente la verificación de foreign keys
-- y las volverá a habilitar al final.

SET FOREIGN_KEY_CHECKS = 0;

-- Eliminar tablas en orden inverso de dependencias (de hijo a padre)
-- para evitar problemas de foreign keys

-- 1. Eliminar EtapaN4 (nivel más bajo - hoja)
DROP TABLE IF EXISTS `etapan4`;
SELECT '✅ Tabla etapan4 eliminada' as Status;

-- 2. Eliminar EtapaN3
DROP TABLE IF EXISTS `etapan3`;
SELECT '✅ Tabla etapan3 eliminada' as Status;

-- 3. Eliminar EtapaN2
DROP TABLE IF EXISTS `etapan2`;
SELECT '✅ Tabla etapan2 eliminada' as Status;

-- 4. Eliminar EtapaN1 (nivel más alto - raíz)
DROP TABLE IF EXISTS `etapan1`;
SELECT '✅ Tabla etapan1 eliminada' as Status;

-- Volver a habilitar verificación de foreign keys
SET FOREIGN_KEY_CHECKS = 1;

-- Verificación: Listar todas las tablas para confirmar eliminación
SELECT '🔍 Verificando tablas restantes...' as Status;
SHOW TABLES;

SELECT '✅ Script completado exitosamente' as Status;

-- ============================================================================
-- NOTAS:
-- - Las tablas EtapaN1-N4 eran parte de un sistema jerárquico de etapas
--   que ya no se utiliza en la versión actual del sistema
-- - Los modelos ya fueron removidos de app/models.py
-- - Las referencias ya fueron removidas de app/seeds.py
-- - Este script completa la limpieza eliminando las tablas de la BD
-- ============================================================================
