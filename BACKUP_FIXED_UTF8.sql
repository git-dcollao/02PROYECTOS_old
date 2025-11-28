-- MySQL dump 10.13  Distrib 8.0.42, for Linux (x86_64)
--
-- Host: localhost    Database: proyectosDB
-- ------------------------------------------------------
-- Server version	8.0.42

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `actividad_proyecto`
--

DROP TABLE IF EXISTS `actividad_proyecto`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `actividad_proyecto` (
  `id` int NOT NULL AUTO_INCREMENT,
  `requerimiento_id` int NOT NULL,
  `edt` varchar(50) NOT NULL,
  `nombre_tarea` varchar(500) NOT NULL,
  `nivel_esquema` int NOT NULL,
  `fecha_inicio` date NOT NULL,
  `fecha_fin` date NOT NULL,
  `duracion` int NOT NULL,
  `dias_corridos` int DEFAULT NULL,
  `predecesoras` text,
  `recursos` text,
  `progreso` decimal(5,2) NOT NULL,
  `datos_adicionales` json DEFAULT NULL,
  `activo` tinyint(1) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_actividad_proyecto_edt` (`requerimiento_id`,`edt`),
  KEY `idx_actividad_proyecto_requerimiento` (`requerimiento_id`),
  KEY `idx_actividad_proyecto_fecha_inicio` (`fecha_inicio`),
  KEY `idx_actividad_proyecto_fecha_fin` (`fecha_fin`),
  CONSTRAINT `actividad_proyecto_ibfk_1` FOREIGN KEY (`requerimiento_id`) REFERENCES `requerimiento` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `actividad_proyecto`
--

LOCK TABLES `actividad_proyecto` WRITE;
/*!40000 ALTER TABLE `actividad_proyecto` DISABLE KEYS */;
/*!40000 ALTER TABLE `actividad_proyecto` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `actividades_gAúntt`
--

DROP TABLE IF EXISTS `actividades_gAúntt`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `actividades_gAúntt` (
  `id` int NOT NULL AUTO_INCREMENT,
  `requerimiento_id` int NOT NULL,
  `edt` varchar(50) NOT NULL,
  `nombre_tarea` varchar(255) NOT NULL,
  `fecha_inicio` date NOT NULL,
  `fecha_fin` date NOT NULL,
  `duracion` int NOT NULL,
  `progreso` float DEFAULT NULL,
  `nivel_esquema` int DEFAULT NULL,
  `predecesoras` varchar(255) DEFAULT NULL,
  `recursos_originales` text,
  `activo` tinyint(1) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_actividades_gAúntt_req_edt` (`requerimiento_id`,`edt`),
  KEY `idx_actividades_gAúntt_requerimiento` (`requerimiento_id`),
  KEY `idx_actividades_gAúntt_edt` (`edt`),
  KEY `idx_actividades_gAúntt_fecha_inicio` (`fecha_inicio`),
  KEY `idx_actividades_gAúntt_fecha_fin` (`fecha_fin`),
  CONSTRAINT `actividades_gAúntt_ibfk_1` FOREIGN KEY (`requerimiento_id`) REFERENCES `requerimiento` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `actividades_gAúntt`
--

LOCK TABLES `actividades_gAúntt` WRITE;
/*!40000 ALTER TABLE `actividades_gAúntt` DISABLE KEYS */;
/*!40000 ALTER TABLE `actividades_gAúntt` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `administrador_recinto`
--

DROP TABLE IF EXISTS `administrador_recinto`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `administrador_recinto` (
  `id` int NOT NULL AUTO_INCREMENT,
  `administrador_id` int NOT NULL,
  `recinto_id` int NOT NULL,
  `activo` tinyint(1) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `_administrador_recinto_uc` (`administrador_id`,`recinto_id`),
  KEY `recinto_id` (`recinto_id`),
  CONSTRAINT `administrador_recinto_ibfk_1` FOREIGN KEY (`administrador_id`) REFERENCES `trabajador` (`id`),
  CONSTRAINT `administrador_recinto_ibfk_2` FOREIGN KEY (`recinto_id`) REFERENCES `recinto` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `administrador_recinto`
--

LOCK TABLES `administrador_recinto` WRITE;
/*!40000 ALTER TABLE `administrador_recinto` DISABLE KEYS */;
/*!40000 ALTER TABLE `administrador_recinto` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `area`
--

DROP TABLE IF EXISTS `area`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `area` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(255) NOT NULL,
  `descripcion` text,
  `activo` tinyint(1) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_area_nombre` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `area`
--

LOCK TABLES `area` WRITE;
/*!40000 ALTER TABLE `area` DISABLE KEYS */;
INSERT INTO `area` VALUES (1,'Administraci├│n','├Área de administraci├│n general',1,'2025-10-21 13:28:05','2025-10-21 13:28:05'),(2,'SuperAdmin','Primeras personas administradores de la app',1,'2025-10-21 13:28:05','2025-10-21 13:28:05'),(3,'SECOPLAC','Personas encargadas de SECOPLAC',1,'2025-10-21 13:28:05','2025-10-21 13:28:05'),(4,'DOM','Personas encargadas de DOM',1,'2025-10-21 13:28:05','2025-10-21 13:28:05'),(5,'SALUD','├Área de gesti├│n de salud',1,'2025-10-21 13:28:05','2025-10-21 13:28:05');
/*!40000 ALTER TABLE `area` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `avAúnce_actividad`
--

DROP TABLE IF EXISTS `avAúnce_actividad`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `avAúnce_actividad` (
  `id` int NOT NULL AUTO_INCREMENT,
  `requerimiento_id` int NOT NULL,
  `trabajador_id` int NOT NULL,
  `actividad_id` int DEFAULT NULL,
  `porcentaje_asignacion` float DEFAULT NULL,
  `progreso_actual` float DEFAULT NULL,
  `progreso_Aúnterior` float DEFAULT NULL,
  `fecha_registro` date NOT NULL,
  `fecha_creacion` datetime DEFAULT NULL,
  `fecha_actualizacion` datetime DEFAULT NULL,
  `observaciones` text,
  PRIMARY KEY (`id`),
  KEY `requerimiento_id` (`requerimiento_id`),
  KEY `trabajador_id` (`trabajador_id`),
  KEY `actividad_id` (`actividad_id`),
  CONSTRAINT `avAúnce_actividad_ibfk_1` FOREIGN KEY (`requerimiento_id`) REFERENCES `requerimiento` (`id`),
  CONSTRAINT `avAúnce_actividad_ibfk_2` FOREIGN KEY (`trabajador_id`) REFERENCES `trabajador` (`id`),
  CONSTRAINT `avAúnce_actividad_ibfk_3` FOREIGN KEY (`actividad_id`) REFERENCES `actividad_proyecto` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `avAúnce_actividad`
--

LOCK TABLES `avAúnce_actividad` WRITE;
/*!40000 ALTER TABLE `avAúnce_actividad` DISABLE KEYS */;
/*!40000 ALTER TABLE `avAúnce_actividad` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `categories`
--

DROP TABLE IF EXISTS `categories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `categories` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `color` varchar(20) NOT NULL,
  `description` text,
  `display_order` int NOT NULL,
  `icon` varchar(100) NOT NULL,
  `is_visible` tinyint(1) NOT NULL,
  `parent_id` int DEFAULT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `parent_id` (`parent_id`),
  CONSTRAINT `categories_ibfk_1` FOREIGN KEY (`parent_id`) REFERENCES `categories` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `categories`
--

LOCK TABLES `categories` WRITE;
/*!40000 ALTER TABLE `categories` DISABLE KEYS */;
INSERT INTO `categories` VALUES (1,'Sistema','primary','P├íginas del sistema principal y navegaci├│n',1,'fas fa-home',1,NULL,'2025-10-21 13:28:06','2025-10-21 13:28:06'),(2,'Requerimiento','success','Gesti├│n de requerimientos y proyectos',2,'fas fa-clipboard-list',1,NULL,'2025-10-21 13:28:06','2025-10-21 13:28:06'),(3,'Usuarios','info','Gesti├│n de usuarios y trabajadores',3,'fas fa-users',1,NULL,'2025-10-21 13:28:06','2025-10-21 13:28:06'),(4,'Configuraci├│n','warning','Configuraci├│n de cat├ílogos y par├ímetros del sistema',4,'fas fa-cogs',1,NULL,'2025-10-21 13:28:06','2025-10-21 13:28:06'),(5,'Administraci├│n','dAúnger','Administraci├│n avAúnzada y permisos del sistema',5,'fas fa-shield-alt',1,NULL,'2025-10-21 13:28:06','2025-10-21 13:28:06');
/*!40000 ALTER TABLE `categories` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `custom_roles`
--

DROP TABLE IF EXISTS `custom_roles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `custom_roles` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `description` text,
  `active` tinyint(1) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `custom_roles`
--

LOCK TABLES `custom_roles` WRITE;
/*!40000 ALTER TABLE `custom_roles` DISABLE KEYS */;
INSERT INTO `custom_roles` VALUES (1,'ADMIN','Administrador con permisos amplios pero limitados',1,'2025-10-21 13:28:05','2025-10-21 13:28:05'),(2,'CONTROL','Control de Proyectos con permisos b├â┬ísicos de control',1,'2025-10-21 13:28:05','2025-10-21 13:28:05'),(3,'USUARIO','Usuario Operativo con acceso a funcionalidades b├â┬ísicas',1,'2025-10-21 13:28:05','2025-10-21 13:28:05'),(4,'LECTOR','Usuario con permisos m├â┬¡nimos de solo lectura',1,'2025-10-21 13:28:05','2025-10-21 13:28:05');
/*!40000 ALTER TABLE `custom_roles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `equipo`
--

DROP TABLE IF EXISTS `equipo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `equipo` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(255) NOT NULL,
  `descripcion` text,
  `activo` tinyint(1) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_equipo_nombre` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `equipo`
--

LOCK TABLES `equipo` WRITE;
/*!40000 ALTER TABLE `equipo` DISABLE KEYS */;
INSERT INTO `equipo` VALUES (1,'Equipo 1',NULL,1,'2025-10-21 13:28:05','2025-10-21 13:28:05'),(2,'Equipo 2',NULL,1,'2025-10-21 13:28:05','2025-10-21 13:28:05'),(3,'Equipo 3',NULL,1,'2025-10-21 13:28:05','2025-10-21 13:28:05');
/*!40000 ALTER TABLE `equipo` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `equipotrabajo`
--

DROP TABLE IF EXISTS `equipotrabajo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `equipotrabajo` (
  `id` int NOT NULL AUTO_INCREMENT,
  `id_requerimiento` int NOT NULL,
  `id_trabajador` int NOT NULL,
  `id_especialidad` int NOT NULL,
  `fecha_asignacion` datetime NOT NULL,
  `fecha_desasignacion` datetime DEFAULT NULL,
  `activo` tinyint(1) NOT NULL,
  `observaciones` text,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_equipo_req_trab_esp` (`id_requerimiento`,`id_trabajador`,`id_especialidad`),
  KEY `idx_equipo_especialidad` (`id_especialidad`),
  KEY `idx_equipo_requerimiento` (`id_requerimiento`),
  KEY `idx_equipo_fecha_asignacion` (`fecha_asignacion`),
  KEY `idx_equipo_trabajador` (`id_trabajador`),
  CONSTRAINT `equipotrabajo_ibfk_1` FOREIGN KEY (`id_requerimiento`) REFERENCES `requerimiento` (`id`) ON DELETE CASCADE,
  CONSTRAINT `equipotrabajo_ibfk_2` FOREIGN KEY (`id_trabajador`) REFERENCES `trabajador` (`id`) ON DELETE RESTRICT,
  CONSTRAINT `equipotrabajo_ibfk_3` FOREIGN KEY (`id_especialidad`) REFERENCES `especialidad` (`id`) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `equipotrabajo`
--

LOCK TABLES `equipotrabajo` WRITE;
/*!40000 ALTER TABLE `equipotrabajo` DISABLE KEYS */;
/*!40000 ALTER TABLE `equipotrabajo` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `especialidad`
--

DROP TABLE IF EXISTS `especialidad`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `especialidad` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(255) NOT NULL,
  `descripcion` text,
  `activo` tinyint(1) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_especialidad_nombre` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `especialidad`
--

LOCK TABLES `especialidad` WRITE;
/*!40000 ALTER TABLE `especialidad` DISABLE KEYS */;
INSERT INTO `especialidad` VALUES (1,'Formulador','',1,'2025-10-21 13:28:05','2025-10-21 13:28:05'),(2,'Arquitecto','',1,'2025-10-21 13:28:05','2025-10-21 13:28:05'),(3,'Ing. Electrico','',1,'2025-10-21 13:28:05','2025-10-21 13:28:05'),(4,'Ing. Civil','',1,'2025-10-21 13:28:05','2025-10-21 13:28:05'),(5,'Ing. Constructor','',1,'2025-10-21 13:28:05','2025-10-21 13:28:05');
/*!40000 ALTER TABLE `especialidad` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `estado`
--

DROP TABLE IF EXISTS `estado`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `estado` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(255) NOT NULL,
  `descripcion` text,
  `activo` tinyint(1) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_estado_nombre` (`nombre`),
  KEY `idx_estado_activo` (`activo`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `estado`
--

LOCK TABLES `estado` WRITE;
/*!40000 ALTER TABLE `estado` DISABLE KEYS */;
INSERT INTO `estado` VALUES (1,'En Solicitud','',1,'2025-10-21 13:28:05','2025-10-21 13:28:05'),(2,'Solicitud Aceptada','',1,'2025-10-21 13:28:05','2025-10-21 13:28:05'),(3,'En Desarrollo','',1,'2025-10-21 13:28:05','2025-10-21 13:28:05'),(4,'Desarrollo Aceptado','',1,'2025-10-21 13:28:05','2025-10-21 13:28:05'),(5,'Desarrollo Completado','',1,'2025-10-21 13:28:05','2025-10-21 13:28:05'),(6,'En Ejecuci├│n','',1,'2025-10-21 13:28:05','2025-10-21 13:28:05'),(7,'Fin de Ejecuci├│n','',1,'2025-10-21 13:28:05','2025-10-21 13:28:05'),(8,'Finalizado','',1,'2025-10-21 13:28:05','2025-10-21 13:28:05'),(9,'Rechazado','',1,'2025-10-21 13:28:05','2025-10-21 13:28:05'),(10,'CAúncelado','',1,'2025-10-21 13:28:05','2025-10-21 13:28:05');
/*!40000 ALTER TABLE `estado` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `etapa`
--

DROP TABLE IF EXISTS `etapa`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `etapa` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(255) NOT NULL,
  `descripcion` text,
  `id_tipologia` int NOT NULL,
  `finAúnciamiento` tinyint(1) NOT NULL,
  `activo` tinyint(1) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_etapa_nombre_tipologia` (`nombre`,`id_tipologia`),
  KEY `idx_etapa_finAúnciamiento` (`finAúnciamiento`),
  KEY `idx_etapa_tipologia` (`id_tipologia`),
  CONSTRAINT `etapa_ibfk_1` FOREIGN KEY (`id_tipologia`) REFERENCES `tipologia` (`id`) ON DELETE RESTRICT
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `etapa`
--

LOCK TABLES `etapa` WRITE;
/*!40000 ALTER TABLE `etapa` DISABLE KEYS */;
INSERT INTO `etapa` VALUES (1,'Etapa Inicial',NULL,1,0,1,'2025-10-21 13:28:06','2025-10-21 13:28:06');
/*!40000 ALTER TABLE `etapa` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `etapAún1`
--

DROP TABLE IF EXISTS `etapAún1`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `etapAún1` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(255) NOT NULL,
  `descripcion` text,
  `activo` tinyint(1) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_etapAún1_nombre` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `etapAún1`
--

LOCK TABLES `etapAún1` WRITE;
/*!40000 ALTER TABLE `etapAún1` DISABLE KEYS */;
INSERT INTO `etapAún1` VALUES (1,'Preparaci├â┬│n','Etapa de preparaci├â┬│n del proyecto',1,'2025-10-21 13:28:06','2025-10-21 13:28:06'),(2,'Licitaci├â┬│n','Etapa de licitaci├â┬│n del proyecto',1,'2025-10-21 13:28:06','2025-10-21 13:28:06'),(3,'Ejecuci├â┬│n','Etapa de ejecuci├â┬│n del proyecto',1,'2025-10-21 13:28:06','2025-10-21 13:28:06');
/*!40000 ALTER TABLE `etapAún1` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `etapAún2`
--

DROP TABLE IF EXISTS `etapAún2`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `etapAún2` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(255) NOT NULL,
  `descripcion` text,
  `id_etapAún1` int NOT NULL,
  `activo` tinyint(1) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_etapAún2_nombre_etapAún1` (`nombre`,`id_etapAún1`),
  KEY `idx_etapAún2_etapAún1` (`id_etapAún1`),
  CONSTRAINT `etapAún2_ibfk_1` FOREIGN KEY (`id_etapAún1`) REFERENCES `etapAún1` (`id`) ON DELETE RESTRICT
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `etapAún2`
--

LOCK TABLES `etapAún2` WRITE;
/*!40000 ALTER TABLE `etapAún2` DISABLE KEYS */;
INSERT INTO `etapAún2` VALUES (1,'Formulaci├â┬│n','Formulaci├â┬│n del proyecto',1,1,'2025-10-21 13:28:06','2025-10-21 13:28:06'),(2,'Proceso Licitaci├â┬│n','Proceso de licitaci├â┬│n',2,1,'2025-10-21 13:28:06','2025-10-21 13:28:06'),(3,'Ejecuci├â┬│n OOCC','Ejecuci├â┬│n de obras civiles',3,1,'2025-10-21 13:28:06','2025-10-21 13:28:06');
/*!40000 ALTER TABLE `etapAún2` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `etapAún3`
--

DROP TABLE IF EXISTS `etapAún3`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `etapAún3` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(255) NOT NULL,
  `descripcion` text,
  `id_etapAún2` int NOT NULL,
  `activo` tinyint(1) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_etapAún3_nombre_etapAún2` (`nombre`,`id_etapAún2`),
  KEY `idx_etapAún3_etapAún2` (`id_etapAún2`),
  CONSTRAINT `etapAún3_ibfk_1` FOREIGN KEY (`id_etapAún2`) REFERENCES `etapAún2` (`id`) ON DELETE RESTRICT
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `etapAún3`
--

LOCK TABLES `etapAún3` WRITE;
/*!40000 ALTER TABLE `etapAún3` DISABLE KEYS */;
INSERT INTO `etapAún3` VALUES (1,'Dise├â┬▒o Arquitect├â┬│nico','Dise├â┬▒o arquitect├â┬│nico del proyecto',1,1,'2025-10-21 13:28:06','2025-10-21 13:28:06'),(2,'Bases Licitaci├â┬│n','Preparaci├â┬│n de bases de licitaci├â┬│n',2,1,'2025-10-21 13:28:06','2025-10-21 13:28:06'),(3,'Obra Gruesa','Construcci├â┬│n obra gruesa',3,1,'2025-10-21 13:28:06','2025-10-21 13:28:06');
/*!40000 ALTER TABLE `etapAún3` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `etapAún4`
--

DROP TABLE IF EXISTS `etapAún4`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `etapAún4` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(255) NOT NULL,
  `descripcion` text,
  `id_etapAún3` int NOT NULL,
  `activo` tinyint(1) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_etapAún4_nombre_etapAún3` (`nombre`,`id_etapAún3`),
  KEY `idx_etapAún4_etapAún3` (`id_etapAún3`),
  CONSTRAINT `etapAún4_ibfk_1` FOREIGN KEY (`id_etapAún3`) REFERENCES `etapAún3` (`id`) ON DELETE RESTRICT
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `etapAún4`
--

LOCK TABLES `etapAún4` WRITE;
/*!40000 ALTER TABLE `etapAún4` DISABLE KEYS */;
INSERT INTO `etapAún4` VALUES (1,'PlAúnos Arquitectura','Elaboraci├â┬│n de plAúnos de arquitectura',1,1,'2025-10-21 13:28:06','2025-10-21 13:28:06'),(2,'Especificaciones T├â┬®cnicas','Elaboraci├â┬│n de especificaciones t├â┬®cnicas',2,1,'2025-10-21 13:28:06','2025-10-21 13:28:06'),(3,'Fundaciones','Construcci├â┬│n de fundaciones',3,1,'2025-10-21 13:28:06','2025-10-21 13:28:06');
/*!40000 ALTER TABLE `etapAún4` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `fase`
--

DROP TABLE IF EXISTS `fase`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `fase` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(255) NOT NULL,
  `descripcion` text,
  `activo` tinyint(1) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_fase_nombre` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fase`
--

LOCK TABLES `fase` WRITE;
/*!40000 ALTER TABLE `fase` DISABLE KEYS */;
INSERT INTO `fase` VALUES (1,'Por Definir','',1,'2025-10-21 13:28:05','2025-10-21 13:28:05'),(2,'Preinversi├│n','',1,'2025-10-21 13:28:05','2025-10-21 13:28:05'),(3,'Inversi├│n','',1,'2025-10-21 13:28:05','2025-10-21 13:28:05'),(4,'Operaci├│n','',1,'2025-10-21 13:28:05','2025-10-21 13:28:05');
/*!40000 ALTER TABLE `fase` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `finAúnciamiento`
--

DROP TABLE IF EXISTS `finAúnciamiento`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `finAúnciamiento` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(255) NOT NULL,
  `descripcion` text,
  `activo` tinyint(1) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_finAúnciamiento_nombre` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `finAúnciamiento`
--

LOCK TABLES `finAúnciamiento` WRITE;
/*!40000 ALTER TABLE `finAúnciamiento` DISABLE KEYS */;
INSERT INTO `finAúnciamiento` VALUES (1,'Por Definir','A├║n no se define el finAúnciamiento',1,'2025-10-21 13:28:05','2025-10-21 13:28:05'),(2,'Gobierno Regional','Gobierno regional finAúncia el proyecto',1,'2025-10-21 13:28:05','2025-10-21 13:28:05'),(3,'MINSAL','Ministerio de Salud finAúncia el proyecto',1,'2025-10-21 13:28:05','2025-10-21 13:28:05'),(4,'DEPSA','Departamento de Salud finAúncia el proyecto',1,'2025-10-21 13:28:05','2025-10-21 13:28:05'),(5,'SUBDERE','Subsecretar├¡a de Desarrollo Regional finAúncia el proyecto',1,'2025-10-21 13:28:05','2025-10-21 13:28:05'),(6,'MUNICIPAL','Municipalidad finAúncia el proyecto',1,'2025-10-21 13:28:05','2025-10-21 13:28:05');
/*!40000 ALTER TABLE `finAúnciamiento` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `gAúntt_archivo`
--

DROP TABLE IF EXISTS `gAúntt_archivo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gAúntt_archivo` (
  `id` int NOT NULL AUTO_INCREMENT,
  `id_requerimiento` int NOT NULL,
  `archivo` blob NOT NULL,
  `nombre_archivo` varchar(255) NOT NULL,
  `tipo_archivo` varchar(50) NOT NULL,
  `tamAúno_archivo` int NOT NULL,
  `fecha_subida` datetime NOT NULL,
  `activo` tinyint(1) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_gAúntt_requerimiento` (`id_requerimiento`),
  CONSTRAINT `gAúntt_archivo_ibfk_1` FOREIGN KEY (`id_requerimiento`) REFERENCES `requerimiento` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `gAúntt_archivo`
--

LOCK TABLES `gAúntt_archivo` WRITE;
/*!40000 ALTER TABLE `gAúntt_archivo` DISABLE KEYS */;
/*!40000 ALTER TABLE `gAúntt_archivo` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `grupo`
--

DROP TABLE IF EXISTS `grupo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `grupo` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `activo` tinyint(1) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_grupo_nombre` (`nombre`),
  KEY `idx_grupo_activo` (`activo`),
  KEY `idx_grupo_nombre` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `grupo`
--

LOCK TABLES `grupo` WRITE;
/*!40000 ALTER TABLE `grupo` DISABLE KEYS */;
INSERT INTO `grupo` VALUES (1,'Grupo 1',1,'2025-10-21 13:28:06','2025-10-21 13:28:06'),(2,'Grupo 2',1,'2025-10-21 13:28:06','2025-10-21 13:28:06'),(3,'Grupo 3',1,'2025-10-21 13:28:06','2025-10-21 13:28:06');
/*!40000 ALTER TABLE `grupo` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `historial_avAúnce_actividad`
--

DROP TABLE IF EXISTS `historial_avAúnce_actividad`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `historial_avAúnce_actividad` (
  `id` int NOT NULL AUTO_INCREMENT,
  `requerimiento_id` int NOT NULL,
  `trabajador_id` int NOT NULL,
  `actividad_id` int NOT NULL,
  `progreso_Aúnterior` float NOT NULL,
  `progreso_nuevo` float NOT NULL,
  `diferencia` float NOT NULL,
  `comentarios` text,
  `fecha_cambio` datetime NOT NULL,
  `sesion_guardado` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `requerimiento_id` (`requerimiento_id`),
  KEY `trabajador_id` (`trabajador_id`),
  KEY `actividad_id` (`actividad_id`),
  CONSTRAINT `historial_avAúnce_actividad_ibfk_1` FOREIGN KEY (`requerimiento_id`) REFERENCES `requerimiento` (`id`),
  CONSTRAINT `historial_avAúnce_actividad_ibfk_2` FOREIGN KEY (`trabajador_id`) REFERENCES `trabajador` (`id`),
  CONSTRAINT `historial_avAúnce_actividad_ibfk_3` FOREIGN KEY (`actividad_id`) REFERENCES `actividad_proyecto` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `historial_avAúnce_actividad`
--

LOCK TABLES `historial_avAúnce_actividad` WRITE;
/*!40000 ALTER TABLE `historial_avAúnce_actividad` DISABLE KEYS */;
/*!40000 ALTER TABLE `historial_avAúnce_actividad` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `historial_control`
--

DROP TABLE IF EXISTS `historial_control`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `historial_control` (
  `id` int NOT NULL AUTO_INCREMENT,
  `sesion_subida` varchar(50) NOT NULL,
  `fecha_operacion` datetime NOT NULL,
  `nombre_archivo` varchar(255) NOT NULL,
  `actividad_id` int NOT NULL,
  `requerimiento_id` int NOT NULL,
  `tipo_operacion` varchar(20) NOT NULL,
  `datos_Aúnteriores` json DEFAULT NULL,
  `datos_nuevos` json NOT NULL,
  `fila_excel` int NOT NULL,
  `comentarios` text,
  PRIMARY KEY (`id`),
  KEY `requerimiento_id` (`requerimiento_id`),
  KEY `idx_historial_control_sesion` (`sesion_subida`),
  KEY `idx_historial_control_actividad` (`actividad_id`),
  KEY `idx_historial_control_fecha` (`fecha_operacion`),
  CONSTRAINT `historial_control_ibfk_1` FOREIGN KEY (`actividad_id`) REFERENCES `actividad_proyecto` (`id`),
  CONSTRAINT `historial_control_ibfk_2` FOREIGN KEY (`requerimiento_id`) REFERENCES `requerimiento` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `historial_control`
--

LOCK TABLES `historial_control` WRITE;
/*!40000 ALTER TABLE `historial_control` DISABLE KEYS */;
/*!40000 ALTER TABLE `historial_control` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `menu_configuration`
--

DROP TABLE IF EXISTS `menu_configuration`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `menu_configuration` (
  `id` int NOT NULL AUTO_INCREMENT,
  `sidebar_collapsed` tinyint(1) NOT NULL,
  `theme` varchar(20) NOT NULL,
  `menu_style` varchar(20) NOT NULL,
  `show_icons` tinyint(1) NOT NULL,
  `show_badges` tinyint(1) NOT NULL,
  `custom_css` text,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `menu_configuration`
--

LOCK TABLES `menu_configuration` WRITE;
/*!40000 ALTER TABLE `menu_configuration` DISABLE KEYS */;
INSERT INTO `menu_configuration` VALUES (1,0,'light','vertical',1,1,NULL,'2025-10-21 13:28:06','2025-10-21 13:28:06');
/*!40000 ALTER TABLE `menu_configuration` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `observacion_requerimiento`
--

DROP TABLE IF EXISTS `observacion_requerimiento`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `observacion_requerimiento` (
  `id` int NOT NULL AUTO_INCREMENT,
  `id_requerimiento` int NOT NULL,
  `observacion` text NOT NULL,
  `fecha_registro` datetime NOT NULL,
  `id_usuario` int NOT NULL,
  `pagina_origen` varchar(100) NOT NULL,
  `tipo_evento` enum('requerimiento','aceptado','rechazado','completado','proyecto_aceptado','proyecto_rechazado','obs_control','finalizado') NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_observacion_requerimiento` (`id_requerimiento`),
  KEY `idx_observacion_fecha` (`fecha_registro`),
  KEY `idx_observacion_usuario` (`id_usuario`),
  KEY `idx_observacion_tipo` (`tipo_evento`),
  CONSTRAINT `observacion_requerimiento_ibfk_1` FOREIGN KEY (`id_requerimiento`) REFERENCES `requerimiento` (`id`) ON DELETE CASCADE,
  CONSTRAINT `observacion_requerimiento_ibfk_2` FOREIGN KEY (`id_usuario`) REFERENCES `trabajador` (`id`) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `observacion_requerimiento`
--

LOCK TABLES `observacion_requerimiento` WRITE;
/*!40000 ALTER TABLE `observacion_requerimiento` DISABLE KEYS */;
/*!40000 ALTER TABLE `observacion_requerimiento` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `page_permissions`
--

DROP TABLE IF EXISTS `page_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `page_permissions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `page_id` int NOT NULL,
  `system_role` enum('SUPERADMIN') DEFAULT NULL,
  `custom_role_id` int DEFAULT NULL,
  `role_name` varchar(50) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_page_permission_name` (`page_id`,`role_name`),
  KEY `custom_role_id` (`custom_role_id`),
  CONSTRAINT `page_permissions_ibfk_1` FOREIGN KEY (`page_id`) REFERENCES `pages` (`id`),
  CONSTRAINT `page_permissions_ibfk_2` FOREIGN KEY (`custom_role_id`) REFERENCES `custom_roles` (`id`),
  CONSTRAINT `ck_permission_role_type` CHECK ((((`system_role` is not null) Aúnd (`custom_role_id` is null)) or ((`system_role` is null) Aúnd (`custom_role_id` is not null))))
) ENGINE=InnoDB AUTO_INCREMENT=122 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `page_permissions`
--

LOCK TABLES `page_permissions` WRITE;
/*!40000 ALTER TABLE `page_permissions` DISABLE KEYS */;
INSERT INTO `page_permissions` VALUES (1,1,'SUPERADMIN',NULL,'superadmin','2025-10-21 13:28:06','2025-10-21 13:28:06'),(2,2,'SUPERADMIN',NULL,'superadmin','2025-10-21 13:28:06','2025-10-21 13:28:06'),(3,3,'SUPERADMIN',NULL,'superadmin','2025-10-21 13:28:06','2025-10-21 13:28:06'),(4,4,'SUPERADMIN',NULL,'superadmin','2025-10-21 13:28:06','2025-10-21 13:28:06'),(5,5,'SUPERADMIN',NULL,'superadmin','2025-10-21 13:28:06','2025-10-21 13:28:06'),(6,6,'SUPERADMIN',NULL,'superadmin','2025-10-21 13:28:06','2025-10-21 13:28:06'),(7,7,'SUPERADMIN',NULL,'superadmin','2025-10-21 13:28:06','2025-10-21 13:28:06'),(8,8,'SUPERADMIN',NULL,'superadmin','2025-10-21 13:28:06','2025-10-21 13:28:06'),(9,9,'SUPERADMIN',NULL,'superadmin','2025-10-21 13:28:06','2025-10-21 13:28:06'),(10,10,'SUPERADMIN',NULL,'superadmin','2025-10-21 13:28:06','2025-10-21 13:28:06'),(11,11,'SUPERADMIN',NULL,'superadmin','2025-10-21 13:28:06','2025-10-21 13:28:06'),(12,12,'SUPERADMIN',NULL,'superadmin','2025-10-21 13:28:06','2025-10-21 13:28:06'),(13,13,'SUPERADMIN',NULL,'superadmin','2025-10-21 13:28:06','2025-10-21 13:28:06'),(14,14,'SUPERADMIN',NULL,'superadmin','2025-10-21 13:28:06','2025-10-21 13:28:06'),(15,15,'SUPERADMIN',NULL,'superadmin','2025-10-21 13:28:06','2025-10-21 13:28:06'),(16,16,'SUPERADMIN',NULL,'superadmin','2025-10-21 13:28:06','2025-10-21 13:28:06'),(17,17,'SUPERADMIN',NULL,'superadmin','2025-10-21 13:28:06','2025-10-21 13:28:06'),(18,18,'SUPERADMIN',NULL,'superadmin','2025-10-21 13:28:06','2025-10-21 13:28:06'),(19,19,'SUPERADMIN',NULL,'superadmin','2025-10-21 13:28:06','2025-10-21 13:28:06'),(20,20,'SUPERADMIN',NULL,'superadmin','2025-10-21 13:28:06','2025-10-21 13:28:06'),(21,21,'SUPERADMIN',NULL,'superadmin','2025-10-21 13:28:06','2025-10-21 13:28:06'),(22,22,'SUPERADMIN',NULL,'superadmin','2025-10-21 13:28:06','2025-10-21 13:28:06'),(23,23,'SUPERADMIN',NULL,'superadmin','2025-10-21 13:28:06','2025-10-21 13:28:06'),(25,25,'SUPERADMIN',NULL,'superadmin','2025-10-21 13:28:06','2025-10-21 13:28:06'),(27,27,'SUPERADMIN',NULL,'superadmin','2025-10-21 13:28:06','2025-10-21 13:28:06'),(28,28,'SUPERADMIN',NULL,'superadmin','2025-10-21 13:28:06','2025-10-21 13:28:06'),(29,29,'SUPERADMIN',NULL,'superadmin','2025-10-21 13:28:06','2025-10-21 13:28:06'),(30,30,'SUPERADMIN',NULL,'superadmin','2025-10-21 13:28:06','2025-10-21 13:28:06'),(31,31,'SUPERADMIN',NULL,'superadmin','2025-10-21 13:28:06','2025-10-21 13:28:06'),(32,32,'SUPERADMIN',NULL,'superadmin','2025-10-21 13:28:06','2025-10-21 13:28:06'),(33,33,'SUPERADMIN',NULL,'superadmin','2025-10-21 13:28:06','2025-10-21 13:28:06'),(34,34,'SUPERADMIN',NULL,'superadmin','2025-10-21 13:28:06','2025-10-21 13:28:06'),(35,35,'SUPERADMIN',NULL,'superadmin','2025-10-21 13:28:06','2025-10-21 13:28:06'),(36,36,'SUPERADMIN',NULL,'superadmin','2025-10-21 13:28:06','2025-10-21 13:28:06'),(37,37,'SUPERADMIN',NULL,'superadmin','2025-10-21 13:28:06','2025-10-21 13:28:06'),(42,42,'SUPERADMIN',NULL,'superadmin','2025-10-21 13:28:06','2025-10-21 13:28:06'),(43,43,'SUPERADMIN',NULL,'superadmin','2025-10-21 13:28:06','2025-10-21 13:28:06'),(44,1,NULL,1,'ADMIN','2025-10-21 13:28:06','2025-10-21 13:28:06'),(45,2,NULL,1,'ADMIN','2025-10-21 13:28:06','2025-10-21 13:28:06'),(46,21,NULL,1,'ADMIN','2025-10-21 13:28:06','2025-10-21 13:28:06'),(47,42,NULL,1,'ADMIN','2025-10-21 13:28:06','2025-10-21 13:28:06'),(48,43,NULL,1,'ADMIN','2025-10-21 13:28:06','2025-10-21 13:28:06'),(49,27,NULL,1,'ADMIN','2025-10-21 13:28:06','2025-10-21 13:28:06'),(50,28,NULL,1,'ADMIN','2025-10-21 13:28:06','2025-10-21 13:28:06'),(51,29,NULL,1,'ADMIN','2025-10-21 13:28:06','2025-10-21 13:28:06'),(52,30,NULL,1,'ADMIN','2025-10-21 13:28:06','2025-10-21 13:28:06'),(53,32,NULL,1,'ADMIN','2025-10-21 13:28:06','2025-10-21 13:28:06'),(54,33,NULL,1,'ADMIN','2025-10-21 13:28:06','2025-10-21 13:28:06'),(55,34,NULL,1,'ADMIN','2025-10-21 13:28:06','2025-10-21 13:28:06'),(56,36,NULL,1,'ADMIN','2025-10-21 13:28:06','2025-10-21 13:28:06'),(57,8,NULL,1,'ADMIN','2025-10-21 13:28:06','2025-10-21 13:28:06'),(58,9,NULL,1,'ADMIN','2025-10-21 13:28:06','2025-10-21 13:28:06'),(59,10,NULL,1,'ADMIN','2025-10-21 13:28:06','2025-10-21 13:28:06'),(60,11,NULL,1,'ADMIN','2025-10-21 13:28:06','2025-10-21 13:28:06'),(61,12,NULL,1,'ADMIN','2025-10-21 13:28:06','2025-10-21 13:28:06'),(62,13,NULL,1,'ADMIN','2025-10-21 13:28:06','2025-10-21 13:28:06'),(63,14,NULL,1,'ADMIN','2025-10-21 13:28:06','2025-10-21 13:28:06'),(64,15,NULL,1,'ADMIN','2025-10-21 13:28:06','2025-10-21 13:28:06'),(65,16,NULL,1,'ADMIN','2025-10-21 13:28:06','2025-10-21 13:28:06'),(66,17,NULL,1,'ADMIN','2025-10-21 13:28:06','2025-10-21 13:28:06'),(67,18,NULL,1,'ADMIN','2025-10-21 13:28:06','2025-10-21 13:28:06'),(68,19,NULL,1,'ADMIN','2025-10-21 13:28:06','2025-10-21 13:28:06'),(69,20,NULL,1,'ADMIN','2025-10-21 13:28:06','2025-10-21 13:28:06'),(71,25,NULL,1,'ADMIN','2025-10-21 13:28:06','2025-10-21 13:28:06'),(73,1,NULL,2,'CONTROL','2025-10-21 13:28:06','2025-10-21 13:28:06'),(74,2,NULL,2,'CONTROL','2025-10-21 13:28:06','2025-10-21 13:28:06'),(75,33,NULL,2,'CONTROL','2025-10-21 13:28:06','2025-10-21 13:28:06'),(77,25,NULL,2,'CONTROL','2025-10-21 13:28:06','2025-10-21 13:28:06'),(79,1,NULL,3,'USUARIO','2025-10-21 13:28:06','2025-10-21 13:28:06'),(80,2,NULL,3,'USUARIO','2025-10-21 13:28:06','2025-10-21 13:28:06'),(81,27,NULL,3,'USUARIO','2025-10-21 13:28:06','2025-10-21 13:28:06'),(82,4,NULL,3,'USUARIO','2025-10-21 13:28:06','2025-10-21 13:28:06'),(83,6,NULL,3,'USUARIO','2025-10-21 13:28:06','2025-10-21 13:28:06'),(84,7,NULL,3,'USUARIO','2025-10-21 13:28:06','2025-10-21 13:28:06'),(85,34,NULL,3,'USUARIO','2025-10-21 13:28:06','2025-10-21 13:28:06'),(86,8,NULL,3,'USUARIO','2025-10-21 13:28:06','2025-10-21 13:28:06'),(87,9,NULL,3,'USUARIO','2025-10-21 13:28:06','2025-10-21 13:28:06'),(88,14,NULL,3,'USUARIO','2025-10-21 13:28:06','2025-10-21 13:28:06'),(89,15,NULL,3,'USUARIO','2025-10-21 13:28:06','2025-10-21 13:28:06'),(90,16,NULL,3,'USUARIO','2025-10-21 13:28:06','2025-10-21 13:28:06'),(91,17,NULL,3,'USUARIO','2025-10-21 13:28:06','2025-10-21 13:28:06'),(92,18,NULL,3,'USUARIO','2025-10-21 13:28:06','2025-10-21 13:28:06'),(94,25,NULL,3,'USUARIO','2025-10-21 13:28:06','2025-10-21 13:28:06'),(96,1,NULL,4,'LECTOR','2025-10-21 13:28:06','2025-10-21 13:28:06'),(97,2,NULL,4,'LECTOR','2025-10-21 13:28:06','2025-10-21 13:28:06'),(98,4,NULL,4,'LECTOR','2025-10-21 13:28:06','2025-10-21 13:28:06'),(99,6,NULL,4,'LECTOR','2025-10-21 13:28:06','2025-10-21 13:28:06'),(100,7,NULL,4,'LECTOR','2025-10-21 13:28:06','2025-10-21 13:28:06'),(101,8,NULL,4,'LECTOR','2025-10-21 13:28:06','2025-10-21 13:28:06'),(102,9,NULL,4,'LECTOR','2025-10-21 13:28:06','2025-10-21 13:28:06'),(103,14,NULL,4,'LECTOR','2025-10-21 13:28:06','2025-10-21 13:28:06'),(104,15,NULL,4,'LECTOR','2025-10-21 13:28:06','2025-10-21 13:28:06'),(105,16,NULL,4,'LECTOR','2025-10-21 13:28:06','2025-10-21 13:28:06'),(106,17,NULL,4,'LECTOR','2025-10-21 13:28:06','2025-10-21 13:28:06'),(107,18,NULL,4,'LECTOR','2025-10-21 13:28:06','2025-10-21 13:28:06'),(109,25,NULL,4,'LECTOR','2025-10-21 13:28:06','2025-10-21 13:28:06'),(116,26,'SUPERADMIN',NULL,'SUPERADMIN','2025-10-21 14:22:17','2025-10-21 14:22:17'),(117,26,NULL,1,'ADMIN','2025-10-21 14:23:01','2025-10-21 14:23:01'),(118,26,NULL,2,'CONTROL','2025-10-21 14:23:03','2025-10-21 14:23:03'),(119,26,NULL,3,'USUARIO','2025-10-21 14:23:04','2025-10-21 14:23:04'),(120,26,NULL,4,'LECTOR','2025-10-21 14:23:05','2025-10-21 14:23:05'),(121,40,'SUPERADMIN',NULL,'SUPERADMIN','2025-10-21 14:29:43','2025-10-21 14:29:43');
/*!40000 ALTER TABLE `page_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pages`
--

DROP TABLE IF EXISTS `pages`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pages` (
  `id` int NOT NULL AUTO_INCREMENT,
  `route` varchar(200) NOT NULL,
  `name` varchar(200) NOT NULL,
  `description` text,
  `category_id` int NOT NULL,
  `template_path` varchar(300) DEFAULT NULL,
  `active` tinyint(1) NOT NULL,
  `display_order` int NOT NULL,
  `icon` varchar(100) NOT NULL,
  `is_visible` tinyint(1) NOT NULL,
  `parent_page_id` int DEFAULT NULL,
  `menu_group` varchar(100) DEFAULT NULL,
  `external_url` varchar(500) DEFAULT NULL,
  `target_blAúnk` tinyint(1) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `route` (`route`),
  KEY `category_id` (`category_id`),
  KEY `parent_page_id` (`parent_page_id`),
  CONSTRAINT `pages_ibfk_1` FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`),
  CONSTRAINT `pages_ibfk_2` FOREIGN KEY (`parent_page_id`) REFERENCES `pages` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=44 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pages`
--

LOCK TABLES `pages` WRITE;
/*!40000 ALTER TABLE `pages` DISABLE KEYS */;
INSERT INTO `pages` VALUES (1,'/','Inicio','P├ígina principal del sistema',1,NULL,1,1,'fas fa-home',1,NULL,NULL,NULL,0,'2025-10-21 13:28:06','2025-10-21 13:28:06'),(2,'/dashboard','Dashboard','PAúnel de control y estad├¡sticas',1,NULL,1,2,'fas fa-tachometer-alt',1,NULL,NULL,NULL,0,'2025-10-21 13:28:06','2025-10-21 13:28:06'),(3,'/health','Estado del Sistema','Estado y salud del sistema',1,NULL,1,3,'fas fa-heartbeat',0,NULL,NULL,NULL,0,'2025-10-21 13:28:06','2025-10-21 13:28:06'),(4,'/projects','Lista de Proyectos','Ver todos los proyectos',2,NULL,1,1,'fas fa-list',1,NULL,NULL,NULL,0,'2025-10-21 13:28:06','2025-10-21 13:28:06'),(5,'/projects/create','Crear Proyecto','Crear nuevo proyecto',2,NULL,1,2,'fas fa-plus',1,NULL,NULL,NULL,0,'2025-10-21 13:28:06','2025-10-21 13:28:06'),(6,'/actividades','Actividades','Gesti├│n de actividades de proyecto',2,NULL,1,3,'fas fa-tasks',1,NULL,NULL,NULL,0,'2025-10-21 13:28:06','2025-10-21 13:28:06'),(7,'/gAúntt','Diagrama de GAúntt','Visualizaci├│n de cronogramas',2,NULL,1,4,'fas fa-chart-line',1,NULL,NULL,NULL,0,'2025-10-21 13:28:06','2025-10-21 13:28:06'),(8,'/estados','Estados','Gesti├│n de estados de proyecto',4,NULL,1,1,'fas fa-flag',1,NULL,NULL,NULL,0,'2025-10-21 13:28:06','2025-10-21 13:28:06'),(9,'/prioridades','Prioridades','Gesti├│n de prioridades',4,NULL,1,2,'fas fa-exclamation-triAúngle',1,NULL,NULL,NULL,0,'2025-10-21 13:28:06','2025-10-21 13:28:06'),(10,'/fases','Fases','Gesti├│n de fases de proyecto',4,NULL,1,3,'fas fa-layer-group',1,NULL,NULL,NULL,0,'2025-10-21 13:28:06','2025-10-21 13:28:06'),(11,'/tipologias','Tipolog├¡as','Gesti├│n de tipolog├¡as',4,NULL,1,4,'fas fa-tags',1,NULL,NULL,NULL,0,'2025-10-21 13:28:06','2025-10-21 13:28:06'),(12,'/finAúnciamientos','FinAúnciamientos','Gesti├│n de tipos de finAúnciamiento',4,NULL,1,5,'fas fa-money-bill-wave',1,NULL,NULL,NULL,0,'2025-10-21 13:28:06','2025-10-21 13:28:06'),(13,'/tipoproyectos','Tipos de Proyecto','Gesti├│n de tipos de proyecto',4,NULL,1,6,'fas fa-project-diagram',1,NULL,NULL,NULL,0,'2025-10-21 13:28:06','2025-10-21 13:28:06'),(14,'/sectores','Sectores','Gesti├│n de sectores',4,NULL,1,7,'fas fa-building',1,NULL,NULL,NULL,0,'2025-10-21 13:28:06','2025-10-21 13:28:06'),(15,'/tiposrecintos','Tipos de Recinto','Gesti├│n de tipos de recinto',4,NULL,1,8,'fas fa-home',1,NULL,NULL,NULL,0,'2025-10-21 13:28:06','2025-10-21 13:28:06'),(16,'/recintos','Recintos','Gesti├│n de recintos',4,NULL,1,9,'fas fa-map-marker-alt',1,NULL,NULL,NULL,0,'2025-10-21 13:28:06','2025-10-21 13:28:06'),(17,'/equipos','Equipos','Gesti├│n de equipos de trabajo',4,NULL,1,10,'fas fa-users-cog',1,NULL,NULL,NULL,0,'2025-10-21 13:28:06','2025-10-21 13:28:06'),(18,'/especialidades','Especialidades','Gesti├│n de especialidades',4,NULL,1,11,'fas fa-graduation-cap',1,NULL,NULL,NULL,0,'2025-10-21 13:28:06','2025-10-21 13:28:06'),(19,'/areas','├Áreas','Gesti├│n de ├íreas orgAúnizacionales',4,NULL,1,12,'fas fa-sitemap',1,NULL,NULL,NULL,0,'2025-10-21 13:28:06','2025-10-21 13:28:06'),(20,'/grupos','Grupos','Gesti├│n de grupos de trabajo',4,NULL,1,13,'fas fa-layer-group',1,NULL,NULL,NULL,0,'2025-10-21 13:28:06','2025-10-21 13:28:06'),(21,'/trabajadores','Trabajadores','Gesti├│n de usuarios del sistema',3,NULL,1,1,'fas fa-users',1,NULL,NULL,NULL,0,'2025-10-21 13:28:06','2025-10-21 13:28:06'),(22,'/auth/login','Iniciar Sesi├│n','P├ígina de inicio de sesi├│n',3,NULL,1,2,'fas fa-sign-in-alt',0,NULL,NULL,NULL,0,'2025-10-21 13:28:06','2025-10-21 13:28:06'),(23,'/auth/logout','Cerrar Sesi├│n','Cerrar sesi├│n del usuario',3,NULL,1,3,'fas fa-sign-out-alt',0,NULL,NULL,NULL,0,'2025-10-21 13:28:06','2025-10-21 13:28:06'),(25,'/profile/edit','Editar Mi Perfil','Editar informaci├│n personal del perfil',3,NULL,1,5,'fas fa-user-edit',0,NULL,NULL,NULL,0,'2025-10-21 13:28:06','2025-10-21 13:28:06'),(26,'/auth/mi-perfil','Mi Perfil','P├ígina Mi Perfil',3,'',1,6,'fas fa-id-card',1,NULL,NULL,NULL,0,'2025-10-21 13:28:06','2025-10-21 14:22:17'),(27,'/requerimientos','Requerimientos','Gesti├│n de requerimientos',2,NULL,1,1,'fas fa-clipboard-list',1,NULL,NULL,NULL,0,'2025-10-21 13:28:06','2025-10-21 13:28:06'),(28,'/requerimientos_aceptar','Requerimientos Aceptar','Aceptar requerimientos',2,NULL,1,2,'fas fa-check-circle',1,NULL,NULL,NULL,0,'2025-10-21 13:28:06','2025-10-21 13:28:06'),(29,'/requerimientos_completar','Requerimientos Completar','Completar requerimientos',2,NULL,1,3,'fas fa-clipboard-check',1,NULL,NULL,NULL,0,'2025-10-21 13:28:06','2025-10-21 13:28:06'),(30,'/proyectos_aceptar','Proyecto Aceptar','Aceptar proyectos',2,NULL,1,4,'fas fa-thumbs-up',1,NULL,NULL,NULL,0,'2025-10-21 13:28:06','2025-10-21 13:28:06'),(31,'/proyectos_completar','Proyectos Completar OLD','Completar proyectos (versi├│n Aúnterior)',2,NULL,1,5,'fas fa-archive',1,NULL,NULL,NULL,0,'2025-10-21 13:28:06','2025-10-21 13:28:06'),(32,'/proyecto-llenar','Proyectos Completar','Completar informaci├│n de proyectos',2,NULL,1,6,'fas fa-edit',1,NULL,NULL,NULL,0,'2025-10-21 13:28:06','2025-10-21 13:28:06'),(33,'/control_actividades','Controles','Control de actividades',2,NULL,1,7,'fas fa-clipboard-list',1,NULL,NULL,NULL,0,'2025-10-21 13:28:06','2025-10-21 13:28:06'),(34,'/avAúnce-actividades','AvAúnce Actividades','Seguimiento de avAúnce de actividades',2,NULL,1,8,'fas fa-chart-line',1,NULL,NULL,NULL,0,'2025-10-21 13:28:06','2025-10-21 13:28:06'),(35,'/avAúnce-actividades-all','AvAúnce Actividades - Todos','Seguimiento de avAúnce de actividades (todos los proyectos)',2,NULL,1,9,'fas fa-chart-area',1,NULL,NULL,NULL,0,'2025-10-21 13:28:06','2025-10-21 13:28:06'),(36,'/historial-avAúnces','Historial AvAúnces','Historial de avAúnces registrados',2,NULL,1,10,'fas fa-history',1,NULL,NULL,NULL,0,'2025-10-21 13:28:06','2025-10-21 13:28:06'),(37,'/permissions/','Gesti├│n de Permisos','Administrar permisos de usuarios',5,NULL,1,1,'fas fa-shield-alt',1,NULL,NULL,NULL,0,'2025-10-21 13:28:06','2025-10-21 13:28:06'),(38,'/admin/config','Configuraci├│n Sistema','Configurar par├ímetros del sistema',5,NULL,1,2,'fas fa-cogs',1,NULL,NULL,NULL,0,'2025-10-21 13:28:06','2025-10-21 13:28:06'),(39,'/admin/logs','Logs del Sistema','Ver logs y auditor├¡a',5,NULL,1,3,'fas fa-file-alt',1,NULL,NULL,NULL,0,'2025-10-21 13:28:06','2025-10-21 13:28:06'),(40,'/admin/backup','Respaldos','Gesti├│n de respaldos',5,NULL,1,4,'fas fa-database',1,NULL,NULL,NULL,0,'2025-10-21 13:28:06','2025-10-21 13:28:06'),(41,'/admin/maintenAúnce','MAúntenimiento','Tareas de mAúntenimiento del sistema',5,NULL,1,5,'fas fa-tools',1,NULL,NULL,NULL,0,'2025-10-21 13:28:06','2025-10-21 13:28:06'),(42,'/gestion-administradores','Gesti├│n de Administradores','Asignar recintos espec├¡ficos a cada administrador',5,NULL,1,6,'fas fa-users-cog',1,NULL,NULL,NULL,0,'2025-10-21 13:28:06','2025-10-21 13:28:06'),(43,'/gestion-usuarios','Gesti├│n de Usuarios por Recinto','Asignar recintos adicionales a trabajadores de mis recintos',5,NULL,1,7,'fas fa-users',1,NULL,NULL,NULL,0,'2025-10-21 13:28:06','2025-10-21 13:28:06');
/*!40000 ALTER TABLE `pages` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `prioridad`
--

DROP TABLE IF EXISTS `prioridad`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `prioridad` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `descripcion` text,
  `urgencia` tinyint(1) NOT NULL,
  `importAúncia` tinyint(1) NOT NULL,
  `cuadrAúnte` int NOT NULL,
  `color` varchar(7) NOT NULL,
  `orden` int NOT NULL,
  `activo` tinyint(1) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_prioridad_nombre` (`nombre`),
  KEY `idx_prioridad_orden` (`orden`),
  KEY `idx_prioridad_cuadrAúnte` (`cuadrAúnte`),
  CONSTRAINT `ck_prioridad_cuadrAúnte` CHECK (((`cuadrAúnte` >= 1) Aúnd (`cuadrAúnte` <= 4))),
  CONSTRAINT `ck_prioridad_orden` CHECK ((`orden` > 0))
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `prioridad`
--

LOCK TABLES `prioridad` WRITE;
/*!40000 ALTER TABLE `prioridad` DISABLE KEYS */;
INSERT INTO `prioridad` VALUES (1,'Urgente e ImportAúnte','Crisis, emergencias, problemas urgentes con fechas l├â┬¡mite',1,1,1,'#dc3545',1,1,'2025-10-21 13:28:05','2025-10-21 13:28:05'),(2,'ImportAúnte, No Urgente','PlAúnificaci├â┬│n, prevenci├â┬│n, desarrollo personal, nuevas oportunidades',0,1,2,'#ffc107',2,1,'2025-10-21 13:28:05','2025-10-21 13:28:05'),(3,'Urgente, No ImportAúnte','Interrupciones, algunas llamadas, correos, reuniones',1,0,3,'#fd7e14',3,1,'2025-10-21 13:28:05','2025-10-21 13:28:05'),(4,'No Urgente, No ImportAúnte','Trivialidades, p├â┬®rdidas de tiempo, actividades placenteras',0,0,4,'#6c757d',4,1,'2025-10-21 13:28:05','2025-10-21 13:28:05');
/*!40000 ALTER TABLE `prioridad` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `recinto`
--

DROP TABLE IF EXISTS `recinto`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `recinto` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(255) NOT NULL,
  `descripcion` text,
  `id_tiporecinto` int NOT NULL,
  `activo` tinyint(1) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_recinto_nombre_tiporecinto` (`nombre`,`id_tiporecinto`),
  KEY `idx_recinto_tiporecinto` (`id_tiporecinto`),
  KEY `idx_recinto_activo` (`activo`),
  CONSTRAINT `recinto_ibfk_1` FOREIGN KEY (`id_tiporecinto`) REFERENCES `tiporecinto` (`id`) ON DELETE RESTRICT
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `recinto`
--

LOCK TABLES `recinto` WRITE;
/*!40000 ALTER TABLE `recinto` DISABLE KEYS */;
INSERT INTO `recinto` VALUES (1,'CESFAM La Tortuga','Centro de Salud Familiar La Tortuga',1,1,'2025-10-21 13:28:06','2025-10-21 13:28:06'),(2,'CECOSF El Boro','Centro Comunitario El Boro',2,1,'2025-10-21 13:28:06','2025-10-21 13:28:06'),(3,'SAPU Dr. H├â┬®ctor Reyno','Servicio de Atenci├â┬│n Primaria',3,1,'2025-10-21 13:28:06','2025-10-21 13:28:06'),(4,'Oficinas DEPSA','Oficinas del Departamento de Salud',5,1,'2025-10-21 13:28:06','2025-10-21 13:28:06');
/*!40000 ALTER TABLE `recinto` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `recursos_trabajador`
--

DROP TABLE IF EXISTS `recursos_trabajador`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `recursos_trabajador` (
  `id` int NOT NULL AUTO_INCREMENT,
  `requerimiento_id` int NOT NULL,
  `actividad_gAúntt_id` int NOT NULL,
  `edt` varchar(50) NOT NULL,
  `fecha_asignacion` datetime DEFAULT NULL,
  `recurso` varchar(255) NOT NULL,
  `id_trabajador` int NOT NULL,
  `porcentaje_asignacion` float DEFAULT NULL,
  `activo` tinyint(1) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_recurso_trabajador_edt` (`edt`),
  KEY `idx_recurso_trabajador_trabajador` (`id_trabajador`),
  KEY `idx_recurso_trabajador_unique` (`actividad_gAúntt_id`,`id_trabajador`),
  KEY `idx_recurso_trabajador_requerimiento` (`requerimiento_id`),
  CONSTRAINT `recursos_trabajador_ibfk_1` FOREIGN KEY (`requerimiento_id`) REFERENCES `requerimiento` (`id`) ON DELETE CASCADE,
  CONSTRAINT `recursos_trabajador_ibfk_2` FOREIGN KEY (`actividad_gAúntt_id`) REFERENCES `actividades_gAúntt` (`id`) ON DELETE CASCADE,
  CONSTRAINT `recursos_trabajador_ibfk_3` FOREIGN KEY (`id_trabajador`) REFERENCES `trabajador` (`id`) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `recursos_trabajador`
--

LOCK TABLES `recursos_trabajador` WRITE;
/*!40000 ALTER TABLE `recursos_trabajador` DISABLE KEYS */;
/*!40000 ALTER TABLE `recursos_trabajador` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `requerimiento`
--

DROP TABLE IF EXISTS `requerimiento`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `requerimiento` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(255) NOT NULL,
  `fecha` datetime NOT NULL,
  `descripcion` text,
  `observacion` text,
  `id_sector` int NOT NULL,
  `id_tiporecinto` int NOT NULL,
  `id_recinto` int NOT NULL,
  `id_estado` int NOT NULL,
  `id_prioridad` int DEFAULT NULL,
  `id_grupo` int DEFAULT NULL,
  `id_area` int DEFAULT NULL,
  `fecha_aceptacion` datetime DEFAULT NULL,
  `id_tipologia` int DEFAULT NULL,
  `id_finAúnciamiento` int DEFAULT NULL,
  `id_tipoproyecto` int DEFAULT NULL,
  `proyecto` varchar(50) DEFAULT NULL,
  `activo` tinyint(1) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `id_tiporecinto` (`id_tiporecinto`),
  KEY `id_recinto` (`id_recinto`),
  KEY `id_grupo` (`id_grupo`),
  KEY `id_area` (`id_area`),
  KEY `id_tipologia` (`id_tipologia`),
  KEY `id_finAúnciamiento` (`id_finAúnciamiento`),
  KEY `id_tipoproyecto` (`id_tipoproyecto`),
  KEY `idx_requerimiento_sector` (`id_sector`),
  KEY `idx_requerimiento_fecha` (`fecha`),
  KEY `idx_requerimiento_estado` (`id_estado`),
  KEY `idx_requerimiento_prioridad` (`id_prioridad`),
  CONSTRAINT `requerimiento_ibfk_1` FOREIGN KEY (`id_sector`) REFERENCES `sector` (`id`) ON DELETE RESTRICT,
  CONSTRAINT `requerimiento_ibfk_10` FOREIGN KEY (`id_tipoproyecto`) REFERENCES `tipoproyecto` (`id`) ON DELETE RESTRICT,
  CONSTRAINT `requerimiento_ibfk_2` FOREIGN KEY (`id_tiporecinto`) REFERENCES `tiporecinto` (`id`) ON DELETE RESTRICT,
  CONSTRAINT `requerimiento_ibfk_3` FOREIGN KEY (`id_recinto`) REFERENCES `recinto` (`id`) ON DELETE RESTRICT,
  CONSTRAINT `requerimiento_ibfk_4` FOREIGN KEY (`id_estado`) REFERENCES `estado` (`id`) ON DELETE RESTRICT,
  CONSTRAINT `requerimiento_ibfk_5` FOREIGN KEY (`id_prioridad`) REFERENCES `prioridad` (`id`) ON DELETE RESTRICT,
  CONSTRAINT `requerimiento_ibfk_6` FOREIGN KEY (`id_grupo`) REFERENCES `grupo` (`id`) ON DELETE RESTRICT,
  CONSTRAINT `requerimiento_ibfk_7` FOREIGN KEY (`id_area`) REFERENCES `area` (`id`) ON DELETE RESTRICT,
  CONSTRAINT `requerimiento_ibfk_8` FOREIGN KEY (`id_tipologia`) REFERENCES `tipologia` (`id`) ON DELETE RESTRICT,
  CONSTRAINT `requerimiento_ibfk_9` FOREIGN KEY (`id_finAúnciamiento`) REFERENCES `finAúnciamiento` (`id`) ON DELETE RESTRICT
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `requerimiento`
--

LOCK TABLES `requerimiento` WRITE;
/*!40000 ALTER TABLE `requerimiento` DISABLE KEYS */;
INSERT INTO `requerimiento` VALUES (1,'PROYECTO PRUEBA 1','2025-01-15 00:00:00','Proyecto de prueba para el sistema','Solo prueba 1',1,1,1,1,1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1,'2025-10-21 13:28:06','2025-10-21 13:28:06'),(2,'PROYECTO PRUEBA 2','2025-01-16 00:00:00','Segundo proyecto de prueba','Solo prueba 2',2,2,2,1,2,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1,'2025-10-21 13:28:06','2025-10-21 13:28:06'),(3,'PROYECTO EN DESARROLLO','2025-01-14 00:00:00','Proyecto que ya fue aceptado y est├í en desarrollo','Aceptado para desarrollo',1,1,1,2,1,NULL,NULL,'2025-01-15 00:00:00',2,2,2,NULL,1,'2025-10-21 13:28:06','2025-10-21 13:28:06');
/*!40000 ALTER TABLE `requerimiento` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `requerimiento_trabajador_especialidad`
--

DROP TABLE IF EXISTS `requerimiento_trabajador_especialidad`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `requerimiento_trabajador_especialidad` (
  `requerimiento_id` int NOT NULL,
  `trabajador_id` int NOT NULL,
  `especialidad_id` int NOT NULL,
  `fecha_asignacion` datetime NOT NULL,
  `activo` tinyint(1) NOT NULL,
  PRIMARY KEY (`requerimiento_id`,`trabajador_id`,`especialidad_id`),
  KEY `trabajador_id` (`trabajador_id`),
  KEY `especialidad_id` (`especialidad_id`),
  CONSTRAINT `requerimiento_trabajador_especialidad_ibfk_1` FOREIGN KEY (`requerimiento_id`) REFERENCES `requerimiento` (`id`) ON DELETE CASCADE,
  CONSTRAINT `requerimiento_trabajador_especialidad_ibfk_2` FOREIGN KEY (`trabajador_id`) REFERENCES `trabajador` (`id`) ON DELETE CASCADE,
  CONSTRAINT `requerimiento_trabajador_especialidad_ibfk_3` FOREIGN KEY (`especialidad_id`) REFERENCES `especialidad` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `requerimiento_trabajador_especialidad`
--

LOCK TABLES `requerimiento_trabajador_especialidad` WRITE;
/*!40000 ALTER TABLE `requerimiento_trabajador_especialidad` DISABLE KEYS */;
/*!40000 ALTER TABLE `requerimiento_trabajador_especialidad` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sector`
--

DROP TABLE IF EXISTS `sector`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sector` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(255) NOT NULL,
  `descripcion` text,
  `activo` tinyint(1) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_sector_nombre` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sector`
--

LOCK TABLES `sector` WRITE;
/*!40000 ALTER TABLE `sector` DISABLE KEYS */;
INSERT INTO `sector` VALUES (1,'MUNICIPAL','',1,'2025-10-21 13:28:06','2025-10-21 13:28:06'),(2,'SALUD','',1,'2025-10-21 13:28:06','2025-10-21 13:28:06'),(3,'CEMENTERIO','',1,'2025-10-21 13:28:06','2025-10-21 13:28:06'),(4,'EDUCACION','',1,'2025-10-21 13:28:06','2025-10-21 13:28:06'),(5,'OTRO','',1,'2025-10-21 13:28:06','2025-10-21 13:28:06');
/*!40000 ALTER TABLE `sector` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tipologia`
--

DROP TABLE IF EXISTS `tipologia`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tipologia` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(255) NOT NULL,
  `nombrecorto` varchar(50) DEFAULT NULL,
  `descripcion` text,
  `id_fase` int NOT NULL,
  `activo` tinyint(1) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_tipologia_nombre_fase` (`nombre`,`id_fase`),
  KEY `idx_tipologia_fase` (`id_fase`),
  KEY `idx_tipologia_activo` (`activo`),
  CONSTRAINT `tipologia_ibfk_1` FOREIGN KEY (`id_fase`) REFERENCES `fase` (`id`) ON DELETE RESTRICT
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tipologia`
--

LOCK TABLES `tipologia` WRITE;
/*!40000 ALTER TABLE `tipologia` DISABLE KEYS */;
INSERT INTO `tipologia` VALUES (1,'Por definir','Por definir','',1,1,'2025-10-21 13:28:05','2025-10-21 13:28:05'),(2,'Estudios B├ísicos - PreInv','EB-PreInv','',2,1,'2025-10-21 13:28:05','2025-10-21 13:28:05'),(3,'Programa de Inversi├│n - PreInv','Prog_Inv-PreInv','',2,1,'2025-10-21 13:28:05','2025-10-21 13:28:05'),(4,'Proyecto de Inversi├│n - PreInv','Proy_Inv-PreInv','',2,1,'2025-10-21 13:28:05','2025-10-21 13:28:05'),(5,'Estudios B├ísicos - Inv','EB-Inv','',3,1,'2025-10-21 13:28:05','2025-10-21 13:28:05'),(6,'Programa de Inversi├│n - Inv','Prog_Inv-Inv','',3,1,'2025-10-21 13:28:05','2025-10-21 13:28:05'),(7,'Proyecto de Inversi├│n - Inv','Proy_Inv-Inv','',3,1,'2025-10-21 13:28:05','2025-10-21 13:28:05'),(8,'Proyecto de Inversi├│n - Op','Proy_Inv-Op','',4,1,'2025-10-21 13:28:05','2025-10-21 13:28:05');
/*!40000 ALTER TABLE `tipologia` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tipoproyecto`
--

DROP TABLE IF EXISTS `tipoproyecto`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tipoproyecto` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(255) NOT NULL,
  `nombrecorto` varchar(50) DEFAULT NULL,
  `descripcion` text,
  `activo` tinyint(1) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_tipoproyecto_nombre` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tipoproyecto`
--

LOCK TABLES `tipoproyecto` WRITE;
/*!40000 ALTER TABLE `tipoproyecto` DISABLE KEYS */;
INSERT INTO `tipoproyecto` VALUES (1,'Por Definir','Por Definir','Fondos por definir',1,'2025-10-21 13:28:05','2025-10-21 13:28:05'),(2,'PMI','PMI','Fondo para Proyectos de Mejoramiento Integral',1,'2025-10-21 13:28:05','2025-10-21 13:28:05'),(3,'AGL','AGL','Fondo de Ampliaci├â┬│n y Generaci├â┬│n de Lugares',1,'2025-10-21 13:28:05','2025-10-21 13:28:05'),(4,'FNDR - Circular 33','FNDR-C33','Fondo Nacional de Desarrollo Regional - Circular 33',1,'2025-10-21 13:28:05','2025-10-21 13:28:05'),(5,'FNDR - Circular 31','FNDR-C31','Fondo Nacional de Desarrollo Regional - Circular 31',1,'2025-10-21 13:28:05','2025-10-21 13:28:05');
/*!40000 ALTER TABLE `tipoproyecto` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tiporecinto`
--

DROP TABLE IF EXISTS `tiporecinto`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tiporecinto` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(255) NOT NULL,
  `descripcion` text,
  `id_sector` int NOT NULL,
  `activo` tinyint(1) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_tiporecinto_nombre_sector` (`nombre`,`id_sector`),
  KEY `idx_tiporecinto_sector` (`id_sector`),
  KEY `idx_tiporecinto_activo` (`activo`),
  CONSTRAINT `tiporecinto_ibfk_1` FOREIGN KEY (`id_sector`) REFERENCES `sector` (`id`) ON DELETE RESTRICT
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tiporecinto`
--

LOCK TABLES `tiporecinto` WRITE;
/*!40000 ALTER TABLE `tiporecinto` DISABLE KEYS */;
INSERT INTO `tiporecinto` VALUES (1,'CESFAM','Centro de Salud Familiar',2,1,'2025-10-21 13:28:06','2025-10-21 13:28:06'),(2,'CECOSF','Centro Comunitario de Salud Familiar',2,1,'2025-10-21 13:28:06','2025-10-21 13:28:06'),(3,'SAPU','Servicio de Atenci├â┬│n Primaria de Urgencia',2,1,'2025-10-21 13:28:06','2025-10-21 13:28:06'),(4,'SAR','Servicio de Alta Resoluci├â┬│n',2,1,'2025-10-21 13:28:06','2025-10-21 13:28:06'),(5,'ED. CONSISTORIAL','Edificio Consistorial',1,1,'2025-10-21 13:28:06','2025-10-21 13:28:06');
/*!40000 ALTER TABLE `tiporecinto` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `trabajador`
--

DROP TABLE IF EXISTS `trabajador`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `trabajador` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(255) NOT NULL,
  `rut` varchar(12) DEFAULT NULL,
  `profesion` varchar(255) DEFAULT NULL,
  `nombrecorto` varchar(50) DEFAULT NULL,
  `password_hash` varchar(255) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `telefono` varchar(20) DEFAULT NULL,
  `activo` tinyint(1) NOT NULL,
  `rol` enum('SUPERADMIN') DEFAULT NULL,
  `custom_role_id` int DEFAULT NULL,
  `ultimo_acceso` datetime DEFAULT NULL,
  `intentos_fallidos` int NOT NULL,
  `bloqueado_hasta` datetime DEFAULT NULL,
  `area_id` int DEFAULT NULL,
  `sector_id` int DEFAULT NULL,
  `recinto_id` int DEFAULT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_trabajador_nombre` (`nombre`),
  UNIQUE KEY `uq_trabajador_email` (`email`),
  UNIQUE KEY `uq_trabajador_rut` (`rut`),
  UNIQUE KEY `email` (`email`),
  KEY `custom_role_id` (`custom_role_id`),
  KEY `sector_id` (`sector_id`),
  KEY `recinto_id` (`recinto_id`),
  KEY `idx_trabajador_email` (`email`),
  KEY `idx_trabajador_profesion` (`profesion`),
  KEY `idx_trabajador_rut` (`rut`),
  KEY `idx_trabajador_area` (`area_id`),
  KEY `idx_trabajador_rol` (`rol`),
  KEY `idx_trabajador_activo` (`activo`),
  CONSTRAINT `trabajador_ibfk_1` FOREIGN KEY (`custom_role_id`) REFERENCES `custom_roles` (`id`),
  CONSTRAINT `trabajador_ibfk_2` FOREIGN KEY (`area_id`) REFERENCES `area` (`id`) ON DELETE SET NULL,
  CONSTRAINT `trabajador_ibfk_3` FOREIGN KEY (`sector_id`) REFERENCES `sector` (`id`) ON DELETE SET NULL,
  CONSTRAINT `trabajador_ibfk_4` FOREIGN KEY (`recinto_id`) REFERENCES `recinto` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `trabajador`
--

LOCK TABLES `trabajador` WRITE;
/*!40000 ALTER TABLE `trabajador` DISABLE KEYS */;
INSERT INTO `trabajador` VALUES (1,'Admin Sistema','11111111-1','Administrador Sistema','admin','$argon2id$v=19$m=65536,t=3,p=4$93eMYISc7e9wqinujP2iZg$0+P4tLeZdLy91eQToLyJR/VabDapUQ+R2C8rAiUfuQ4','admin@sistema.local',NULL,1,'SUPERADMIN',NULL,'2025-11-03 14:27:38',1,NULL,NULL,NULL,NULL,'2025-10-21 13:28:05','2025-11-03 14:27:38'),(2,'Administrador L1','22222222-2','Administrador','admingen','$argon2id$v=19$m=65536,t=3,p=4$Lqjhq3jsIYgDPWDob8ryBg$Jo0/A0RYNyyEIRW+tAGP0esF6zufJhS0AHLNwS2U86g','administrador@sistema.local',NULL,1,NULL,1,NULL,0,NULL,NULL,NULL,NULL,'2025-10-21 13:28:05','2025-10-21 13:28:05'),(3,'Control de Proyectos','33333333-3','Jefe de Control','control','$argon2id$v=19$m=65536,t=3,p=4$qLkI5/E/qHVBTQGH4cpGyQ$qMEO2v1VJRslYZDi+UztgWeRxZ6ottMc+aTACmPUQsc','control@sistema.local',NULL,1,NULL,2,NULL,0,NULL,NULL,NULL,NULL,'2025-10-21 13:28:06','2025-10-21 13:28:06'),(4,'Usuario Operativo','44444444-4','Especialista','usuario','$argon2id$v=19$m=65536,t=3,p=4$81md+5e5o9p1hLp1GhdXpw$M+b036IsL6WRR9Tnw1PedKopb72wFXX/0Q1aw5GfLFE','usuario@sistema.local',NULL,1,NULL,3,NULL,0,NULL,NULL,NULL,NULL,'2025-10-21 13:28:06','2025-10-21 13:28:06'),(5,'SolicitAúnte Externo','55555555-5','SolicitAúnte','solicit','$argon2id$v=19$m=65536,t=3,p=4$Z5S8NUr3tfszOCZdyp7z2Q$MljqFvwN31JzK3IWN7+EaorXv8dmAS94qy/S6ErwPTM','solicitAúnte@sistema.local',NULL,1,NULL,1,NULL,0,NULL,NULL,NULL,NULL,'2025-10-21 13:28:06','2025-10-21 13:28:06'),(6,'Lector del Sistema','66666666-6','Consultor','lector','$argon2id$v=19$m=65536,t=3,p=4$3ZJ+mq6JiLS3nVpoVS1CaA$ka2oQ+Pb/v4F3p3hfJy3LQtcWjL352UbNtiPZeKSKDA','lector@sistema.local',NULL,1,NULL,4,NULL,0,NULL,NULL,NULL,NULL,'2025-10-21 13:28:06','2025-10-21 13:28:06');
/*!40000 ALTER TABLE `trabajador` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `trabajador_areas`
--

DROP TABLE IF EXISTS `trabajador_areas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `trabajador_areas` (
  `trabajador_id` int NOT NULL,
  `area_id` int NOT NULL,
  `fecha_asignacion` datetime NOT NULL,
  `activo` tinyint(1) NOT NULL,
  PRIMARY KEY (`trabajador_id`,`area_id`),
  KEY `idx_trabajador_areas_area` (`area_id`),
  KEY `idx_trabajador_areas_activo` (`activo`),
  KEY `idx_trabajador_areas_trabajador` (`trabajador_id`),
  CONSTRAINT `trabajador_areas_ibfk_1` FOREIGN KEY (`trabajador_id`) REFERENCES `trabajador` (`id`) ON DELETE CASCADE,
  CONSTRAINT `trabajador_areas_ibfk_2` FOREIGN KEY (`area_id`) REFERENCES `area` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `trabajador_areas`
--

LOCK TABLES `trabajador_areas` WRITE;
/*!40000 ALTER TABLE `trabajador_areas` DISABLE KEYS */;
/*!40000 ALTER TABLE `trabajador_areas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `trabajador_recinto`
--

DROP TABLE IF EXISTS `trabajador_recinto`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `trabajador_recinto` (
  `id` int NOT NULL AUTO_INCREMENT,
  `trabajador_id` int NOT NULL,
  `recinto_id` int NOT NULL,
  `activo` tinyint(1) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `_trabajador_recinto_uc` (`trabajador_id`,`recinto_id`),
  KEY `recinto_id` (`recinto_id`),
  CONSTRAINT `trabajador_recinto_ibfk_1` FOREIGN KEY (`trabajador_id`) REFERENCES `trabajador` (`id`),
  CONSTRAINT `trabajador_recinto_ibfk_2` FOREIGN KEY (`recinto_id`) REFERENCES `recinto` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `trabajador_recinto`
--

LOCK TABLES `trabajador_recinto` WRITE;
/*!40000 ALTER TABLE `trabajador_recinto` DISABLE KEYS */;
/*!40000 ALTER TABLE `trabajador_recinto` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping routines for database 'proyectosDB'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-11-03 14:44:48
