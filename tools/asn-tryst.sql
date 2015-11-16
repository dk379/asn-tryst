-- MySQL dump 10.13  Distrib 5.6.27, for osx10.8 (x86_64)
--
-- Host: ***.***.***.***    Database: asn-tryst
-- ------------------------------------------------------
-- Server version	5.6.26

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `IPSV4`
--

DROP TABLE IF EXISTS `IPSV4`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `IPSV4` (
  `IP` int(10) unsigned NOT NULL,
  `AUTNUM` int(10) unsigned NOT NULL,
  PRIMARY KEY (`IP`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `IPSV4GEO`
--

DROP TABLE IF EXISTS `IPSV4GEO`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `IPSV4GEO` (
  `IP` int(10) unsigned NOT NULL,
  `LATITUDE` decimal(11,8) NOT NULL DEFAULT '0.00000000',
  `LONGITUDE` decimal(11,8) NOT NULL DEFAULT '0.00000000',
  PRIMARY KEY (`IP`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `IPSV6`
--

DROP TABLE IF EXISTS `IPSV6`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `IPSV6` (
  `IP` varbinary(16) NOT NULL,
  `AUTNUM` int(10) unsigned NOT NULL,
  PRIMARY KEY (`IP`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `IPSV6GEO`
--

DROP TABLE IF EXISTS `IPSV6GEO`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `IPSV6GEO` (
  `IP` varbinary(16) NOT NULL,
  `LATITUDE` decimal(11,8) NOT NULL DEFAULT '0.00000000',
  `LONGITUDE` decimal(11,8) NOT NULL DEFAULT '0.00000000',
  PRIMARY KEY (`IP`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `IPV4PAIRS`
--

DROP TABLE IF EXISTS `IPV4PAIRS`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `IPV4PAIRS` (
  `PAIR_ID` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `IP1` int(10) unsigned NOT NULL,
  `IP2` int(10) unsigned NOT NULL,
  PRIMARY KEY (`PAIR_ID`),
  UNIQUE KEY `IP1` (`IP1`,`IP2`),
  KEY `IP2` (`IP2`)
) ENGINE=InnoDB AUTO_INCREMENT=4442 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `IPV6PAIRS`
--

DROP TABLE IF EXISTS `IPV6PAIRS`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `IPV6PAIRS` (
  `ID` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `IP1` varbinary(16) DEFAULT NULL,
  `IP2` varbinary(16) DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `IP1` (`IP1`,`IP2`)
) ENGINE=InnoDB AUTO_INCREMENT=401 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `MIDS`
--

DROP TABLE IF EXISTS `MIDS`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `MIDS` (
  `id` int(10) DEFAULT NULL,
  `msm_id` int(10) DEFAULT NULL,
  `timestamp` datetime DEFAULT NULL,
  `PAIR_ID` int(10) unsigned DEFAULT NULL,
  `af` int(1) unsigned DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `asn_to_name`
--

DROP TABLE IF EXISTS `asn_to_name`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `asn_to_name` (
  `asn` int(10) unsigned NOT NULL,
  `name` varchar(180) NOT NULL,
  PRIMARY KEY (`asn`),
  KEY `asn` (`asn`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `measurements`
--

DROP TABLE IF EXISTS `measurements`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `measurements` (
  `msm_id` int(10) unsigned NOT NULL,
  `af` int(1) DEFAULT NULL,
  `description` text COLLATE utf8_bin NOT NULL,
  `start_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `stop_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `interv` int(10) DEFAULT NULL,
  UNIQUE KEY `msm_id` (`msm_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `openipmap_locations`
--

DROP TABLE IF EXISTS `openipmap_locations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `openipmap_locations` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `ip` varbinary(16) DEFAULT NULL,
  `lat` decimal(10,8) NOT NULL,
  `lon` decimal(11,8) NOT NULL,
  `place` text COLLATE utf8_bin NOT NULL,
  `hostname` text COLLATE utf8_bin NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ip_idx` (`ip`)
) ENGINE=InnoDB AUTO_INCREMENT=32942 DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2015-11-16  2:57:49
