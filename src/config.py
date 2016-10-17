# -*- coding:utf8 -*-

import os

GLOBAL={

    "Host": os.getenv("passport_host", "0.0.0.0"),
    #Application run network address, you can set it `0.0.0.0`, `127.0.0.1`, ``;

    "Port": os.getenv("passport_port", 10030),
    #Application run port, default port;

    "Debug": os.getenv("passport_debug", True),
    #The development environment is open, the production environment is closed, which is also the default configuration.

    "LogLevel": os.getenv("passport_loglevel", "DEBUG"),
    #应用程序写日志级别，目前有DEBUG，INFO，WARNING，ERROR，CRITICAL

    "ACL": ("Team.Front", "Team.Api"),
    #Access Control List, 访问控制列表, 限定只有ACL定义中的应用可以访问某些资源。

    "UserQueueKey": "passport_user_authentication_mq_",

    "QQ_APP_ID": 100581101,

    "QQ_APP_KEY":  "36b4136a30a1bcd126525baf9e815f1f",

    "QQ_REDIRECT_URI": "https://passport.saintic.com/callback/qq/",

    "WEIBO_APP_ID":  1746902937,

    "WEIBO_APP_KEY": '8853e9ba5835e5a26fa0b4907c2995ce',

    "WEIBO_REDIRECT_URI": "https://passport.saintic.com/callback/weibo/",
}

PRODUCT={

    "ProcessName": "Passport",
    #Custom process, you can see it with "ps aux|grep ProcessName".

    "ProductType": os.getenv("passport_producttype", "tornado"),
    #生产环境启动方法，可选`gevent`, `tornado`。
}


MODULES={
    #指定应用会话存储集群，暂时支持redis、redis_cluster、etcd、memory(StringIO),
    "Session": {
        "type": "redis",

        "host": "101.200.125.9",

        "port": 16379,

        "pass": "SaintIC",
        #验证密码(目前仅支持单实例版redis)

        "db": 0
        #单实例版redis连接的库
    },

    #账号认证模块
    "Authentication": {
        "type": "mysql",
        #认证来源, 支持mysql表、LDAP、
        "Host": "127.0.0.1",

        "Port": 3306,

        "User": "root",

        "Passwd": "123456",

        "Database": "passport",
        #数据库

        "Charset": "utf8",
        #字符集，默认国际统一标准utf8

        "Timezone": "+8:00",
        #时区，默认是东八区
    },

    #权限管理模块
    "Authority": None,
}
