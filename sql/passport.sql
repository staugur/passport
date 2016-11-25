/*
Navicat MySQL Data Transfer

Source Server         : 101.200.125.9
Source Server Version : 50634
Source Host           : 127.0.0.1:3306
Source Database       : saintic

Target Server Type    : MYSQL
Target Server Version : 50634
File Encoding         : 65001

Date: 2016-11-18 22:15:05
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for blog
-- ----------------------------
DROP TABLE IF EXISTS `blog`;
CREATE TABLE `blog` (
  `id` int(4) NOT NULL AUTO_INCREMENT COMMENT 'BlogId',
  `title` varchar(88) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL COMMENT '文章标题',
  `content` varchar(20000) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL COMMENT '文章',
  `create_time` varchar(20) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '文章创建时间',
  `update_time` varchar(20) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '文章更新时间',
  `tag` varchar(30) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT '技术' COMMENT '文章标签',
  `catalog` varchar(30) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT '未分类' COMMENT '文章分类目录',
  `sources` varchar(30) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT '原创' COMMENT '''Original\n,Reprint\n,Translate|原创,转载,翻译''',
  `author` varchar(255) DEFAULT 'admin',
  `editor` varchar(255) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT 'wangEditor',
  PRIMARY KEY (`id`),
  KEY `id` (`id`,`create_time`,`tag`,`catalog`,`sources`,`author`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for clickLog
-- ----------------------------
DROP TABLE IF EXISTS `clickLog`;
CREATE TABLE `clickLog` (
  `id` int(6) NOT NULL AUTO_INCREMENT,
  `requestId` varchar(36) COLLATE utf8_unicode_ci NOT NULL,
  `url` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `agent` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `method` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `ip` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `status_code` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `referer` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

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
-- Records of LAuth
-- ----------------------------
INSERT INTO `LAuth` VALUES ('1', 'admin', '8879168cbf8a9e11c296530803e93308');

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
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

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
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- ----------------------------
-- Records of User
-- ----------------------------
INSERT INTO `User` VALUES ('1', 'admin', 'staugur@saintic.com', '管理员', '/static/img/avatar/admin.jpg', '原谅我一生放荡不羁爱自由', 'http://www.saintic.com', '2016-10-14', 'http://weibo.com/staugur', 'https://github.com/staugur', '男', 'Administrator', 'false');
