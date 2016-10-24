# Passport
Unified authentication and authorization management SSO system for SaintIC Org.


# LICENSE
MIT


## Environment
> 1. Python Version: 2.6, 2.7
> 2. Web Framework: Flask, Flask-RESTful
> 3. Required Modules:

```
Flask            基础WEB框架
Flask-RESTful    基础WEB框架构建RESTful HTTP API扩展
tornado          生产环境启动方式, WSGI
gevent           生产环境启动方式, WSGI
setproctitle     LinuxOS设定进程
SpliceURL        URL拼接分割叠加模块
requests         URL请求处理模块
torndb           数据库模块
MySQL-python     数据库模块
```


## Usage

```
1. Requirement:
    1.0 yum install -y gcc gcc-c++ python-devel libffi-devel openssl-devel mysql-devel
    1.1 pip install -r requirements.txt
    1.2 MySQL, 导入sql/passport.sql数据库文件

2. modify config.py or add environment variables(os.getenv key in the reference configuration item):
    2.1 修改GLOBAL全局配置项(主要是端口、日志级别)
    2.2 修改MODULES核心配置项账号认证模块的MYSQL信息
    2.3 修改PLUGINS插件配置项(主要是第三方登录)

3. run:
    3.1 python main.py        #开发模式
    3.2 sh Control.sh         #生产模式
    3.3 python -O Product.py  #生产模式，3.2中方式实际调用此脚本
    3.4 python super_debug.py #性能分析模式
```


## Usage for Docker

```
   cd misc ; docker build -f Dockerfile_gcc -t alpine:gcc .
   #上一步需时较长，你也可以使用构建好的镜像，修改Dockerfile，第一行设置成FROM registry.saintic.com/alpine-python:gcc
   cd .. ;   docker build -t passport .
   docker run -tdi --name passport --net=host --always=restart passport
   ps aux|grep Passport //查看进程
```


## Design
![Design][1]

[1]: ./misc/passport.png


## ChangeLog

**v0.0.1**

> 1. Local Auth for Login
> 2. QQ Login
> 3. Weibo Login
> 4. The third login as plugins
> 5. Fix the third plugins bug when login
> 6. Update user profile with qq, weibo when login
> 7. Unified account login is good.

**v0.0.2**

> 1. GitHub Login
> 2. User Center Page Update
> 3. SSO Define and Client(https://github.com/saintic/passport.client)

**v0.0.3**

> 1. uc 修复当weibo 或 github 无协议(http)时跳转问题
> 2. uc个人中心丰富信息，悬浮可见
> 3. login 增加使用某类型账号登录提示
> 4. update sql(gender)


**v1.0.0**

> 1. 基本SSO同步登录功能
