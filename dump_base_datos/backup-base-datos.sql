-- MySQL dump 10.13  Distrib 9.1.0, for Linux (x86_64)
--
-- Host: localhost    Database: bd-tarjeta
-- ------------------------------------------------------
-- Server version	9.1.0

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
-- Table structure for table `cliente`
--

DROP TABLE IF EXISTS `cliente`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cliente` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) NOT NULL,
  `apellido` varchar(50) NOT NULL,
  `edad` int NOT NULL,
  `direccion` varchar(255) NOT NULL,
  `datos_laborales` text,
  `datos_beneficiarios` text,
  `dpi` varchar(13) NOT NULL,
  `numero_telefono` varchar(15) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `dpi` (`dpi`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cliente`
--

LOCK TABLES `cliente` WRITE;
/*!40000 ALTER TABLE `cliente` DISABLE KEYS */;
INSERT INTO `cliente` VALUES (1,'Juan','Garcia',35,'Guatemala','Arquitecto','Hija: Margaret','324554578202','3545-3675');
/*!40000 ALTER TABLE `cliente` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `mensaje_sms`
--

DROP TABLE IF EXISTS `mensaje_sms`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `mensaje_sms` (
  `id` int NOT NULL AUTO_INCREMENT,
  `numero_telefono` varchar(15) NOT NULL,
  `mensaje` text NOT NULL,
  `estado` enum('pendiente','enviado','fallido') DEFAULT 'pendiente',
  `fecha_envio` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `identificador_cola` varchar(255) NOT NULL,
  `tipo_mensaje` enum('cargo','abono') NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `mensaje_sms`
--

LOCK TABLES `mensaje_sms` WRITE;
/*!40000 ALTER TABLE `mensaje_sms` DISABLE KEYS */;
INSERT INTO `mensaje_sms` VALUES (1,'3545-3675','Se ha realizado un cargo a su tarjeta 6800680029249498 por Q100.00','pendiente','2024-11-22 23:49:14','1','cargo'),(2,'3545-3675','Se ha realizado un cargo a su tarjeta 6800680029249498 por Q100.00','pendiente','2024-11-23 03:12:37','1','cargo'),(3,'3545-3675','Se ha realizado un cargo a su tarjeta 6800680029249498 por Q100.00','pendiente','2024-11-23 03:13:23','2','cargo'),(4,'3545-3675','Se ha realizado un abono a su tarjeta 6800680029249498 por Q100.00','pendiente','2024-11-23 03:13:59','3','abono'),(5,'3545-3675','Se ha realizado un cargo a su tarjeta 6800680029249498 por Q100.00','pendiente','2024-11-23 03:15:34','4','cargo');
/*!40000 ALTER TABLE `mensaje_sms` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tarjeta_credito`
--

DROP TABLE IF EXISTS `tarjeta_credito`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tarjeta_credito` (
  `id` int NOT NULL AUTO_INCREMENT,
  `numero_tarjeta` char(16) NOT NULL,
  `limite_credito` decimal(10,2) NOT NULL,
  `saldo_actual` decimal(10,2) NOT NULL DEFAULT '0.00',
  `cliente_id` int NOT NULL,
  `replica_id` varchar(50) NOT NULL,
  `fecha_creacion` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `numero_tarjeta` (`numero_tarjeta`),
  KEY `cliente_id` (`cliente_id`),
  CONSTRAINT `tarjeta_credito_ibfk_1` FOREIGN KEY (`cliente_id`) REFERENCES `cliente` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tarjeta_credito`
--

LOCK TABLES `tarjeta_credito` WRITE;
/*!40000 ALTER TABLE `tarjeta_credito` DISABLE KEYS */;
INSERT INTO `tarjeta_credito` VALUES (1,'6800680029249498',15000.00,600.00,1,'98337614cc16','2024-11-22 23:44:26');
/*!40000 ALTER TABLE `tarjeta_credito` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `transaccion`
--

DROP TABLE IF EXISTS `transaccion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `transaccion` (
  `id` int NOT NULL AUTO_INCREMENT,
  `tarjeta_id` int NOT NULL,
  `tipo` enum('CARGO','ABONO') NOT NULL,
  `monto` decimal(10,2) NOT NULL,
  `fecha` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `tarjeta_id` (`tarjeta_id`),
  CONSTRAINT `transaccion_ibfk_1` FOREIGN KEY (`tarjeta_id`) REFERENCES `tarjeta_credito` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `transaccion`
--

LOCK TABLES `transaccion` WRITE;
/*!40000 ALTER TABLE `transaccion` DISABLE KEYS */;
INSERT INTO `transaccion` VALUES (1,1,'CARGO',100.00,'2024-11-22 23:44:37'),(2,1,'CARGO',100.00,'2024-11-22 23:49:14'),(3,1,'CARGO',100.00,'2024-11-23 03:09:33'),(4,1,'CARGO',100.00,'2024-11-23 03:09:48'),(5,1,'CARGO',100.00,'2024-11-23 03:12:37'),(6,1,'CARGO',100.00,'2024-11-23 03:13:22'),(7,1,'ABONO',100.00,'2024-11-23 03:13:59'),(8,1,'CARGO',100.00,'2024-11-23 03:15:34');
/*!40000 ALTER TABLE `transaccion` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-11-23  3:23:01
