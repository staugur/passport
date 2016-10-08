# -*- coding:utf8 -*-

from utils.tool import logger, mysql, md5

def UserAuth_Login(username, password):

    sql = "SELECT username,password FROM user WHERE username=%s"
    data= mysql.get(sql, username)
    logger.debug("mysql data is %s, request %s:%s" %(data, username, md5(password)))
    if data and username == data.get("username") and md5(password) == data.get("password"):
        logger.info("%s Sign in successfully" %username)
        return True
    return False

def UserAuth_Registry(username, password):
    return False
