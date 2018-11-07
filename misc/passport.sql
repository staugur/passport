/*
Navicat MySQL Data Transfer

Date: 2018-08-08 17:39:09
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for sso_apps
-- ----------------------------
DROP TABLE IF EXISTS `sso_apps`;
CREATE TABLE `sso_apps` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(18) NOT NULL COMMENT '应用名称',
  `description` varchar(50) NOT NULL COMMENT '应用描述',
  `app_id` char(32) NOT NULL COMMENT '应用id',
  `app_secret` char(36) NOT NULL COMMENT '应用密钥',
  `app_redirect_url` varchar(255) NOT NULL COMMENT '应用回调根地址，即授权、注销前缀',
  `ctime` int(10) NOT NULL COMMENT '创建时间',
  `mtime` int(10) DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for user_auth
-- ----------------------------
DROP TABLE IF EXISTS `user_auth`;
CREATE TABLE `user_auth` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `uid` char(22) NOT NULL COMMENT '用户id',
  `identity_type` tinyint(2) unsigned NOT NULL COMMENT '0保留 1手机号 2邮箱 3GitHub 4qq 5微信 6谷歌 7新浪微博 8Coding 9码云',
  `identifier` varchar(50) NOT NULL DEFAULT '' COMMENT '手机号、邮箱或第三方应用的唯一标识(openid、union_id)',
  `certificate` varchar(106) NOT NULL DEFAULT '' COMMENT '密码凭证(站内的保存密码，站外的不保存或保存token)',
  `verified` tinyint(1) unsigned NOT NULL DEFAULT '0' COMMENT '是否已验证 0-未验证 1-已验证',
  `status` tinyint(1) unsigned NOT NULL DEFAULT '1' COMMENT '用户状态 0-禁用 1-启用',
  `ctime` int(11) unsigned NOT NULL DEFAULT '0' COMMENT '绑定时间',
  `mtime` int(11) unsigned DEFAULT '0' COMMENT '更新绑定时间',
  `etime` int(11) unsigned DEFAULT '0' COMMENT '到期时间，特指OAuth2登录',
  `refresh_token` varchar(255) DEFAULT '' COMMENT '第三方登录刷新token',
  PRIMARY KEY (`id`),
  UNIQUE KEY `identifier` (`identifier`) USING BTREE,
  KEY `status` (`status`) USING BTREE,
  KEY `idx_uid` (`uid`) USING BTREE,
  KEY `identity_type` (`identity_type`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COMMENT='用户授权表';

-- ----------------------------
-- Table structure for user_loginlog
-- ----------------------------
DROP TABLE IF EXISTS `user_loginlog`;
CREATE TABLE `user_loginlog` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `uid` char(22) NOT NULL COMMENT '用户id',
  `login_type` tinyint(2) unsigned NOT NULL DEFAULT '1' COMMENT '登录类型 同identity_type',
  `login_ip` varchar(15) NOT NULL COMMENT '登录IP',
  `login_area` varchar(200) DEFAULT NULL COMMENT '登录地点',
  `login_time` int(10) NOT NULL COMMENT '登录时间',
  `user_agent` varchar(255) NOT NULL COMMENT '用户代理',
  `browser_type` varchar(10) CHARACTER SET utf8 DEFAULT NULL COMMENT '浏览器终端类型，入pc mobile bot tablet',
  `browser_device` varchar(30) CHARACTER SET utf8 DEFAULT NULL COMMENT '浏览器设备，如pc，xiaomi，iphone',
  `browser_os` varchar(30) CHARACTER SET utf8 DEFAULT NULL COMMENT '浏览器所在操作系统，如windows10，iPhone',
  `browser_family` varchar(30) CHARACTER SET utf8 DEFAULT NULL COMMENT '浏览器种类及版本，如chrome 60.0.3122',
  PRIMARY KEY (`id`),
  KEY `idx_uid_type_time` (`uid`,`login_type`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COMMENT='登录日志表';

-- ----------------------------
-- Table structure for user_profile
-- ----------------------------
DROP TABLE IF EXISTS `user_profile`;
CREATE TABLE `user_profile` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '主键',
  `uid` char(22) NOT NULL COMMENT '用户id',
  `register_source` tinyint(2) unsigned NOT NULL DEFAULT '0' COMMENT '注册来源 同identity_type 不可更改',
  `register_ip` varchar(15) NOT NULL DEFAULT '' COMMENT '注册IP地址，不可更改',
  `nick_name` varchar(49) DEFAULT '' COMMENT '用户昵称',
  `domain_name` varchar(32) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '个性域名',
  `gender` tinyint(1) unsigned DEFAULT '2' COMMENT '用户性别 0-女 1-男 2-保密',
  `birthday` int(10) unsigned DEFAULT '0' COMMENT '用户生日时间戳',
  `signature` varchar(140) DEFAULT '' COMMENT '用户个人签名',
  `avatar` varchar(255) DEFAULT 'https://img.saintic.com/cdn/images/defaultAvatar.png' COMMENT '头像',
  `location` varchar(50) DEFAULT '' COMMENT '地址',
  `ctime` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '账号创建时间',
  `mtime` int(10) unsigned DEFAULT '0' COMMENT '资料修改时间',
  `is_realname` tinyint(1) unsigned NOT NULL DEFAULT '0' COMMENT '是否实名认证 0-未实名 1-已实名',
  `is_admin` tinyint(1) unsigned NOT NULL DEFAULT '0' COMMENT '是否管理员 0-否 1-是',
  `lock_nick_name` int(10) DEFAULT '1' COMMENT '昵称锁，10位有效时间戳内表示加锁，1表示无锁',
  `lock_domain_name` tinyint(1) DEFAULT '1' COMMENT '域名锁，0表示加锁 1表示无锁',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uid` (`uid`),
  UNIQUE KEY `dn` (`domain_name`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COMMENT='用户个人资料表';
