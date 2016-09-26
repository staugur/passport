# -*- coding:utf8 -*-

import os

#全局配置端
GLOBAL={

    "Host": os.environ.get("host", "0.0.0.0"),
    #Application run network address, you can set it `0.0.0.0`, `127.0.0.1`, ``;

    "Port": os.environ.get("port", 10030),
    #Application run port, default port;

    "Debug": os.environ.get("debug", True),
    #The development environment is open, the production environment is closed, which is also the default configuration.

    "LogLevel": os.environ.get("loglevel", "DEBUG"),
    #应用程序写日志级别，目前有DEBUG，INFO，WARNING，ERROR，CRITICAL

    "put2Redis": os.environ.get("put2redis", True),
    #是否开启put至redis的线程

    "ACL": ("Team.Front", "Team.Api"),
    #Access Control List, 访问控制列表, 限定只有ACL定义中的应用可以访问某些资源。

    "AppPrefix": "Auth.Registered.Application",
    #应用注册信息写入集群的前缀名

    "UserQueueKeyName": "user_authentication_mq"
}


#生产环境配置段
PRODUCT={

    "ProcessName": "Auth",
    #Custom process, you can see it with "ps aux|grep ProcessName".

    "ProductType": os.environ.get("producttype", "tornado"),
    #生产环境启动方法，可选`gevent`, `tornado`。
}


#模块配置项
MODULES={
    #指定应用会话存储集群，暂时支持redis、redis_cluster、etcd、memory(StringIO),
    "Session": {
        "type": "redis",

        "host": "101.200.125.9",

        "port": 1000,

        "pass": "SaintIC",
        #验证密码(目前仅支持单实例版redis)

        "db": 0
        #单实例版redis连接的库
    },

    #账号认证模块
    "Authentication": {
        "type": "mysql",
        #认证来源, 支持mysql表、LDAP、
        "Host": "101.200.125.9",

        "Port": 3306,

        "User": "root",

        "Passwd": "123456",

        "Database": "team",
        #数据库

        "Charset": "utf8",
        #字符集，默认国际统一标准utf8

        "Timezone": "+8:00",
        #时区，默认是东八区
    },

    #权限管理模块
    "Authority": None,
}
