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

    "STATIC_URL_ROOT": os.getenv("passport_static_url_root")
    #静态资源根地址，如果引用CDN等第三方css、js、image等文件，请填写资源域名，否则留空
}


# 邮箱配置段
EMAIL = {

    "useraddr": os.getenv("passport_email_useraddr"),
    # 邮箱用户：发件人

    "userpass": os.getenv("passport_email_userpass"),
    # 用户邮箱密码

    "smtpServer": os.getenv("passport_email_smtpserver"),
    # 邮箱服务器地址
}


MYSQL=os.getenv("passport_mysql_url")
#MYSQL数据库连接信息
#mysql://host:port:user:password:database?charset=&timezone=


REDIS=os.getenv("passport_redis_url")
#Redis数据库连接信息，格式：
#redis://[:password]@host:port/db
#host,port必填项,如有密码,记得密码前加冒号,默认localhost:6379/0

#插件配置段
PLUGINS={}