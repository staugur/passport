/*
Navicat MySQL Data Transfer

Source Server         : 101.200.125.9
Source Server Version : 50633
Source Host           : localhost:3306
Source Database       : passport

Target Server Type    : MYSQL
Target Server Version : 50633
File Encoding         : 65001

Date: 2016-10-12 17:58:50
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for LAuth
-- ----------------------------
DROP TABLE IF EXISTS `LAuth`;
CREATE TABLE `LAuth` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `lauth_username` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `lauth_password` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`,`lauth_username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- ----------------------------
-- Records of LAuth
-- ----------------------------

-- ----------------------------
-- Table structure for OAuth
-- ----------------------------
DROP TABLE IF EXISTS `OAuth`;
CREATE TABLE `OAuth` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `oauth_username` varchar(30) COLLATE utf8_unicode_ci NOT NULL,
  `oauth_type` varchar(9) COLLATE utf8_unicode_ci NOT NULL,
  `oauth_openid` varchar(41) COLLATE utf8_unicode_ci NOT NULL,
  `oauth_access_token` varchar(32) COLLATE utf8_unicode_ci NOT NULL,
  `oauth_expires` date NOT NULL,
  PRIMARY KEY (`id`,`oauth_username`),
  UNIQUE KEY `openid` (`oauth_openid`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- ----------------------------
-- Records of OAuth
-- ----------------------------

-- ----------------------------
-- Table structure for User
-- ----------------------------
DROP TABLE IF EXISTS `User`;
CREATE TABLE `User` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(32) COLLATE utf8_unicode_ci NOT NULL,
  `email` varchar(50) CHARACTER SET utf8 DEFAULT NULL,
  `cname` varchar(25) CHARACTER SET utf8 DEFAULT NULL,
  `avatar` varchar(300) CHARACTER SET utf8 DEFAULT NULL,
  `motto` varchar(200) CHARACTER SET utf8 DEFAULT NULL,
  `url` varchar(50) CHARACTER SET utf8 DEFAULT NULL,
  `time` date DEFAULT NULL,
  `weibo` varchar(30) COLLATE utf8_unicode_ci DEFAULT NULL,
  `github` varchar(30) COLLATE utf8_unicode_ci DEFAULT NULL,
  `extra` varchar(500) CHARACTER SET utf8 DEFAULT NULL,
  PRIMARY KEY (`id`,`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- ----------------------------
-- Records of User
-- ----------------------------
