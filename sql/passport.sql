/*
Navicat MySQL Data Transfer

Source Server         : 101.200.125.9
Source Server Version : 50633
Source Host           : localhost:3306
Source Database       : passport

Target Server Type    : MYSQL
Target Server Version : 50633
File Encoding         : 65001

Date: 2016-10-18 11:52:19
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
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- ----------------------------
-- Records of OAuth
-- ----------------------------
INSERT INTO `OAuth` VALUES ('9', 'QQ_AF8AA7E0F', 'QQ', 'AF8AA7E0F77451736DD97FB796849024', '861B113AD1B8D386882A27C05E3805C3', '2017-01-16');
INSERT INTO `OAuth` VALUES ('12', 'Weibo_RWZ4ZDpPp', 'Weibo', '3271188341', '2.00RWZ4ZDpPpNuB645c8c2e44dACccB', '2021-10-17');
INSERT INTO `OAuth` VALUES ('13', 'QQ_C83D12014', 'QQ', 'C83D1201492C20026F74410F3F0904C4', '3FBAC5C2F590F1E38051C7ABB41D8D21', '2017-01-16');
INSERT INTO `OAuth` VALUES ('14', 'QQ_9B72DAC02', 'QQ', '9B72DAC022A38DC7D36C9BFF392F93A2', 'DA336BD86DD2AAE44E9BEF01AA3BB3E0', '2017-01-16');
INSERT INTO `OAuth` VALUES ('15', 'QQ_006BA58A0', 'QQ', '006BA58A03B6C55D9BD2BC01451263A7', '76A120E9E8F9C830FCBCBE0A07E635F9', '2017-01-16');
INSERT INTO `OAuth` VALUES ('16', 'QQ_C912C3A44', 'QQ', 'C912C3A4459366E6083009093F15A99B', '9B02840E3B635AA3690228D2C3D35488', '2017-01-16');
INSERT INTO `OAuth` VALUES ('17', 'QQ_464F8186C', 'QQ', '464F8186CB06B7F43F0A768DF0E9F105', '5634DFDD360FFEC66945C7DCE69A3ED7', '2017-01-16');
INSERT INTO `OAuth` VALUES ('18', 'QQ_8A26C82CF', 'QQ', '8A26C82CF475638821EEF834F9884EF0', 'F7B602C695B4913F016A6DA076646F50', '2017-01-16');
INSERT INTO `OAuth` VALUES ('19', 'QQ_C91E712F8', 'QQ', 'C91E712F8C23E489AF2AB9869CC3235D', 'FD96FD70F9A53B721A529AC1A00AC381', '2017-01-16');

-- ----------------------------
-- Table structure for SSO
-- ----------------------------
DROP TABLE IF EXISTS `SSO`;
CREATE TABLE `SSO` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id` (`id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- ----------------------------
-- Records of SSO
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
  `time` varchar(10) COLLATE utf8_unicode_ci DEFAULT NULL,
  `weibo` varchar(30) COLLATE utf8_unicode_ci DEFAULT NULL,
  `github` varchar(30) COLLATE utf8_unicode_ci DEFAULT NULL,
  `extra` text CHARACTER SET utf8,
  PRIMARY KEY (`id`,`username`),
  UNIQUE KEY `username` (`username`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=57 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- ----------------------------
-- Records of User
-- ----------------------------
INSERT INTO `User` VALUES ('1', 'admin', 'staugur@saintic.com', '陶成伟', '/static/upload/15768284.jpg', '原谅我一生放荡不羁爱自由', 'www.saintic.com', '2016-10-14', 'weibo.com/staugur', 'github.com/staugur', 'Administrator');
INSERT INTO `User` VALUES ('10', 'QQ_AF8AA7E0F', null, 'Together Forever!', 'http://q.qlogo.cn/qqapp/100581101/AF8AA7E0F77451736DD97FB796849024/40', null, null, '2016-10-16', null, null, '大家好，我是来自QQ的小伙伴！');
INSERT INTO `User` VALUES ('22', 'Weibo_RWZ4ZDpPp', null, '姓陶字成伟', 'http://tva3.sinaimg.cn/crop.0.0.200.200.50/c2fa5f75jw8f8w9kk6cydj205k05kdft.jpg', null, null, '2016-10-16', 'weibo.com/staugur', null, 'www.saintic.com');
INSERT INTO `User` VALUES ('24', 'taochengwei', null, null, null, null, null, '2016-10-17', null, null, null);
INSERT INTO `User` VALUES ('25', 'sakura', null, null, null, null, null, '2016-10-17', null, null, null);
INSERT INTO `User` VALUES ('26', 'saintic', null, null, null, null, null, '2016-10-17', null, null, null);
INSERT INTO `User` VALUES ('27', 'staugur', null, null, null, null, null, '2016-10-17', null, null, null);
INSERT INTO `User` VALUES ('36', 'QQ_C83D12014', null, 'ａ楠子', 'http://q.qlogo.cn/qqapp/100581101/C83D1201492C20026F74410F3F0904C4/40', null, null, '2016-10-18', null, null, '大家好，我是来自QQ的小伙伴！');
INSERT INTO `User` VALUES ('37', 'QQ_9B72DAC02', null, '楠子i', 'http://q.qlogo.cn/qqapp/100581101/9B72DAC022A38DC7D36C9BFF392F93A2/40', null, null, '2016-10-18', null, null, '大家好，我是来自QQ的小伙伴！');
INSERT INTO `User` VALUES ('38', 'QQ_006BA58A0', null, '瑕疵', 'http://q.qlogo.cn/qqapp/100581101/006BA58A03B6C55D9BD2BC01451263A7/40', null, null, '2016-10-18', null, null, '大家好，我是来自QQ的小伙伴！');
INSERT INTO `User` VALUES ('40', 'QQ_C912C3A44', null, '情不知所起一往而深', 'http://q.qlogo.cn/qqapp/100581101/C912C3A4459366E6083009093F15A99B/40', null, null, '2016-10-18', null, null, '大家好，我是来自QQ的小伙伴！');
INSERT INTO `User` VALUES ('42', 'QQ_464F8186C', null, '陪伴是最长情的告白', 'http://q.qlogo.cn/qqapp/100581101/464F8186CB06B7F43F0A768DF0E9F105/40', null, null, '2016-10-18', null, null, '大家好，我是来自QQ的小伙伴！');
INSERT INTO `User` VALUES ('43', 'QQ_8A26C82CF', null, '风继续吹', 'http://q.qlogo.cn/qqapp/100581101/8A26C82CF475638821EEF834F9884EF0/40', null, null, '2016-10-18', null, null, '大家好，我是来自QQ的小伙伴！');
INSERT INTO `User` VALUES ('51', 'QQ_C91E712F8', null, '致我爱的人', 'http://q.qlogo.cn/qqapp/100581101/C91E712F8C23E489AF2AB9869CC3235D/40', null, null, '2016-10-18', null, null, '大家好，我是来自QQ的小伙伴！');
