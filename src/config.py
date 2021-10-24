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
    # Application run network address, you can set it 0.0.0.0, 127.0.0.1.
    "Port": getenv("passport_port", 10030),
    # Application run port, default port.
    "LogLevel": getenv("passport_loglevel", "DEBUG"),
    # Application log level, DEBUG, INFO, WARNING, ERROR, CRITICAL.
}


MYSQL = getenv("passport_mysql_url")
# 必填-MYSQL数据库连接信息
# mysql://host:port:user:password:database?charset=&timezone=


REDIS = getenv("passport_redis_url")
# 必填-Redis数据库连接信息，格式：
# redis://[:password]@host:port/db
# host,port必填项,如有密码,记得密码前加冒号,默认localhost:6379/0


# picbed/sapic图床
PICBED = {
    "enable": getenv(
        "passport_picbed_enable", getenv("passport_sapic_enable", False)
    ),
    "api": getenv("passport_picbed_api", getenv("passport_sapic_api")),
    "LinkToken": getenv(
        "passport_picbed_linktoken", getenv("passport_sapic_linktoken")
    ),
}


# 又拍云存储配置
UPYUN = {
    "enable": getenv("passport_upyun_enable", False),
    "bucket": getenv("passport_upyun_bucket", ""),
    "username": getenv("passport_upyun_username", ""),
    "password": getenv("passport_upyun_password", ""),
    "dn": getenv("passport_upyun_dn", ""),
    "basedir": getenv("passport_upyun_basedir", "/passport"),
}


# 邮箱配置段：建议
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

# 发送短信配置段：建议
PHONE = {
    "ACCESS_KEY_ID": getenv("passport_phone_keyid"),
    # 阿里云api密钥key
    "ACCESS_KEY_SECRET": getenv("passport_phone_keysecret"),
    # 阿里云api密钥secret加密串
    "sign_name": getenv("passport_phone_sign_name"),
    # 阿里云短信签名名称
    "template_code": getenv("passport_phone_template_code")
    # 阿里云短信模版CODE
}

# 系统配置
SYSTEM = {
    "HMAC_SHA256_KEY": getenv(
        "passport_hmac_sha256_key", "273d32c8d797fa715190c7408ad73811"
    ),
    # hmac sha256 key
    "AES_CBC_KEY": getenv("passport_aes_cbc_key", "YRRGBRYQqrV1gv5A"),
    # utils.aes_cbc.CBC类中所用加密key
    "JWT_SECRET_KEY": getenv(
        "passport_jwt_secret_key", "WBlE7_#qDf2vRb@vM!Zw#lqrg@rdd3A6"
    ),
    # utils.jwt.JWTUtil类中所用加密key
    "Sign": {
        "version": getenv("passport_sign_version", "v1"),
        "accesskey_id": getenv("passport_sign_accesskeyid", "accesskey_id"),
        "accesskey_secret": getenv(
            "passport_sign_accesskeysecret", "accesskey_secret"
        ),
    },
    # utils.Signature.Signature类中所有签名配置
    "CACHE_ENABLE": {
        "UserAdmin": getenv("passport_cache_useradmin", True),
        # 开启管理员用户缓存
        "UserProfile": getenv("passport_cache_userprofile", True),
        # 开启用户资料缓存
        "UserApps": getenv("passport_cache_userapps", True),
        # 开启sso应用缓存
    },
    # 缓存启用项
    "PersonalizedDomainNamePrefix": getenv(
        "passport_personalizeddomainnameprefix", ""
    ),
    # 个性域名前缀：业务系统中用户对公个人主页前缀地址，此配置项在github.com/staugur/EauDouce程序中可以体现
    "SESSION_EXPIRE": int(getenv("passport_session_expire", 604800)),
    # session过期时间，单位秒，默认7d
    "EMAIL": getenv("passport_system_email", ""),
    # 意见反馈收件人
    "STATUS": getenv("passport_status_url", ""),
    # 服务状态地址
    "CASENUMBER": getenv("passport_casenumber")
    # 备案号
}


# 插件配置段
PLUGINS = {
    # 下面几个是第三方登录插件
    "weibo": {
        "ENABLE": getenv("passport_weibo_enable", False),
        "APP_ID": getenv("passport_weibo_appid"),
        "APP_KEY": getenv("passport_weibo_appkey"),
        "REDIRECT_URI": getenv(
            "passport_weibo_redirecturi",
            "https://passport.saintic.com/oauth2/weibo/authorized",
        ),
    },
    "qq": {
        "ENABLE": getenv("passport_qq_enable", False),
        "APP_ID": getenv("passport_qq_appid"),
        "APP_KEY": getenv("passport_qq_appkey"),
        "REDIRECT_URI": getenv(
            "passport_qq_redirecturi",
            "https://passport.saintic.com/oauth2/qq/authorized",
        ),
    },
    "github": {
        "ENABLE": getenv("passport_github_enable", False),
        "APP_ID": getenv("passport_github_appid"),
        "APP_KEY": getenv("passport_github_appkey"),
        "REDIRECT_URI": getenv(
            "passport_github_redirecturi",
            "https://passport.saintic.com/oauth2/github/authorized",
        ),
    },
    "coding": {
        "ENABLE": getenv("passport_coding_enable", False),
        "APP_ID": getenv("passport_coding_appid"),
        "APP_KEY": getenv("passport_coding_appkey"),
        "REDIRECT_URI": getenv(
            "passport_coding_redirecturi",
            "https://passport.saintic.com/oauth2/coding/authorized",
        ),
    },
    "gitee": {
        "ENABLE": getenv("passport_gitee_enable", False),
        "APP_ID": getenv("passport_gitee_appid"),
        "APP_KEY": getenv("passport_gitee_appkey"),
        "REDIRECT_URI": getenv(
            "passport_gitee_redirecturi",
            "https://passport.saintic.com/oauth2/gitee/authorized",
        ),
    },
    "AccessCount": getenv("passport_accesscount"),
    # 访问统计插件
}
