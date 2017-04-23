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

    "ACL": ("Team.Front", "Api", "Interest.blog", "passport.client", "Open", "Deployer", "fss", "SwarmOps", "Breezes", "BlueSky", "EauDouce"),
    #Access Control List, 访问控制列表, 限定只有ACL定义中的应用可以访问某些资源。

    "ApiUrl": os.getenv("passport_ApiUrl", "https://api.sainti.com"),
    #接口地址

    "Blog.Url": os.getenv("passport_Blog_Url", "https://www.saintic.com/"),
    #博客地址
}

PRODUCT={
    "ProcessName": "Passport",
    #Custom process, you can see it with "ps aux|grep ProcessName".

    "ProductType": "tornado",
    #生产环境启动方法，可选`gevent`, `tornado`。
}

MODULES={
    #账号认证模块
    "Authentication": os.getenv("passport_authentication", ""),

    #权限管理模块
    "Authority": None,
}

PLUGINS = {
    #Third party social account login plug-in, allowing developers to enable some of the third party application login.If disabled one, then the login page does not appear the corresponding third party login icon.
    "thirdLogin": {
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
            "APP_ID": '32d6eea53343476e62ac',
            "APP_KEY": "847b038ae547c41d0ba07f9641bef74309870224",
            "REDIRECT_URI": "https://passport.saintic.com/callback/github/"
        },
        "INSTAGRAM": {
            "ENABLE": False,
            "APP_ID": '05602bf1f7e648b89d50ea30d02dc295',
            "APP_KEY": "bcea24fd61434f78b9b28479e3ddcc75",
            "REDIRECT_URI": "https://passport.saintic.com/callback/instagram/"
        },
        "OSCHINA": {
            "ENABLE": False,
            "APP_ID": 'QCU8KM1DilI6KOh9St1M',
            "APP_KEY": "q5xjAxnuWvCgJVCeXNIp2Jgdi89dcfL8",
            "REDIRECT_URI": "https://passport.saintic.com/callback/oschina/"
        },        
    },
}
