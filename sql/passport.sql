/*
Navicat MySQL Data Transfer

Source Server         : 101.200.125.9
Source Server Version : 50634
Source Host           : localhost:3306
Source Database       : passport

Target Server Type    : MYSQL
Target Server Version : 50634
File Encoding         : 65001

Date: 2016-11-11 17:38:04
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
  `oauth_access_token` varchar(40) COLLATE utf8_unicode_ci NOT NULL,
  `oauth_expires` varchar(10) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`,`oauth_username`),
  UNIQUE KEY `openid` (`oauth_openid`) USING BTREE,
  UNIQUE KEY `id` (`id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=30 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- ----------------------------
-- Records of OAuth
-- ----------------------------
INSERT INTO `OAuth` VALUES ('9', 'QQ_AF8AA7E0F', 'QQ', 'AF8AA7E0F77451736DD97FB796849024', 'ED1A1ADDEE5C3AF5A0F44F5AE924FFE1', '2017-02-08');
INSERT INTO `OAuth` VALUES ('12', 'Weibo_RWZ4ZDpPp', 'Weibo', '3271188341', '2.00RWZ4ZDpPpNuB645c8c2e44dACccB', '2021-11-09');
INSERT INTO `OAuth` VALUES ('13', 'QQ_C83D12014', 'QQ', 'C83D1201492C20026F74410F3F0904C4', 'ADEC2817642278875B565FD4464D8A93', '2017-02-02');
INSERT INTO `OAuth` VALUES ('14', 'QQ_9B72DAC02', 'QQ', '9B72DAC022A38DC7D36C9BFF392F93A2', '9114998634CF23BB03C1707AFDAA03B8', '2017-01-18');
INSERT INTO `OAuth` VALUES ('15', 'QQ_006BA58A0', 'QQ', '006BA58A03B6C55D9BD2BC01451263A7', 'F665801EC5B1DFA2421B6C0A17D70691', '2017-01-18');
INSERT INTO `OAuth` VALUES ('16', 'QQ_C912C3A44', 'QQ', 'C912C3A4459366E6083009093F15A99B', 'C8CCDE8269C69225780B5BF5A9618B28', '2017-02-05');
INSERT INTO `OAuth` VALUES ('17', 'QQ_464F8186C', 'QQ', '464F8186CB06B7F43F0A768DF0E9F105', '5634DFDD360FFEC66945C7DCE69A3ED7', '2017-01-16');
INSERT INTO `OAuth` VALUES ('18', 'QQ_8A26C82CF', 'QQ', '8A26C82CF475638821EEF834F9884EF0', '8BB7E2852518D63269D8C07016148597', '2017-01-19');
INSERT INTO `OAuth` VALUES ('19', 'QQ_C91E712F8', 'QQ', 'C91E712F8C23E489AF2AB9869CC3235D', 'FD96FD70F9A53B721A529AC1A00AC381', '2017-01-16');
INSERT INTO `OAuth` VALUES ('20', 'Weibo_PIKiQCpPp', 'Weibo', '2079212423', '2.00PIKiQCpPpNuB81deb168b0xM8x5D', '2016-10-22');
INSERT INTO `OAuth` VALUES ('21', 'QQ_8E1F1C7A5', 'QQ', '8E1F1C7A562A6D8A60405DE883B2662A', '87BA89AAFA99D04E45BCA7B88BF98CC5', '2017-01-16');
INSERT INTO `OAuth` VALUES ('22', 'QQ_8C9A426DA', 'QQ', '8C9A426DAC79F4E53F76091A3F3960CC', 'B6FEC5DE9784002D053292BF76019EE3', '2017-01-18');
INSERT INTO `OAuth` VALUES ('23', 'QQ_E3F80F154', 'QQ', 'E3F80F154FBF9A9143EEF63D897C580F', '12804462CEB6146A0C6F8597A8CC30A3', '2017-01-18');
INSERT INTO `OAuth` VALUES ('24', 'GitHub_staugur', 'GitHub', '10270930', 'f027d21cf5bb8240c9258942e2d8c47304262459', '2016-11-10');
INSERT INTO `OAuth` VALUES ('25', 'QQ_7405517AC', 'QQ', '7405517ACF446D6EB808FF08EA1AC4A9', '87DA014AA7ECB4B77E1888F7C5543E4D', '2017-01-19');
INSERT INTO `OAuth` VALUES ('26', 'Weibo_GuWTbGpPp', 'Weibo', '6050559422', '2.00GuWTbGpPpNuB3aa6bad660QVVdJC', '2016-11-21');
INSERT INTO `OAuth` VALUES ('27', 'GitHub_LXSakura', 'GitHub', '16093434', '4f4ed1b905c0a45856df9057f0172d3043f25a18', '2016-11-09');
INSERT INTO `OAuth` VALUES ('28', 'Weibo_vXs5iBpPp', 'Weibo', '1572221167', '2.00vXs5iBpPpNuB01d8a18570w6ms7E', '2016-12-11');
INSERT INTO `OAuth` VALUES ('29', 'QQ_30F7762DB', 'QQ', '30F7762DBFB1450DDF0BBDBF50D1CB23', 'F02B990CE32FA6298E413E5323A77D89', '2017-02-09');

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
) ENGINE=InnoDB AUTO_INCREMENT=141 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- ----------------------------
-- Records of User
-- ----------------------------
INSERT INTO `User` VALUES ('1', 'admin', 'staugur@saintic.com', '管理员', '/static/img/avatar/admin.jpg', '原谅我一生放荡不羁爱自由', 'http://www.saintic.com', '2016-10-14', 'http://weibo.com/staugur', 'https://github.com/staugur', '男', 'Administrator', 'false');
INSERT INTO `User` VALUES ('10', 'QQ_AF8AA7E0F', null, 'Together Forever!', 'http://q.qlogo.cn/qqapp/100581101/AF8AA7E0F77451736DD97FB796849024/40', null, null, '2016-10-16', null, null, '男', '北京 朝阳', 'false');
INSERT INTO `User` VALUES ('22', 'Weibo_RWZ4ZDpPp', null, '陶字成伟', 'http://tva3.sinaimg.cn/crop.0.0.200.200.50/c2fa5f75jw8f8w9kk6cydj205k05kdft.jpg', null, null, '2016-10-16', 'http://weibo.com/staugur', null, '男', 'www.saintic.com', 'false');
INSERT INTO `User` VALUES ('24', 'taochengwei', 'staugur@vip.qq.com', '陶先森', '/static/img/avatar/default.jpg', '我命由我不由天', 'https://blog.saintic.com', '2016-10-17', 'weibo.com/staugur', 'github.com/saintic', '男', null, 'false');
INSERT INTO `User` VALUES ('25', 'sakura', null, '木', '/static/img/avatar/default.jpg', null, null, '2016-10-17', null, null, '女', null, 'false');
INSERT INTO `User` VALUES ('26', 'saintic', null, null, '/static/img/avatar/default.jpg', null, null, '2016-10-17', null, null, null, null, 'false');
INSERT INTO `User` VALUES ('27', 'staugur', null, null, '/static/img/avatar/default.jpg', null, null, '2016-10-17', null, null, null, null, 'false');
INSERT INTO `User` VALUES ('36', 'QQ_C83D12014', null, 'ａ楠子', 'http://q.qlogo.cn/qqapp/100581101/C83D1201492C20026F74410F3F0904C4/40', null, null, '2016-10-18', null, null, '女', '北京 ', 'false');
INSERT INTO `User` VALUES ('37', 'QQ_9B72DAC02', null, '楠子i', 'http://q.qlogo.cn/qqapp/100581101/9B72DAC022A38DC7D36C9BFF392F93A2/40', null, null, '2016-10-18', null, null, null, '大家好，我是来自QQ的小伙伴！', 'false');
INSERT INTO `User` VALUES ('38', 'QQ_006BA58A0', null, '瑕疵', 'http://q.qlogo.cn/qqapp/100581101/006BA58A03B6C55D9BD2BC01451263A7/40', null, null, '2016-10-18', null, null, null, '大家好，我是来自QQ的小伙伴！', 'false');
INSERT INTO `User` VALUES ('40', 'QQ_C912C3A44', null, 'SaintIC Test', 'http://q.qlogo.cn/qqapp/100581101/C912C3A4459366E6083009093F15A99B/40', null, null, '2016-10-18', null, null, '男', '北京 朝阳', 'false');
INSERT INTO `User` VALUES ('42', 'QQ_464F8186C', null, '陪伴是最长情的告白', 'http://q.qlogo.cn/qqapp/100581101/464F8186CB06B7F43F0A768DF0E9F105/40', null, null, '2016-10-18', null, null, null, '大家好，我是来自QQ的小伙伴！', 'false');
INSERT INTO `User` VALUES ('43', 'QQ_8A26C82CF', null, '风继续吹', 'http://q.qlogo.cn/qqapp/100581101/8A26C82CF475638821EEF834F9884EF0/40', null, null, '2016-10-18', null, null, null, '大家好，我是来自QQ的小伙伴！', 'false');
INSERT INTO `User` VALUES ('51', 'QQ_C91E712F8', null, '致我爱的人', 'http://q.qlogo.cn/qqapp/100581101/C91E712F8C23E489AF2AB9869CC3235D/40', null, null, '2016-10-18', null, null, null, '大家好，我是来自QQ的小伙伴！', 'false');
INSERT INTO `User` VALUES ('57', 'Weibo_PIKiQCpPp', null, '楠子zzz', 'http://tva3.sinaimg.cn/crop.0.0.996.996.50/7bee4387jw8f8oc5x5588j20ro0rot9w.jpg', null, null, '2016-10-18', 'http://weibo.com/u/2079212423', null, null, '你从不孤单。因为这个世界上，肯定有个人，在努力的走到你的身边！', 'false');
INSERT INTO `User` VALUES ('63', 'QQ_8E1F1C7A5', null, '我想找个女朋友', 'http://q.qlogo.cn/qqapp/100581101/8E1F1C7A562A6D8A60405DE883B2662A/40', null, null, '2016-10-18', null, null, null, '大家好，我是来自QQ的小伙伴！', 'false');
INSERT INTO `User` VALUES ('79', 'QQ_8C9A426DA', null, '遮天', 'http://q.qlogo.cn/qqapp/100581101/8C9A426DAC79F4E53F76091A3F3960CC/40', null, null, '2016-10-20', null, null, null, '大家好，我是来自QQ的小伙伴！', 'false');
INSERT INTO `User` VALUES ('80', 'QQ_E3F80F154', null, '诸天诸代星辰幻灭', 'http://q.qlogo.cn/qqapp/100581101/E3F80F154FBF9A9143EEF63D897C580F/40', null, null, '2016-10-20', null, null, null, '大家好，我是来自QQ的小伙伴！', 'false');
INSERT INTO `User` VALUES ('92', 'GitHub_staugur', 'staugur@saintic.com', 'Mr.tao', 'https://avatars.githubusercontent.com/u/10270930?v=3', null, null, '2016-10-21', null, 'https://github.com/staugur', null, 'blog:http://www.saintic.com, company:SaintIC, location:Beijing China', 'false');
INSERT INTO `User` VALUES ('95', 'QQ_7405517AC', null, '  \"九霄 倾心\"', 'http://q.qlogo.cn/qqapp/100581101/7405517ACF446D6EB808FF08EA1AC4A9/40', null, null, '2016-10-21', null, null, null, '大家好，我是来自QQ的小伙伴！', 'false');
INSERT INTO `User` VALUES ('109', 'Weibo_GuWTbGpPp', null, '楠子要阳光', 'http://tva2.sinaimg.cn/crop.0.0.200.200.50/006BtwU6jw8f8yoi8r709j305k05ka9y.jpg', null, null, '2016-10-21', 'http://weibo.com/u/6050559422', null, '女', '喜欢就去表白，相爱就一定要相守。', 'false');
INSERT INTO `User` VALUES ('130', 'GitHub_LXSakura', null, 'Mr.Sa', 'https://avatars.githubusercontent.com/u/16093434?v=3', null, null, '2016-11-09', null, 'https://github.com/LXSakura', null, 'blog:None, company:Emar, location:None', 'false');
INSERT INTO `User` VALUES ('131', 'Weibo_vXs5iBpPp', null, '隐藏人物', 'http://tva4.sinaimg.cn/crop.0.0.180.180.50/5db630efjw8egw3uufwg2j2050050jrh.jpg', null, null, '2016-11-10', 'http://weibo.com/linz', null, '男', '我是一个互联网工作者，我深深地爱着我的网民。不要问我为什么总是饱含泪水，因为我对我的网民爱得深沉⋯⋯', 'false');
INSERT INTO `User` VALUES ('140', 'QQ_30F7762DB', null, 'As', 'http://q.qlogo.cn/qqapp/100581101/30F7762DBFB1450DDF0BBDBF50D1CB23/40', null, null, '2016-11-11', null, null, '男', '上海 浦东新区', 'false');
