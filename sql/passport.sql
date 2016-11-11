/*
Navicat MySQL Data Transfer

Source Server         : 101.200.125.9
Source Server Version : 50634
Source Host           : localhost:3306
Source Database       : passport

Target Server Type    : MYSQL
Target Server Version : 50634
File Encoding         : 65001

Date: 2016-11-11 11:20:47
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for LAuth
-- ----------------------------
DROP TABLE IF EXISTS `LAuth`;
CREATE TABLE `LAuth` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `lauth_username` varchar(30) COLLATE utf8_unicode_ci NOT NULL,
  `lauth_password` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`,`lauth_username`),
  UNIQUE KEY `username` (`lauth_username`) USING BTREE,
  UNIQUE KEY `id` (`id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- ----------------------------
-- Table structure for OAuth
-- ----------------------------
DROP TABLE IF EXISTS `OAuth`;
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
) ENGINE=InnoDB AUTO_INCREMENT=29 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- ----------------------------
-- Table structure for User
-- ----------------------------
DROP TABLE IF EXISTS `User`;
CREATE TABLE `User` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(32) COLLATE utf8_unicode_ci NOT NULL,
  `email` varchar(50) COLLATE utf8_unicode_ci DEFAULT NULL,
  `cname` varchar(25) COLLATE utf8_unicode_ci DEFAULT NULL,
  `avatar` varchar(300) COLLATE utf8_unicode_ci DEFAULT NULL,
  `motto` varchar(200) COLLATE utf8_unicode_ci DEFAULT NULL,
  `url` varchar(50) COLLATE utf8_unicode_ci DEFAULT NULL,
  `time` varchar(10) COLLATE utf8_unicode_ci DEFAULT NULL,
  `weibo` varchar(30) COLLATE utf8_unicode_ci DEFAULT NULL,
  `github` varchar(30) COLLATE utf8_unicode_ci DEFAULT NULL,
  `gender` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `extra` text COLLATE utf8_unicode_ci,
  `isAdmin` varchar(255) COLLATE utf8_unicode_ci DEFAULT 'false',
  PRIMARY KEY (`id`,`username`),
  UNIQUE KEY `username` (`username`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=140 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
