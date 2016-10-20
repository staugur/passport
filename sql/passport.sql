-- MySQL dump 10.13  Distrib 5.6.33, for Linux (x86_64)
--
-- Host: localhost    Database: passport
-- ------------------------------------------------------
-- Server version	5.6.33

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
-- Current Database: `passport`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `passport` /*!40100 DEFAULT CHARACTER SET utf8 COLLATE utf8_unicode_ci */;

USE `passport`;

--
-- Table structure for table `LAuth`
--

DROP TABLE IF EXISTS `LAuth`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `LAuth` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `lauth_username` varchar(30) COLLATE utf8_unicode_ci NOT NULL,
  `lauth_password` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`,`lauth_username`),
  UNIQUE KEY `username` (`lauth_username`) USING BTREE,
  UNIQUE KEY `id` (`id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `LAuth`
--

LOCK TABLES `LAuth` WRITE;
/*!40000 ALTER TABLE `LAuth` DISABLE KEYS */;
INSERT INTO `LAuth` VALUES (1,'admin','8879168cbf8a9e11c296530803e93308'),(2,'saintic','8879168cbf8a9e11c296530803e93308'),(3,'sakura','8879168cbf8a9e11c296530803e93308'),(4,'staugur','8879168cbf8a9e11c296530803e93308'),(5,'taochengwei','8879168cbf8a9e11c296530803e93308');
/*!40000 ALTER TABLE `LAuth` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `OAuth`
--

DROP TABLE IF EXISTS `OAuth`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `OAuth` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `oauth_username` varchar(30) COLLATE utf8_unicode_ci NOT NULL,
  `oauth_type` varchar(9) COLLATE utf8_unicode_ci NOT NULL,
  `oauth_openid` varchar(41) COLLATE utf8_unicode_ci NOT NULL,
  `oauth_access_token` varchar(40) COLLATE utf8_unicode_ci NOT NULL,
  `oauth_expires` varchar(10) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`,`oauth_username`),
  UNIQUE KEY `openid` (`oauth_openid`) USING BTREE,
  UNIQUE KEY `id` (`id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `OAuth`
--

LOCK TABLES `OAuth` WRITE;
/*!40000 ALTER TABLE `OAuth` DISABLE KEYS */;
INSERT INTO `OAuth` VALUES (9,'QQ_AF8AA7E0F','QQ','AF8AA7E0F77451736DD97FB796849024','E94C6BE9B5632976B33892C693FF9FFF','2017-01-18'),(12,'Weibo_RWZ4ZDpPp','Weibo','3271188341','2.00RWZ4ZDpPpNuB645c8c2e44dACccB','2021-10-19'),(13,'QQ_C83D12014','QQ','C83D1201492C20026F74410F3F0904C4','3FFBFB8E7E0FBF9EE81AF8F2178AF976','2017-01-18'),(14,'QQ_9B72DAC02','QQ','9B72DAC022A38DC7D36C9BFF392F93A2','9114998634CF23BB03C1707AFDAA03B8','2017-01-18'),(15,'QQ_006BA58A0','QQ','006BA58A03B6C55D9BD2BC01451263A7','F665801EC5B1DFA2421B6C0A17D70691','2017-01-18'),(16,'QQ_C912C3A44','QQ','C912C3A4459366E6083009093F15A99B','8642D1B8E686CF5D4990B6D821D3515A','2017-01-17'),(17,'QQ_464F8186C','QQ','464F8186CB06B7F43F0A768DF0E9F105','5634DFDD360FFEC66945C7DCE69A3ED7','2017-01-16'),(18,'QQ_8A26C82CF','QQ','8A26C82CF475638821EEF834F9884EF0','F7B602C695B4913F016A6DA076646F50','2017-01-16'),(19,'QQ_C91E712F8','QQ','C91E712F8C23E489AF2AB9869CC3235D','FD96FD70F9A53B721A529AC1A00AC381','2017-01-16'),(20,'Weibo_PIKiQCpPp','Weibo','2079212423','2.00PIKiQCpPpNuB81deb168b0xM8x5D','2016-10-22'),(21,'QQ_8E1F1C7A5','QQ','8E1F1C7A562A6D8A60405DE883B2662A','87BA89AAFA99D04E45BCA7B88BF98CC5','2017-01-16'),(22,'QQ_8C9A426DA','QQ','8C9A426DAC79F4E53F76091A3F3960CC','B6FEC5DE9784002D053292BF76019EE3','2017-01-18'),(23,'QQ_E3F80F154','QQ','E3F80F154FBF9A9143EEF63D897C580F','12804462CEB6146A0C6F8597A8CC30A3','2017-01-18'),(24,'GitHub_staugur','GitHub','10270930','9c59e6d95eedcdf154f2759e4ad69da44db6cc07','2016-10-21');
/*!40000 ALTER TABLE `OAuth` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `SSO`
--

DROP TABLE IF EXISTS `SSO`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `SSO` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id` (`id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `SSO`
--

LOCK TABLES `SSO` WRITE;
/*!40000 ALTER TABLE `SSO` DISABLE KEYS */;
/*!40000 ALTER TABLE `SSO` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `User`
--

DROP TABLE IF EXISTS `User`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `User` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(32) COLLATE utf8_unicode_ci NOT NULL,
  `email` varchar(50) CHARACTER SET utf8 DEFAULT NULL,
  `cname` varchar(25) CHARACTER SET utf8 DEFAULT NULL,
  `avatar` varchar(300) CHARACTER SET utf8 DEFAULT NULL,
  `motto` varchar(200) CHARACTER SET utf8 DEFAULT NULL,
  `url` varchar(50) CHARACTER SET utf8 DEFAULT NULL,
  `time` varchar(10) COLLATE utf8_unicode_ci DEFAULT NULL,
  `weibo` varchar(30) COLLATE utf8_unicode_ci DEFAULT NULL,
  `github` varchar(30) COLLATE utf8_unicode_ci DEFAULT NULL,
  `extra` text CHARACTER SET utf8,
  PRIMARY KEY (`id`,`username`),
  UNIQUE KEY `username` (`username`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=93 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `User`
--

LOCK TABLES `User` WRITE;
/*!40000 ALTER TABLE `User` DISABLE KEYS */;
INSERT INTO `User` VALUES (1,'admin','staugur@saintic.com','陶成伟','/static/img/avatar/admin.jpg','原谅我一生放荡不羁爱自由','http://www.saintic.com','2016-10-14','http://weibo.com/staugur','https://github.com/staugur','Administrator'),(10,'QQ_AF8AA7E0F',NULL,'Together Forever!','http://q.qlogo.cn/qqapp/100581101/AF8AA7E0F77451736DD97FB796849024/40',NULL,NULL,'2016-10-16',NULL,NULL,'大家好，我是来自QQ的小伙伴！'),(22,'Weibo_RWZ4ZDpPp',NULL,'陶字成伟','http://tva3.sinaimg.cn/crop.0.0.200.200.50/c2fa5f75jw8f8w9kk6cydj205k05kdft.jpg',NULL,NULL,'2016-10-16','http://weibo.com/staugur',NULL,'www.saintic.com'),(24,'taochengwei',NULL,NULL,'/static/img/avatar/admin.jpg',NULL,NULL,'2016-10-17',NULL,NULL,NULL),(25,'sakura',NULL,NULL,'/static/img/avatar/admin.jpg',NULL,NULL,'2016-10-17',NULL,NULL,NULL),(26,'saintic',NULL,NULL,'/static/img/avatar/admin.jpg',NULL,NULL,'2016-10-17',NULL,NULL,NULL),(27,'staugur',NULL,NULL,'/static/img/avatar/admin.jpg',NULL,NULL,'2016-10-17',NULL,NULL,NULL),(36,'QQ_C83D12014',NULL,'ａ楠子','http://q.qlogo.cn/qqapp/100581101/C83D1201492C20026F74410F3F0904C4/40',NULL,NULL,'2016-10-18',NULL,NULL,'大家好，我是来自QQ的小伙伴！'),(37,'QQ_9B72DAC02',NULL,'楠子i','http://q.qlogo.cn/qqapp/100581101/9B72DAC022A38DC7D36C9BFF392F93A2/40',NULL,NULL,'2016-10-18',NULL,NULL,'大家好，我是来自QQ的小伙伴！'),(38,'QQ_006BA58A0',NULL,'瑕疵','http://q.qlogo.cn/qqapp/100581101/006BA58A03B6C55D9BD2BC01451263A7/40',NULL,NULL,'2016-10-18',NULL,NULL,'大家好，我是来自QQ的小伙伴！'),(40,'QQ_C912C3A44',NULL,'SaintIC Test','http://q.qlogo.cn/qqapp/100581101/C912C3A4459366E6083009093F15A99B/40',NULL,NULL,'2016-10-18',NULL,NULL,'大家好，我是来自QQ的小伙伴！'),(42,'QQ_464F8186C',NULL,'陪伴是最长情的告白','http://q.qlogo.cn/qqapp/100581101/464F8186CB06B7F43F0A768DF0E9F105/40',NULL,NULL,'2016-10-18',NULL,NULL,'大家好，我是来自QQ的小伙伴！'),(43,'QQ_8A26C82CF',NULL,'风继续吹','http://q.qlogo.cn/qqapp/100581101/8A26C82CF475638821EEF834F9884EF0/40',NULL,NULL,'2016-10-18',NULL,NULL,'大家好，我是来自QQ的小伙伴！'),(51,'QQ_C91E712F8',NULL,'致我爱的人','http://q.qlogo.cn/qqapp/100581101/C91E712F8C23E489AF2AB9869CC3235D/40',NULL,NULL,'2016-10-18',NULL,NULL,'大家好，我是来自QQ的小伙伴！'),(57,'Weibo_PIKiQCpPp',NULL,'楠子zzz','http://tva3.sinaimg.cn/crop.0.0.996.996.50/7bee4387jw8f8oc5x5588j20ro0rot9w.jpg',NULL,NULL,'2016-10-18','http://weibo.com/u/2079212423',NULL,'你从不孤单。因为这个世界上，肯定有个人，在努力的走到你的身边！'),(63,'QQ_8E1F1C7A5',NULL,'我想找个女朋友','http://q.qlogo.cn/qqapp/100581101/8E1F1C7A562A6D8A60405DE883B2662A/40',NULL,NULL,'2016-10-18',NULL,NULL,'大家好，我是来自QQ的小伙伴！'),(79,'QQ_8C9A426DA',NULL,'遮天','http://q.qlogo.cn/qqapp/100581101/8C9A426DAC79F4E53F76091A3F3960CC/40',NULL,NULL,'2016-10-20',NULL,NULL,'大家好，我是来自QQ的小伙伴！'),(80,'QQ_E3F80F154',NULL,'诸天诸代星辰幻灭','http://q.qlogo.cn/qqapp/100581101/E3F80F154FBF9A9143EEF63D897C580F/40',NULL,NULL,'2016-10-20',NULL,NULL,'大家好，我是来自QQ的小伙伴！'),(92,'GitHub_staugur','staugur@saintic.com','Mr.tao','https://avatars.githubusercontent.com/u/10270930?v=3',NULL,NULL,'2016-10-21',NULL,'https://github.com/staugur','blog:http://www.saintic.com, company:SaintIC, location:Beijing China');
/*!40000 ALTER TABLE `User` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2016-10-21  2:17:32
