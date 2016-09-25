# -*- coding: utf8 -*-

__doc__ = "User login or registry rule map"

import time
import sys
reload(sys)
sys.setdefaultencoding('utf8')
from flask import Blueprint, request, url_for
from flask_restful import Api, Resource
from utils.tool import mysql, mail_check, logger, md5, chinese_check


class User(Resource):

    """
    Define /user, check login, registry, list user and so on, url is /user, /user/.

    1. #get:    Get user
    2. #post:   Create user, registry and login
    3. #put:    Update user profile
    4. #delete: Delete user
    """

    def get(self):
        """
        Public func, no token, with url args:
        1. num(int), The number of shows, the default is 10
        2. username|email, User name or email, database primary key, unique
        3. token, if true, display token info.

        Return data sample, {'msg':'success or error message', 'code':'result state', 'data':data}
        """
        #code - 1000~1010
        res = {"code": 0, "msg": None, "data": None}

        _num      = request.args.get('num', 10)
        _email    = request.args.get('email', None)
        _username = request.args.get('username', None)
        logger.info("num:%s, email:%s, username:%s" %(_num, _email, _username))

        #check parameters
        if not isinstance(_num, int):
            res.update(msg="num not a number", code=-1000)
        elif _email and not mail_check.match(_email):
            #check email format
            res.update(msg="email format error", code=-1001)
        else:
            #username's priority is greater than email
            if _username:
                sql = "SELECT username,email,cname,avatar,motto,url,time,extra FROM user WHERE username=%s"
                res.update(data=mysql.get(sql, _username))
                """
                emails=[ email.email for email in mysql.get("SELECT email FROM user") if email.email ]
                logger.debug({"The mysql emails": emails, "requestId": str(g.requestId)})
                if mail_check.match(_email) and _email in emails: #check email in mysql and format
                    sql="SELECT username,email,cname,avatar,motto,url,time,extra FROM user WHERE email='%s' LIMIT 1" % _email
                else:
                    res.update({"msg": "email format error or no such email", "code": 1001}) #code:1001, email format error or no email
                    logger.info(res)
                    return res
                """
            else:
                #url args no username and email, this is default sql and display
                sql = "SELECT username,email,cname,avatar,motto,url,time,extra FROM user LIMIT %s"
                res.update(data=mysql.query(sql, int(_num)))

        logger.info(res)
        return res

    def post(self):
        """
        1. login and registry, with query action=log/reg,

        2. post data:
            :: username,
            :: password,
            :: email, optional, without system login, if there will be regular inspection does not meet the format rebound request.
        """
        #code - 1011~1030
        res = {"msg": None, "code": 0, "success": False}

        username = request.form.get("username")
        password = request.form.get("password")
        email    = request.form.get("email")
        action   = request.args.get("action")

        if not username or not password:
            res.update(msg="Invaild username or password", code=-1011)
        else:
            if len(username) < 5 or len(password) < 5:
                res.update(msg="username or password length of at least 5", code=-1012)
            elif chinese_check.search(unicode(username)): #reload(sys), and set defaultencoding('utf8')
                res.update(msg="username can not contain Chinese", code=-1013)
            elif email and not mail_check.match(email):
                res.update(msg="email format error", code=-1014)
            elif not action in ("signup", "reg", "signin", "log"):
                res.update(msg="No action selected", code=-1015)
            else:
                password = md5(password)
                sql = "SELECT username,password FROM user WHERE username=%s"
                data= mysql.get(sql, username)
                logger.debug("mysql data is %s, request %s:%s" %(data, username, password))
                #Judgment and processing login or register
                if action in ("signup", "reg"):
                    if data:
                        res.update(msg="User already exists, cannot be registered!", code=-1016)
                    else:
                        mysql.insert("INSERT INTO user (username, password, email, time) VALUES(%s, %s, %s, %s)", username, password, email, time.strftime("%Y-%m-%d"))
                        if mysql.get(sql, username):
                            res.update(msg="Sign up failed", code=-1017)
                        else:
                            res.update(msg="Sign up success", code=-1018)
                else:
                    if data and username == data.get("username") and password == data.get("password"):
                        res.update(success=True)
                        logger.info("%s Sign in successfully" %username)
                    else:
                        res.update(msg="Sign in failed", code=-1019)

        logger.info(res)
        return res

    def delete(self):
        """delete user, with url args:
        1. token, must match username,
        2. username, must match token,
        And, operator must have administrator rights.
        """
        #from pub.config.BLOG import AdminGroup
        AdminGroup = config.BLOG.get('AdminGroup')
        res      = {"url": request.url, "msg": None, "data": None, "code": 200}
        token    = request.args.get('token', None)
        username = request.args.get('username', None)
        if not token:
            res.update({'msg': 'No token', "code": 1020}) #code:1020, 请求参数无token
            logger.warn(res)
            return res
        if not username:
            res.update({'msg': 'No username', "code": 1021}) #code:1021, 请求参数无username
            logger.warn(res)
            return res
        if not username in AdminGroup:
            res.update({'msg': 'The user does not have permission!', "code": 1022}) #code:1022, 请求的username不在配置文件的AdminGroup组，没有删除权限
            logger.error(res)
            return res

        ReqData  = dbUser(username, token=True)
        logger.debug({"User:delete:ReqData": ReqData})
        if ReqData:
            _DBtoken = ReqData.get('token')
            _DBuser  = ReqData.get('username')
            if _DBtoken != token:
                res.update({'msg': 'token miss match!', 'code': 1023}) #code:1023, 请求的token参数与数据库token值不匹配
                logger.error(res)
                return res
            sql = "DELETE FROM user WHERE username='%s'" % username
            logger.info({"User:delete:SQL": sql})
            try:
                if hasattr(mysql, 'delete'):
                    mysql.delete(sql)
                else:
                    mysql.execute(sql)
            except Exception, e:
                res.update({'code':1024, 'msg':'Delete user failed'}) #code:1024, delete user from mysql, it's error
                logger.error(res)
                return res
            else:
                res.update({'code':0, 'msg':'Delete success', 'data':{'delete username': username}}) #token match username, deleter ok
        else:
            res.update({'code': 1025, 'msg':'No found username'}) #code:1025, no such username in mysql.
        logger.info(res)
        return res

    def put(self):
        """Update user profile"""
        pass


User_blueprint = Blueprint(__name__, __name__)
#Bind API to the blueprint interface, and add this URL to the blueprint mapping rules
api = Api(User_blueprint)
api.add_resource(User, '/user', '/user/', endpoint='user')
