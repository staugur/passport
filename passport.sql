/*
Navicat MySQL Data Transfer

Source Server         : localhost
Source Server Version : 50720
Source Host           : localhost:3306
Source Database       : passport

Target Server Type    : MYSQL
Target Server Version : 50720
File Encoding         : 65001

Date: 2018-01-12 16:45:30
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for sys_clicklog
-- ----------------------------
DROP TABLE IF EXISTS `sys_clicklog`;
CREATE TABLE `sys_clicklog` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `url` varchar(255) NOT NULL COMMENT '访问地址',
  `user_agent` varchar(255) NOT NULL COMMENT '用户代理',
  `method` varchar(7) NOT NULL COMMENT '请求方法',
  `ip` varchar(15) NOT NULL COMMENT '客户端ip',
  `status_code` int(4) NOT NULL COMMENT '状态码',
  `referer` varchar(255) DEFAULT NULL COMMENT '来源',
  `click_time` int(11) NOT NULL COMMENT '点击时间',
  `browser_type` varchar(10) DEFAULT NULL COMMENT '浏览器终端类型，入pc mobile bot tablet',
  `browser_device` varchar(30) DEFAULT NULL COMMENT '浏览器设备，如pc，xiaomi，iphone',
  `browser_os` varchar(30) DEFAULT NULL COMMENT '浏览器所在操作系统，如windows10，iPhone',
  `browser_family` varchar(30) DEFAULT NULL COMMENT '浏览器种类及版本，如chrome 60.0.3122',
  PRIMARY KEY (`id`),
  KEY `uri_query` (`url`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='访问日志表';

-- ----------------------------
-- Table structure for user_auth
-- ----------------------------
DROP TABLE IF EXISTS `user_auth`;
CREATE TABLE `user_auth` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `uid` char(22) NOT NULL COMMENT '用户id',
  `identity_type` tinyint(4) unsigned NOT NULL COMMENT '1手机号 2邮箱 3GitHub 4qq 5微信 6腾讯微博 7新浪微博',
  `identifier` varchar(50) NOT NULL DEFAULT '' COMMENT '手机号、邮箱或第三方应用的唯一标识(openid、union_id)',
  `certificate` varchar(20) NOT NULL DEFAULT '' COMMENT '密码凭证(站内的保存密码，站外的不保存或保存token)',
  `method` char(5) NOT NULL COMMENT '登录方式 lauth: 系统用户; oauth: 第三方用户',
  `verified` tinyint(1) unsigned NOT NULL DEFAULT '0' COMMENT '是否已验证 0-未验证 1-已验证',
  `create_time` int(11) unsigned NOT NULL DEFAULT '0' COMMENT '绑定时间',
  `update_time` int(11) unsigned NOT NULL DEFAULT '0' COMMENT '更新绑定时间',
  `refresh_token` varchar(255) DEFAULT NULL COMMENT '第三方登录刷新token',
  PRIMARY KEY (`id`),
  UNIQUE KEY `only` (`uid`,`identifier`),
  KEY `idx_uid` (`uid`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户授权表';

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
  `status` tinyint(1) unsigned NOT NULL DEFAULT '1' COMMENT '用户状态 0-禁用 1-启用',
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
  UNIQUE KEY `uid` (`uid`),
  KEY `status` (`status`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户个人资料表';

-- ----------------------------
-- Table structure for user_loginlog
-- ----------------------------
DROP TABLE IF EXISTS `user_loginlog`;
CREATE TABLE `user_loginlog` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `uid` char(22) NOT NULL COMMENT '用户id',
  `login_type` tinyint(3) unsigned NOT NULL DEFAULT '1' COMMENT '登录类型 第三方/邮箱/手机等',
  `login_ip` varchar(15) NOT NULL COMMENT '登录IP',
  `login_area` varchar(200) DEFAULT NULL COMMENT '登录地点',
  `login_time` char(19) NOT NULL COMMENT '登录时间',
  `login_status` tinyint(1) unsigned NOT NULL DEFAULT '2' COMMENT '登录状态 1登录成功 0登录失败',
  `user_agent` varchar(255) NOT NULL COMMENT '用户代理',
  `device_id` varchar(32) DEFAULT '' COMMENT '登录时设备号',
  `browser_type` varchar(10) CHARACTER SET utf8 DEFAULT NULL COMMENT '浏览器终端类型，入pc mobile bot tablet',
  `browser_device` varchar(30) CHARACTER SET utf8 DEFAULT NULL COMMENT '浏览器设备，如pc，xiaomi，iphone',
  `browser_os` varchar(30) CHARACTER SET utf8 DEFAULT NULL COMMENT '浏览器所在操作系统，如windows10，iPhone',
  `browser_family` varchar(30) CHARACTER SET utf8 DEFAULT NULL COMMENT '浏览器种类及版本，如chrome 60.0.3122',
  PRIMARY KEY (`id`),
  KEY `idx_uid_type_time` (`uid`,`login_type`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='登录日志表';
