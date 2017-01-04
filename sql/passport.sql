/*
Navicat MySQL Data Transfer

Source Server         : 101.200.125.9-product
Source Server Version : 50520
Source Host           : 127.0.0.1:33306
Source Database       : saintic

Target Server Type    : MYSQL
Target Server Version : 50520
File Encoding         : 65001

Date: 2017-01-04 16:15:43
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
  `recommend` varchar(5) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT 'false',
  `top` varchar(5) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT 'false',
  PRIMARY KEY (`id`),
  KEY `id` (`id`,`create_time`,`tag`,`catalog`,`sources`,`author`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=217 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of blog
-- ----------------------------
INSERT INTO `blog` VALUES ('110', '版本更新记录', '           <p>           </p><p>           </p><p>           </p><p>           </p><blockquote><p>不知道该说些什么，本想着做个更新日志的页面，不过考虑下也用不到，因为，我更新的功能、修复的bug我都不记得了。。。</p></blockquote>\r\n        <p><b><font face=\"微软雅黑\" size=\"6\">Interest.blog</font></b></p><pre style=\"max-width: 100%;\"><code class=\"markdown hljs\" codemark=\"1\"><span class=\"hljs-strong\">**v0.1**</span>\r\n<span class=\"hljs-bullet\">1. </span>wangEditor富文本编辑器 上传图片上传博客 功能完成\r\n<span class=\"hljs-bullet\">2. </span>增加代码高亮插件、微博分享插件\r\n<span class=\"hljs-bullet\">3. </span>sso登录(passport)\r\n\r\n<span class=\"hljs-strong\">**v0.2**</span>\r\n<span class=\"hljs-bullet\">1. </span>用户个人中心\r\n\r\n<span class=\"hljs-strong\">**v0.3**</span>\r\n<span class=\"hljs-bullet\">1. </span>增加百度自动推送插件\r\n<span class=\"hljs-bullet\">2. </span>调整博客写作成功提交后跳转问题\r\n<span class=\"hljs-bullet\">3. </span>调整个人中心展现(头像、博客等)，徽章博客数量\r\n<span class=\"hljs-bullet\">4. </span>调整SSO登录\r\n<span class=\"hljs-bullet\">5. </span>增加多说评论插件\r\n<span class=\"hljs-bullet\">6. </span>增加个人中心天气显示插件\r\n<span class=\"hljs-bullet\">7. </span>修复SSO登录回调时cookie时间的bug\r\n<span class=\"hljs-bullet\">8. </span>导航中文化\r\n<span class=\"hljs-bullet\">9. </span>编辑文章功能,作者和admin可以编辑\r\n\r\n<span class=\"hljs-strong\">**v0.4**</span>\r\n<span class=\"hljs-bullet\">1. </span>修正了模板相关URL链接地址及meta信息\r\n<span class=\"hljs-bullet\">2. </span>增加了SSO同步注销\r\n<span class=\"hljs-bullet\">3. </span>修复任何人都可以通过GET拼接URL方式修改文章的bug\r\n<span class=\"hljs-bullet\">4. </span>博客详情页增加信息显示\r\n<span class=\"hljs-bullet\">5. </span>增加百度统计插件\r\n<span class=\"hljs-bullet\">6. </span>在README中更新了简单使用文档\r\n\r\n<span class=\"hljs-strong\">**v0.5**</span>\r\n<span class=\"hljs-bullet\">1. </span>优化了SSO登录\r\n<span class=\"hljs-bullet\">2. </span>点击数据记录到MySQL中\r\n<span class=\"hljs-bullet\">3. </span>调整了requirements.txt\r\n<span class=\"hljs-bullet\">4. </span>修复了SSO登录时不允许remember时的问题(登录在一次浏览器session有效)\r\n<span class=\"hljs-bullet\">5. </span>增加了admin后台蓝图，获取user、blog数据，User数据表增加isAdmin字段设置是否为管理员，管理员可在个人中心进入后台管理\r\n<span class=\"hljs-bullet\">6. </span>增加sitemap.xml\r\n<span class=\"hljs-bullet\">7. </span>增加百度社会化分享插件\r\n<span class=\"hljs-bullet\">8. </span>增加markdown富文本编辑器，使用开源软件Editor.md\r\n\r\n<span class=\"hljs-strong\">**v0.6**</span>\r\n<span class=\"hljs-bullet\">1. </span>增加更换头像功能\r\n<span class=\"hljs-bullet\">2. </span>调整个人中心别名、按钮样式、导航、写作页面等样式和展示\r\n<span class=\"hljs-bullet\">3. </span>调整sitema.xml策略，动态更新\r\n<span class=\"hljs-bullet\">4. </span>调整博客详情页相关tag、catalog、source到相关资源链接\r\n<span class=\"hljs-bullet\">5. </span>Dockerize\r\n<span class=\"hljs-bullet\">6. </span>上线“标签分类”导航，查询所有标签、目录、类型等资源下的博客\r\n<span class=\"hljs-bullet\">7. </span>去掉相应接口地址硬编码，改到配置文件(亦先读取环境变量)\r\n<span class=\"hljs-bullet\">8. </span>增加“返回顶部”功能\r\n<span class=\"hljs-bullet\">9. </span>增加外部搜索连接\r\n<span class=\"hljs-bullet\">10. </span>增加订阅更新功能\r\n<span class=\"hljs-bullet\">11. </span>增加修改个人资料功能\r\n\r\n<span class=\"hljs-strong\">**v1.0**</span>\r\n<span class=\"hljs-bullet\">1. </span>头像、博客等图片存储到又拍云\r\n\r\n<span class=\"hljs-strong\">**v1.1**</span>\r\n<span class=\"hljs-bullet\">1. </span>删除admin蓝图\r\n<span class=\"hljs-bullet\">2. </span>调整部分表单提示\r\n<span class=\"hljs-bullet\">3. </span>调整了整体架构，例如多说评论公共js中shortname改为读配置文件\r\n<span class=\"hljs-bullet\">4. </span>实现了markdown编辑器上传图片功能\r\n<span class=\"hljs-bullet\">6. </span>首页增加“最近更新”、“热评文章”、“推荐文章”、“置顶文章”等标签卡\r\n<span class=\"hljs-bullet\">7. </span>调整导航页，“更新记录、关于本站”的博客ID由配置文件指定\r\n<span class=\"hljs-bullet\">8. </span>增加圣诞节祝福插件\r\n<span class=\"hljs-bullet\">9. </span>增加360自动提交(实时)页面插件\r\n<span class=\"hljs-bullet\">10. </span>增加百度主动推送(实时)插件\r\n<span class=\"hljs-bullet\">11. </span>博客详情页增加设置/取消推荐/置顶文章(只允许admin操作)\r\n<span class=\"hljs-bullet\">12. </span>首页展示最新置顶文章\r\n</code></pre><p><b><font face=\"微软雅黑\" size=\"6\">Passport</font></b></p><pre style=\"max-width: 100%;\"><code class=\"markdown hljs\" codemark=\"1\"><span class=\"hljs-strong\">**v0.0.1**</span>\r\n\r\n<span class=\"hljs-quote\">&gt; 1. Local Auth for Login</span>\r\n<span class=\"hljs-quote\">&gt; 2. QQ Login</span>\r\n<span class=\"hljs-quote\">&gt; 3. Weibo Login</span>\r\n<span class=\"hljs-quote\">&gt; 4. The third login as plugins</span>\r\n<span class=\"hljs-quote\">&gt; 5. Fix the third plugins bug when login</span>\r\n<span class=\"hljs-quote\">&gt; 6. Update user profile with qq, weibo when login</span>\r\n<span class=\"hljs-quote\">&gt; 7. Unified account login is good.</span>\r\n\r\n<span class=\"hljs-strong\">**v0.0.2**</span>\r\n\r\n<span class=\"hljs-quote\">&gt; 1. GitHub Login</span>\r\n<span class=\"hljs-quote\">&gt; 2. User Center Page Update</span>\r\n<span class=\"hljs-quote\">&gt; 3. SSO Define and Client(https://github.com/saintic/passport.client)</span>\r\n\r\n<span class=\"hljs-strong\">**v0.0.3**</span>\r\n\r\n<span class=\"hljs-quote\">&gt; 1. uc 修复当weibo 或 github 无协议(http)时跳转问题</span>\r\n<span class=\"hljs-quote\">&gt; 2. uc个人中心丰富信息，悬浮可见</span>\r\n<span class=\"hljs-quote\">&gt; 3. login 增加使用某类型账号登录提示</span>\r\n<span class=\"hljs-quote\">&gt; 4. update sql(gender)</span>\r\n\r\n<span class=\"hljs-strong\">**v1.0.0**</span>\r\n\r\n<span class=\"hljs-quote\">&gt; 1. 基本SSO同步登录功能</span>\r\n\r\n<span class=\"hljs-strong\">**v1.0.1**</span>\r\n\r\n<span class=\"hljs-quote\">&gt; 1. ACL allow Interest.blog, Open</span>\r\n<span class=\"hljs-quote\">&gt; 2. 修复当本地登录失败时跳转没有携带query的问题</span>\r\n<span class=\"hljs-quote\">&gt; 3. QQ Weibo Github SSO同步完成</span>\r\n\r\n<span class=\"hljs-strong\">**v1.0.2**</span>\r\n\r\n<span class=\"hljs-quote\">&gt; 1. 修复SSO同步注销的一些问题</span>\r\n<span class=\"hljs-quote\">&gt; 2. 修复remember不选择时的None bug</span>\r\n<span class=\"hljs-quote\">&gt; 3. 更新了sql语句</span>\r\n<span class=\"hljs-quote\">&gt; 3. 第三方登录增加了instagram</span>\r\n<span class=\"hljs-quote\">&gt; 4. 调整当用户头像不为网络图片时，第三方登录不更新头像</span>\r\n<span class=\"hljs-quote\">&gt; 5. 增加uwsgi生产环境启动方式</span>\r\n<span class=\"hljs-quote\">&gt; 6. 删除了UC页，改为直接跳转到interest.blog个人中心页</span>\r\n<span class=\"hljs-quote\">&gt; 7. 增加用户注册功能</span></code></pre><p><br></p>', '2016-11-04', '2016-12-26', 'Interest.blog Passport', 'Interest.blog', '原创', 'admin', 'false', 'false');
INSERT INTO `blog` VALUES ('113', '关于我们', '           <p></p><p>           </p><h2><p><b>我是干什么的？</b></p><pre style=\"max-width: 100%;\"><code class=\"coffeescript hljs\" codemark=\"1\">SA，DevOpser</code></pre><p><b>这个站点为什么存在？</b></p><pre style=\"max-width: 100%;\"><code class=\"coffeescript hljs\" codemark=\"1\">记录技术点滴，开源项目源码，分享经验与技术。</code></pre><p><b>本站历程：</b></p><pre style=\"max-width: 100%;\"><code class=\"coffeescript hljs\" codemark=\"1\">Interest.blog之前，\r\n--&gt;最初的PHP(wordpress、emlog等)\r\n--&gt;GitHub Page\r\n--&gt;Python Flask(saintic/blog-&gt;saintic/Team/Front-&gt;Interest.blog)\r\n如果你有好的文章、想法、经验想与大家分享，或者文章有错误，请及时告诉我，欢迎投稿。</code></pre><p><b>如何联系我？</b></p><pre style=\"max-width: 100%;\"><code class=\"coffeescript hljs\" codemark=\"1\">如果还有问题想联系我？比如协同开发项目、谈谈人生聊聊理想啊，OK，我的邮箱是：staugur@saintic.com\r\n或者查看页脚部分的“邮我”按钮，给我们团队发邮件：<span style=\"font-size: 0.8em; color: rgb(17, 17, 17); font-family: &quot;Helvetica Neue&quot;, Helvetica, Arial, sans-serif;\">developers@saintic.com。</span></code></pre></h2><h2><p><b>Public：</b></p><pre style=\"max-width: 100%;\"><code class=\"coffeescript hljs\" codemark=\"1\">我的GitHub组织代码仓库是--&gt;&gt; https:<span class=\"hljs-regexp\">//gi</span>thub.com/saintic\r\n\r\n我的GitHub私人代码仓库是--&gt;&gt; https:<span class=\"hljs-regexp\">//gi</span>thub.com/staugur\r\n\r\n我的Docker仓库名是staugur--&gt;&gt; docker search staugur\r\n\r\n订阅本站最近更新的文章--&gt;&gt; <a href=\"http://www.saintic.com/blog/200.html\" target=\"_blank\" style=\"font-size: 0.8em; font-family: &quot;Helvetica Neue&quot;, Helvetica, Arial, sans-serif;\">http://www.saintic.com/blog/200.html</a></code></pre><p>另外如果你想砸死我，可以扫描下面的二维码试试：\r\n</p></h2><h2><img src=\"http://img.saintic.com/interest.blog/blog/5226820977404714.png\" alt=\"22-24-34-alipay\" class=\"\" style=\"font-size: 16px;\"><br></h2>', '2016-11-05', '2016-12-08', 'Interest.blog', 'Interest.blog', '原创', 'admin', 'false', 'false');

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
) ENGINE=InnoDB AUTO_INCREMENT=163419 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- ----------------------------
-- Records of clickLog
-- ----------------------------

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
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- ----------------------------
-- Records of LAuth
-- ----------------------------
INSERT INTO `LAuth` VALUES ('1', 'admin', '21232f297a57a5a743894a0e4a801fc3');

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
) ENGINE=InnoDB AUTO_INCREMENT=35 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

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
) ENGINE=InnoDB AUTO_INCREMENT=164 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- ----------------------------
-- Records of User
-- ----------------------------
INSERT INTO `User` VALUES ('1', 'admin', 'staugur@saintic.com', '管理员', '/static/img/avatar/default.jpg', 'Men always fight alone, always in the challenge of their own.', 'http://www.saintic.com', '2016-10-14', 'http://weibo.com/staugur', 'github.com/staugur', '男', 'Administrator', 'true');
