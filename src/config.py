# -*- coding: utf-8 -*-
"""
    passport.config
    ~~~~~~~~~~~~~~

    configure file

    :copyright: (c) 2017 by staugur.
    :license: MIT, see LICENSE for more details.
"""

import os

GLOBAL={

    "ProcessName": "passport",
    #Custom process, you can see it with "ps aux|grep ProcessName".

    "Host": os.getenv("passport_host", "0.0.0.0"),
    #Application run network address, you can set it `0.0.0.0`, `127.0.0.1`, ``.

    "Port": os.getenv("passport_port", 10030),
    #Application run port, default port.

    "LogLevel": os.getenv("passport_loglevel", "DEBUG"),
    #Application to write the log level, currently has DEBUG, INFO, WARNING, ERROR, CRITICAL.

    "STATIC_URL_ROOT": os.getenv("passport_static_url_root"),
    #静态资源根地址，如果引用CDN等第三方css、js、image等文件，请填写资源域名，否则留空

    "AES_CBC_KEY": os.getenv("passport_aes_cbc_key", "YRRGBRYQqrV1gv5A"),
    # utils.aes_cbc.CBC类中所用加密key

    "JWT_SECRET_KEY": os.getenv("passport_jwt_secret_key", "WBlE7_#qDf2vRb@vM!Zw#lqrg@rdd3A6")
    # utils.jwt.JWTUtil类中所用加密key
}

#手势验证码配置段
VAPTCHA = {
    "vid": os.getenv("passport_vaptcha_vid"),
    #验证单元id

    "key": os.getenv("passport_vaptcha_key")
    #验证单元key
}


# 邮箱配置段
EMAIL = {

    "useraddr": os.getenv("passport_email_useraddr"),
    # 邮箱用户：发件人

    "userpass": os.getenv("passport_email_userpass"),
    # 用户邮箱密码

    "smtpServer": os.getenv("passport_email_smtpserver"),
    # 邮箱服务器地址

    "smtpPort": os.getenv("passport_email_smtpport", 25),
    # 邮箱服务器端口

    "smtpSSL": os.getenv("passport_email_smtpssl", False)
    # 是否使用SSL加密
}


MYSQL=os.getenv("passport_mysql_url")
#MYSQL数据库连接信息
#mysql://host:port:user:password:database?charset=&timezone=


REDIS=os.getenv("passport_redis_url")
#Redis数据库连接信息，格式：
#redis://[:password]@host:port/db
#host,port必填项,如有密码,记得密码前加冒号,默认localhost:6379/0

#插件配置段
PLUGINS = {
    "WEIBO": {
        "ENABLE": True,
        "APP_ID": 1746902937,
        "APP_KEY": "8853e9ba5835e5a26fa0b4907c2995ce",
        "REDIRECT_URI": "https://passport.saintic.com/callback/weibo/"
    },
    "QQ": {
        "ENABLE": True,
        "APP_ID": 100581101,
        "APP_KEY": "36b4136a30a1bcd126525baf9e815f1f",
        "REDIRECT_URI": "https://passport.saintic.com/callback/qq/"
    },
    "GITHUB": {
        "ENABLE": True,
        "APP_ID": '02de0bef7a4f0c669ffd',
        "APP_KEY": "fa3cd1ce0269b40b40fd98f863a0a6a3c1fb3e83",
        "REDIRECT_URI": "http://passport.90era.vip/oauth2/github/authorized"
    },
}
