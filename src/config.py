# -*- coding: utf-8 -*-
"""
    passport.config
    ~~~~~~~~~~~~~~

    configure file

    :copyright: (c) 2017 by staugur.
    :license: MIT, see LICENSE for more details.
"""

from os import getenv

GLOBAL = {

    "ProcessName": "passport",
    # Custom process, you can see it with "ps aux|grep ProcessName".

    "Host": getenv("passport_host", "0.0.0.0"),
    # Application run network address, you can set it `0.0.0.0`, `127.0.0.1`, ``.

    "Port": getenv("passport_port", 10030),
    # Application run port, default port.

    "LogLevel": getenv("passport_loglevel", "DEBUG"),
    # Application to write the log level, currently has DEBUG, INFO, WARNING, ERROR, CRITICAL.
}


MYSQL = getenv("passport_mysql_url")
# MYSQL数据库连接信息
# mysql://host:port:user:password:database?charset=&timezone=


REDIS = getenv("passport_redis_url")
# Redis数据库连接信息，格式：
# redis://[:password]@host:port/db
# host,port必填项,如有密码,记得密码前加冒号,默认localhost:6379/0


# 手势验证码配置段
VAPTCHA = {

    "vid": getenv("passport_vaptcha_vid"),
    # 验证单元id

    "key": getenv("passport_vaptcha_key")
    # 验证单元key
}


# 又拍云存储配置
UPYUN = {
    "bucket": getenv("passport_upyun_bucket", ""),
    "username": getenv("passport_upyun_username", ""),
    "password": getenv("passport_upyun_password", ""),
    "dn": getenv("passport_upyun_dn", "https://img.saintic.com"),
    "basedir": getenv("passport_upyun_basedir", "/test")
}


# 邮箱配置段
EMAIL = {

    "useraddr": getenv("passport_email_useraddr"),
    # 邮箱用户：发件人

    "userpass": getenv("passport_email_userpass"),
    # 用户邮箱密码

    "smtpServer": getenv("passport_email_smtpserver"),
    # 邮箱服务器地址

    "smtpPort": getenv("passport_email_smtpport", 25),
    # 邮箱服务器端口

    "smtpSSL": getenv("passport_email_smtpssl", False)
    # 是否使用SSL加密
}


# 插件配置段
PLUGINS = {

    "weibo": {
        "ENABLE": getenv("passport_weibo_enable", True),
        "APP_ID": getenv("passport_weibo_appid"),
        "APP_KEY": getenv("passport_weibo_appkey"),
        "REDIRECT_URI": getenv("passport_weibo_redirecturi", "https://passport.saintic.com/oauth2/weibo/authorized")
    },
    "qq": {
        "ENABLE": getenv("passport_qq_enable", True),
        "APP_ID": getenv("passport_qq_appid"),
        "APP_KEY": getenv("passport_qq_appkey"),
        "REDIRECT_URI": getenv("passport_qq_redirecturi", "https://passport.saintic.com/oauth2/qq/authorized")
    },
    "github": {
        "ENABLE": getenv("passport_github_enable", True),
        "APP_ID": getenv("passport_github_appid"),
        "APP_KEY": getenv("passport_github_appkey"),
        "REDIRECT_URI": getenv("passport_github_redirecturi", "https://passport.saintic.com/oauth2/github/authorized")
    },
    "coding": {
        "ENABLE": getenv("passport_coding_enable", True),
        "APP_ID": getenv("passport_coding_appid"),
        "APP_KEY": getenv("passport_coding_appkey"),
        "REDIRECT_URI": getenv("passport_coding_redirecturi", "https://passport.saintic.com/oauth2/coding/authorized")
    },
    "gitee": {
        "ENABLE": getenv("passport_gitee_enable", True),
        "APP_ID": getenv("passport_gitee_appid"),
        "APP_KEY": getenv("passport_gitee_appkey"),
        "REDIRECT_URI": getenv("passport_gitee_redirecturi", "https://passport.saintic.com/oauth2/gitee/authorized")
    },
    "baidu": {
        "ENABLE": getenv("passport_baidu_enable", True),
        "APP_ID": getenv("passport_baidu_appid"),
        "APP_KEY": getenv("passport_baidu_appkey"),
        "REDIRECT_URI": getenv("passport_gitee_redirecturi", "https://passport.saintic.com/oauth2/baidu/authorized")
    },
}


# 系统配置
SYSTEM = {

    "HMAC_SHA256_KEY": getenv("passport_hmac_sha256_key", "273d32c8d797fa715190c7408ad73811"),
    # hmac sha256 key

    "AES_CBC_KEY": getenv("passport_aes_cbc_key", "YRRGBRYQqrV1gv5A"),
    # utils.aes_cbc.CBC类中所用加密key

    "JWT_SECRET_KEY": getenv("passport_jwt_secret_key", "WBlE7_#qDf2vRb@vM!Zw#lqrg@rdd3A6"),
    # utils.jwt.JWTUtil类中所用加密key

    "CACHE_ENABLE": {

        "UserAdmin": getenv("passport_cache_useradmin", True),
        # 开启管理员用户缓存

        "UserProfile": getenv("passport_cache_userprofile", True),
        # 开启用户资料缓存

        "UserApps": getenv("passport_cache_userapps", True),
        # 开启sso应用缓存
    },
    # 缓存启用项

    "PersonalizedDomainNamePrefix": "https://90era.vip/user/",
    # 个性域名前缀：业务系统中用户对公个人主页前缀地址

    "ApiSignature": {

        "ENABLE": False,
    }
}
