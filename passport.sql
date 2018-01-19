/*
Navicat MySQL Data Transfer

Source Server         : localhost
Source Server Version : 50720
Source Host           : localhost:3306
Source Database       : passport

Target Server Type    : MYSQL
Target Server Version : 50720
File Encoding         : 65001

Date: 2018-01-19 18:35:51
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for user_auth
-- ----------------------------
DROP TABLE IF EXISTS `user_auth`;
CREATE TABLE `user_auth` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `uid` char(22) NOT NULL COMMENT '用户id',
  `identity_type` tinyint(4) unsigned NOT NULL COMMENT '1手机号 2邮箱 3GitHub 4qq 5微信 6腾讯微博 7新浪微博',
  `identifier` varchar(50) NOT NULL DEFAULT '' COMMENT '手机号、邮箱或第三方应用的唯一标识(openid、union_id)',
  `certificate` varchar(106) NOT NULL DEFAULT '' COMMENT '密码凭证(站内的保存密码，站外的不保存或保存token)',
  `verified` tinyint(1) unsigned NOT NULL DEFAULT '0' COMMENT '是否已验证 0-未验证 1-已验证',
  `status` tinyint(1) unsigned NOT NULL DEFAULT '1' COMMENT '用户状态 0-禁用 1-启用',
  `create_time` int(11) unsigned NOT NULL DEFAULT '0' COMMENT '绑定时间',
  `update_time` int(11) unsigned DEFAULT '0' COMMENT '更新绑定时间',
  `expire_time` int(11) DEFAULT NULL COMMENT '到期时间，特指OAuth2登录',
  `refresh_token` varchar(255) DEFAULT NULL COMMENT '第三方登录刷新token',
  PRIMARY KEY (`id`),
  UNIQUE KEY `identifier` (`identifier`) USING BTREE,
  KEY `status` (`status`) USING BTREE,
  KEY `idx_uid` (`uid`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COMMENT='用户授权表';

-- ----------------------------
-- Records of user_auth
-- ----------------------------
INSERT INTO `user_auth` VALUES ('1', 'fWYsBAWhL6sUrM8D7jAL6e', '2', 'staugur@vip.qq.com', 'pbkdf2:sha256:50000$JRmJt9NS$07ffc4c24899f8375b2b3964997a4cc00b5bafff5b7f4ff67eb8e61635a408d7', '1', '1', '1516075172', '0', null, null);
INSERT INTO `user_auth` VALUES ('2', '2XyKu82nFWoT9HUoKUwhVQ', '2', 'staugur@saintic.com', 'pbkdf2:sha256:50000$QEB9eHHW$419ff3357a2792e46564be9c978fb496cd50613ecfc3891dfb10f117c4d13ba3', '1', '1', '1516075478', '0', null, null);
INSERT INTO `user_auth` VALUES ('3', 'RH3XJVUizkQjyRCsvsCY7U', '2', '1663116375@qq.com', 'pbkdf2:sha256:50000$IIyRnV6n$68c380314e0f9a7a7aec58ac5d83c6e5c4ee8210be4e0157cf0ad319bd525765', '1', '1', '1516081249', '0', null, null);
INSERT INTO `user_auth` VALUES ('4', 'MCSki7q8VyhsJuLuMGKusj', '2', 'staugur@qq.com', 'pbkdf2:sha256:50000$Ru1nFYsW$d3b41ae24ff41b0c6aeb4edea113cb3e4bb80d9f8f0df1a2bb708f6bb5f1c005', '1', '1', '1516081679', '0', null, null);
INSERT INTO `user_auth` VALUES ('5', 'uw7JAzAV9MCz5zRQThV4tf', '2', 'staugur@foxmail.com', 'pbkdf2:sha256:50000$NgpNJydp$9138d04356f92a7716f8f6dc7eb7ffc58542e11a98dee68132813b663833a69f', '1', '1', '1516087910', '0', null, null);
INSERT INTO `user_auth` VALUES ('6', '7c4DWFyB4YASkSU5Ry2wri', '2', 'taochengwei@starokay.com', 'pbkdf2:sha256:50000$2fRb7MlN$d2a4d20dcc506e22bba7121620ec455660eeb808b756ee1b30ee5a93a658c9c8', '1', '1', '1516093470', '0', null, null);

-- ----------------------------
-- Table structure for user_loginlog
-- ----------------------------
DROP TABLE IF EXISTS `user_loginlog`;
CREATE TABLE `user_loginlog` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `uid` char(22) NOT NULL COMMENT '用户id',
  `login_type` tinyint(3) unsigned NOT NULL DEFAULT '1' COMMENT '登录类型 1手机号 2邮箱 3GitHub 4qq 5微信 6腾讯微博 7新浪微博',
  `login_ip` varchar(15) NOT NULL COMMENT '登录IP',
  `login_area` varchar(200) DEFAULT NULL COMMENT '登录地点',
  `login_time` char(19) NOT NULL COMMENT '登录时间',
  `user_agent` varchar(255) NOT NULL COMMENT '用户代理',
  `browser_type` varchar(10) CHARACTER SET utf8 DEFAULT NULL COMMENT '浏览器终端类型，入pc mobile bot tablet',
  `browser_device` varchar(30) CHARACTER SET utf8 DEFAULT NULL COMMENT '浏览器设备，如pc，xiaomi，iphone',
  `browser_os` varchar(30) CHARACTER SET utf8 DEFAULT NULL COMMENT '浏览器所在操作系统，如windows10，iPhone',
  `browser_family` varchar(30) CHARACTER SET utf8 DEFAULT NULL COMMENT '浏览器种类及版本，如chrome 60.0.3122',
  PRIMARY KEY (`id`),
  KEY `idx_uid_type_time` (`uid`,`login_type`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COMMENT='登录日志表';

-- ----------------------------
-- Records of user_loginlog
-- ----------------------------
INSERT INTO `user_loginlog` VALUES ('1', 'fWYsBAWhL6sUrM8D7jAL6e', '2', '127.0.0.1', '  内网IP 内网IP', '1516081790', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36', 'pc', 'PC', 'Windows 10', 'Chrome 63.0.3239');
INSERT INTO `user_loginlog` VALUES ('2', 'fWYsBAWhL6sUrM8D7jAL6e', '2', '127.0.0.1', '  内网IP 内网IP', '1516083514', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36', 'pc', 'PC', 'Windows 10', 'Chrome 63.0.3239');
INSERT INTO `user_loginlog` VALUES ('3', 'uw7JAzAV9MCz5zRQThV4tf', '2', '127.0.0.1', '  内网IP 内网IP', '1516088724', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36', 'pc', 'PC', 'Windows 10', 'Chrome 63.0.3239');
INSERT INTO `user_loginlog` VALUES ('4', 'fWYsBAWhL6sUrM8D7jAL6e', '2', '127.0.0.1', '  内网IP 内网IP', '1516090135', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36', 'pc', 'PC', 'Windows 10', 'Chrome 63.0.3239');
INSERT INTO `user_loginlog` VALUES ('5', '2XyKu82nFWoT9HUoKUwhVQ', '2', '127.0.0.1', '  内网IP 内网IP', '1516090400', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36', 'pc', 'PC', 'Windows 10', 'Chrome 63.0.3239');
INSERT INTO `user_loginlog` VALUES ('6', 'fWYsBAWhL6sUrM8D7jAL6e', '2', '127.0.0.1', '  内网IP 内网IP', '1516093174', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36', 'pc', 'PC', 'Windows 10', 'Chrome 63.0.3239');
INSERT INTO `user_loginlog` VALUES ('7', '7c4DWFyB4YASkSU5Ry2wri', '2', '127.0.0.1', '  内网IP 内网IP', '1516093479', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36', 'pc', 'PC', 'Windows 10', 'Chrome 63.0.3239');
INSERT INTO `user_loginlog` VALUES ('8', '7c4DWFyB4YASkSU5Ry2wri', '2', '127.0.0.1', '  内网IP 内网IP', '1516094184', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36', 'pc', 'PC', 'Windows 10', 'Chrome 63.0.3239');
INSERT INTO `user_loginlog` VALUES ('9', 'fWYsBAWhL6sUrM8D7jAL6e', '2', '127.0.0.1', '  内网IP 内网IP', '1516094198', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36', 'pc', 'PC', 'Windows 10', 'Chrome 63.0.3239');
INSERT INTO `user_loginlog` VALUES ('10', 'fWYsBAWhL6sUrM8D7jAL6e', '2', '127.0.0.1', '  内网IP 内网IP', '1516182464', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36', 'pc', 'PC', 'Windows 10', 'Chrome 63.0.3239');

-- ----------------------------
-- Table structure for user_profile
-- ----------------------------
DROP TABLE IF EXISTS `user_profile`;
CREATE TABLE `user_profile` (
  `uid` char(22) NOT NULL COMMENT '用户id',
  `register_source` tinyint(4) unsigned NOT NULL DEFAULT '0' COMMENT '注册来源：1手机号 2邮箱 3GitHub 4qq 5微信 6腾讯微博 7新浪微博',
  `register_ip` varchar(15) NOT NULL COMMENT '注册IP地址',
  `nick_name` varchar(32) DEFAULT '' COMMENT '用户昵称',
  `domain_name` varchar(32) DEFAULT '' COMMENT '个性域名',
  `gender` tinyint(1) unsigned DEFAULT '2' COMMENT '用户性别 0-女 1-男 2-保密',
  `birthday` bigint(20) unsigned DEFAULT '0' COMMENT '用户生日',
  `signature` varchar(140) DEFAULT '' COMMENT '用户个人签名',
  `avatar` varchar(255) DEFAULT '' COMMENT '头像',
  `curr_nation` varchar(10) DEFAULT NULL,
  `curr_province` varchar(10) DEFAULT NULL,
  `curr_city` varchar(10) DEFAULT NULL,
  `create_time` int(11) unsigned NOT NULL COMMENT '账号创建时间',
  `update_time` int(11) unsigned DEFAULT NULL COMMENT '账号修改时间',
  `is_realname` tinyint(1) unsigned NOT NULL DEFAULT '0' COMMENT '是否实名认证 0-未实名 1-已实名',
  `is_admin` tinyint(1) unsigned NOT NULL DEFAULT '0' COMMENT '是否管理员 0-否 1-是',
  `retain` varchar(255) DEFAULT NULL COMMENT '保留字段',
  PRIMARY KEY (`uid`),
  UNIQUE KEY `uid` (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户个人资料表';

-- ----------------------------
-- Records of user_profile
-- ----------------------------
INSERT INTO `user_profile` VALUES ('2XyKu82nFWoT9HUoKUwhVQ', '2', '127.0.0.1', '', '', '2', '0', '', '', null, null, null, '1516075478', null, '0', '0', null);
INSERT INTO `user_profile` VALUES ('7c4DWFyB4YASkSU5Ry2wri', '2', '127.0.0.1', '', '', '2', '0', '', '', null, null, null, '1516093470', null, '0', '0', null);
INSERT INTO `user_profile` VALUES ('fWYsBAWhL6sUrM8D7jAL6e', '2', '127.0.0.1', '', '', '2', '0', '', '', null, null, null, '1516075172', null, '0', '0', null);
INSERT INTO `user_profile` VALUES ('MCSki7q8VyhsJuLuMGKusj', '2', '127.0.0.1', '', '', '2', '0', '', '', null, null, null, '1516081679', null, '0', '0', null);
INSERT INTO `user_profile` VALUES ('RH3XJVUizkQjyRCsvsCY7U', '2', '127.0.0.1', '', '', '2', '0', '', '', null, null, null, '1516081249', null, '0', '0', null);
INSERT INTO `user_profile` VALUES ('uw7JAzAV9MCz5zRQThV4tf', '2', '127.0.0.1', '', '', '2', '0', '', '', null, null, null, '1516087910', null, '0', '0', null);
