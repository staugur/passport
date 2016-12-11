# -*- coding:utf8 -*-

import requests
from config import GLOBAL
from utils.tool import logger, mysql, md5

def UserAuth_Login(username, password):

    sql = " SELECT lauth_username, lauth_password FROM LAuth WHERE lauth_username=%s"
    data= mysql.get(sql, username)
    logger.debug("mysql data is %s, request %s:%s" %(data, username, md5(password)))
    if data and username == data.get("lauth_username") and md5(password) == data.get("lauth_password"):
        logger.info("%s Sign in successfully" %username)
        return True
    else:
        logger.info("%s Sign in failed" %username)
        return False

def UserAuth_Registry(kw):
    data = dict(
        username = kw.get("username"),
        password = kw.get("password"),
        email    = kw.get("email")
    )
    logger.info(data)
    res = requests.post(GLOBAL["ApiUrl"].strip("/") + "/user/?action=SignUp", data=data, timeout=5).json()
    logger.info(res)
