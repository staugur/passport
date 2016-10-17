/*
Navicat MySQL Data Transfer

Source Server         : 101.200.125.9
Source Server Version : 50633
Source Host           : localhost:3306
Source Database       : passport

Target Server Type    : MYSQL
Target Server Version : 50633
File Encoding         : 65001

Date: 2016-10-17 17:30:45
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
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- ----------------------------
-- Records of LAuth
-- ----------------------------
INSERT INTO `LAuth` VALUES ('1', 'admin', '8879168cbf8a9e11c296530803e93308');
INSERT INTO `LAuth` VALUES ('2', 'saintic', '8879168cbf8a9e11c296530803e93308');
INSERT INTO `LAuth` VALUES ('3', 'sakura', '8879168cbf8a9e11c296530803e93308');
INSERT INTO `LAuth` VALUES ('4', 'staugur', '8879168cbf8a9e11c296530803e93308');
INSERT INTO `LAuth` VALUES ('5', 'taochengwei', '8879168cbf8a9e11c296530803e93308');

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
  `oauth_expires` varchar(10) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`,`oauth_username`),
  UNIQUE KEY `openid` (`oauth_openid`) USING BTREE,
  UNIQUE KEY `id` (`id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- ----------------------------
-- Records of OAuth
-- ----------------------------
INSERT INTO `OAuth` VALUES ('9', 'QQ_AF8AA7E0F', 'QQ', 'AF8AA7E0F77451736DD97FB796849024', 'FA7CA5E4E94AA3941C7484E1EF50861B', '2017-01-14');
INSERT INTO `OAuth` VALUES ('12', 'Weibo_RWZ4ZDpPp', 'Weibo', '3271188341', '2.00RWZ4ZDpPpNuB645c8c2e44dACccB', '2021-10-15');

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
  `time` varchar(10) COLLATE utf8_unicode_ci DEFAULT NULL,
  `weibo` varchar(30) COLLATE utf8_unicode_ci DEFAULT NULL,
  `github` varchar(30) COLLATE utf8_unicode_ci DEFAULT NULL,
  `extra` text CHARACTER SET utf8,
  PRIMARY KEY (`id`,`username`),
  UNIQUE KEY `username` (`username`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=24 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- ----------------------------
-- Records of User
-- ----------------------------
INSERT INTO `User` VALUES ('1', 'admin', 'staugur@saintic.com', '陶成伟', '/static/upload/15768284.jpg', '原谅我一生放荡不羁爱自由', 'www.saintic.com', '2016-10-14', 'weibo.com/staugur', 'github.com/staugur', 'Administrator');
INSERT INTO `User` VALUES ('10', 'QQ_AF8AA7E0F', null, 'Together Forever!', 'http://q.qlogo.cn/qqapp/100581101/AF8AA7E0F77451736DD97FB796849024/40', null, null, '2016-10-16', null, null, '大家好，我是来自QQ的小伙伴！');
INSERT INTO `User` VALUES ('22', 'Weibo_RWZ4ZDpPp', null, '姓陶字成伟', 'http://tva1.sinaimg.cn/crop.25.0.330.330.50/c2fa5f75gw1en2jxj0o7xj20a5099aae.jpg', null, null, '2016-10-16', 'weibo.com/staugur', null, 'www.saintic.com');
