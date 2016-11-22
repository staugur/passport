# -*- coding: utf8 -*-
#
# The third login's callback bluerint
#

import requests
import datetime
from flask import Blueprint, request, g, redirect, url_for, make_response
from flask_restful import Api, Resource
from utils.tool import mysql, logger, How_Much_Time, Callback_Returned_To_Dict, Parse_Access_Token, md5, isLogged_in
from SpliceURL import Splice
from torndb import IntegrityError
from config import PLUGINS, GLOBAL
from urllib import urlencode


def QQ_Login_Page_State(code, QQ_APP_ID, QQ_APP_KEY, QQ_REDIRECT_URI, timeout=5, verify=False):
    ''' Authorization Code cannot repeat '''
    QQ_Access_Token_Url = Splice(scheme="https", netloc="graph.qq.com", path="/oauth2.0/token", query={"grant_type": "authorization_code", "client_id": QQ_APP_ID, "client_secret": QQ_APP_KEY, "code": code, "state": "P.passport", "redirect_uri": QQ_REDIRECT_URI}).geturl
    access_token_data = requests.get(QQ_Access_Token_Url, timeout=timeout, verify=verify).text

    try:
        data = Parse_Access_Token(access_token_data)
    except Exception,e:
        logger.error(e, exc_info=True)
        data = Callback_Returned_To_Dict(access_token_data)

    #Should returned right data, such as {'access_token': '79D493208A237BAB3C9AE93FAD2798CE', 'expires_in': '7776000', 'refresh_token': '30AF0BD336324575029492BD2D1E134B'}
    if "refresh_token" in data:
        #access_token = data.get("access_token")
        #expires_in   = data.get("expires_in")
        refresh_token = data.get("refresh_token")

        '''Update some required parameters for OAuth2.0 API calls'''
        Update_Access_Token_Url = Splice(scheme="https", netloc="graph.qq.com", path="/oauth2.0/token", query={"grant_type": "refresh_token", "client_id": QQ_APP_ID, "client_secret": QQ_APP_KEY, "refresh_token": refresh_token}).geturl
        access_token_data = requests.get(Update_Access_Token_Url, timeout=timeout, verify=verify).text

        try:
            data = Parse_Access_Token(access_token_data)
        except Exception,e:
            logger.error(e, exc_info=True)
            data = Callback_Returned_To_Dict(access_token_data)

        if "access_token" in data:
            access_token = data.get("access_token")
            expires_in   = data.get("expires_in")
        else:
            return False

        getId  = Splice(scheme="https", netloc="graph.qq.com", path="/oauth2.0/me", query={"access_token": access_token}).geturl
        data   = Callback_Returned_To_Dict(requests.get(getId, timeout=timeout, verify=verify).text)
        logger.debug(data)
        openid = data.get("openid")
        if openid:
            User_Info_Url = Splice(scheme="https", netloc="graph.qq.com", path="/user/get_user_info", query={"access_token": access_token, "oauth_consumer_key": QQ_APP_ID, "openid": openid}).geturl
            UserQzoneInfo = requests.get(User_Info_Url, timeout=timeout, verify=verify).json()
            username   = "QQ_" + openid[:9]
            user_extra = "%s %s" %(UserQzoneInfo.get("province"), UserQzoneInfo.get("city"))
            logger.info(UserQzoneInfo)
            try:
                UserSQL  = "INSERT INTO User (username, cname, avatar, time, gender, extra) VALUES (%s, %s, %s, %s, %s, %s)"
                mysql.insert(UserSQL, username, UserQzoneInfo.get("nickname"), UserQzoneInfo.get("figureurl_qq_1"), How_Much_Time(), UserQzoneInfo.get("gender"), user_extra)
                OAuthSQL = "INSERT INTO OAuth (oauth_username, oauth_type, oauth_openid, oauth_access_token, oauth_expires) VALUES (%s, %s, %s, %s, %s)"
                mysql.insert(OAuthSQL, username, "QQ", openid, access_token, How_Much_Time(seconds=int(expires_in)))
            except IntegrityError,e:
                logger.debug(e, exc_info=True)
                #Check if it has been registered
                CheckSQL = "SELECT oauth_username FROM OAuth WHERE oauth_username=%s"
                if mysql.get(CheckSQL, username):
                    UpdateSQL = "UPDATE OAuth SET oauth_access_token=%s, oauth_expires=%s WHERE oauth_username=%s"
                    mysql.update(UpdateSQL, access_token, How_Much_Time(seconds=int(expires_in)), username)
                    #update user profile
                    UpdateUserSQL = "UPDATE User SET cname=%s,gender=%s,extra=%s WHERE username=%s"
                    mysql.update(UpdateUserSQL, UserQzoneInfo.get("nickname"), UserQzoneInfo.get("gender"), user_extra, username)
                    return {"username": username, "expires_in": expires_in, "openid": openid}
            except Exception,e:
                logger.error(e, exc_info=True)
                return False
            else:
                logger.info("insert into User and OAuth, %s" %username)
                return {"username": username, "expires_in": expires_in, "openid": openid}
        else:
            return False
    else:
        logger.error("Get Access Token Error with Authorization Code in %s" %data)
        return False

def Weibo_Login_Page_State(code, WEIBO_APP_ID, WEIBO_APP_KEY, WEIBO_REDIRECT_URI, timeout=5, verify=False):
    ''' Authorization Code cannot repeat '''
    Access_Token_Url = Splice(scheme="https", netloc="api.weibo.com", path="/oauth2/access_token", query={"grant_type": "authorization_code", "client_id": WEIBO_APP_ID, "client_secret": WEIBO_APP_KEY, "code": code, "redirect_uri": WEIBO_REDIRECT_URI}).geturl
    data = requests.post(Access_Token_Url, timeout=timeout, verify=verify).json()
    if "access_token" in data:
        access_token  = data.get("access_token")
        expires_in    = data.get("expires_in")
        uid           = requests.get("https://api.weibo.com/2/account/get_uid.json?access_token=%s" %access_token, timeout=timeout, verify=verify).json().get("uid", data.get("uid"))
        User_Info_Url = Splice(scheme="https", netloc="api.weibo.com", path="/2/users/show.json", query={"access_token": access_token, "uid": uid}).geturl
        data          = requests.get(User_Info_Url, timeout=timeout, verify=verify).json()
        logger.debug(data)
        username      = "Weibo_" + access_token[4:13]
        user_cname    = data.get("screen_name")
        user_avater   = data.get("profile_image_url")
        user_weibo    = "http://weibo.com/" + data.get("profile_url")
        user_extra    = data.get("description")
        user_gender   = u"男" if data.get("gender") == "m" else u"女"
        try:
            UserSQL  = "INSERT INTO User (username, cname, avatar, time, weibo, gender, extra) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            mysql.insert(UserSQL, username, user_cname, user_avater, How_Much_Time(), user_weibo, user_gender, user_extra)
            OAuthSQL = "INSERT INTO OAuth (oauth_username, oauth_type, oauth_openid, oauth_access_token, oauth_expires) VALUES (%s, %s, %s, %s, %s)"
            mysql.insert(OAuthSQL, username, "Weibo", uid, access_token, How_Much_Time(seconds=int(expires_in)))
        except IntegrityError, e:
            logger.debug(e, exc_info=True)
            #Check if it has been registered
            CheckSQL = "SELECT oauth_username FROM OAuth WHERE oauth_username=%s"
            if mysql.get(CheckSQL, username):
                UpdateSQL = "UPDATE OAuth SET oauth_access_token=%s, oauth_expires=%s, oauth_openid=%s WHERE oauth_username=%s"
                mysql.update(UpdateSQL, access_token, How_Much_Time(seconds=int(expires_in)), uid, username)
                #update user profile
                if "http://" in user_avater or "https://" in user_avater:
                    UpdateUserSQL = "UPDATE User SET cname=%s, avatar=%s, weibo=%s, gender=%s, extra=%s WHERE username=%s"
                    mysql.update(UpdateUserSQL, user_cname, user_avater, user_weibo, user_gender, user_extra, username)
                else:
                    UpdateUserSQL = "UPDATE User SET cname=%s, weibo=%s, gender=%s, extra=%s WHERE username=%s"
                    mysql.update(UpdateUserSQL, user_cname, user_weibo, user_gender, user_extra, username)
                return {"username": username, "expires_in": expires_in, "uid": uid}
        except Exception,e:
            logger.error(e, exc_info=True)
            return False
        else:
            logger.info("insert into User and OAuth, %s" %username)
            return {"username": username, "expires_in": expires_in, "uid": uid}
    else:
        logger.error(data)
        return False

def GitHub_Login_Page_State(code, GITHUB_APP_ID, GITHUB_APP_KEY, GITHUB_REDIRECT_URI, timeout=5, verify=False):
    ''' Authorization Code cannot repeat '''
    Access_Token_Url = Splice(scheme="https", netloc="github.com", path="/login/oauth/access_token", query={"client_id": GITHUB_APP_ID, "client_secret": GITHUB_APP_KEY, "code": code, "redirect_uri": GITHUB_REDIRECT_URI}).geturl
    data = requests.post(Access_Token_Url, timeout=timeout, verify=verify).text
    data = Parse_Access_Token(data)

    if "access_token" in data:
        access_token  = data.get("access_token")
        User_Info_Url = Splice(scheme="https", netloc="api.github.com", path="/user", query={"access_token": access_token}).geturl
        data          = requests.get(User_Info_Url, timeout=timeout, verify=verify).json()
        username      = "GitHub_" + data.get("login")
        user_id       = data.get("id")
        user_github   = data.get("html_url")
        user_cname    = data.get("name")
        user_avater   = data.get("avatar_url")
        user_email    = data.get("email")
        user_url      = data.get("blog")
        user_extra    = "company:%s, location:%s" %(data.get("company"), data.get("location"))
        try:
            UserSQL  = "INSERT INTO User (username, cname, email, avatar, time, url, github, extra) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            mysql.insert(UserSQL, username, user_cname, user_email, user_avater, How_Much_Time(), user_url, user_github, user_extra)
            OAuthSQL = "INSERT INTO OAuth (oauth_username, oauth_type, oauth_openid, oauth_access_token, oauth_expires) VALUES (%s, %s, %s, %s, %s)"
            mysql.insert(OAuthSQL, username, "GitHub", user_id, access_token, How_Much_Time())
        except IntegrityError, e:
            logger.debug(e, exc_info=True)
            #Check if it has been registered
            CheckSQL = "SELECT oauth_username FROM OAuth WHERE oauth_username=%s"
            if mysql.get(CheckSQL, username):
                UpdateSQL = "UPDATE OAuth SET oauth_access_token=%s, oauth_expires=%s, oauth_openid=%s WHERE oauth_username=%s"
                mysql.update(UpdateSQL, access_token, How_Much_Time(), user_id, username)
                #update user profile
                if "http://" in user_avater or "https://" in user_avater:
                    UpdateUserSQL = "UPDATE User SET cname=%s, avatar=%s, url=%s, extra=%s WHERE username=%s"
                    mysql.update(UpdateUserSQL, user_cname, user_avater, user_url, user_extra, username)
                else:
                    UpdateUserSQL = "UPDATE User SET cname=%s, url=%s, extra=%s WHERE username=%s"
                    mysql.update(UpdateUserSQL, user_cname, user_url, user_extra, username)
                return {"username": username, "uid": user_id}
        except Exception,e:
            logger.error(e, exc_info=True)
            return False
        else:
            logger.info("insert into User and OAuth, %s" %username)
            return {"username": username, "uid": user_id}
    else:
        logger.error(data)
        return False

def Instagram_Login_Page_State(code, INSTAGRAM_APP_ID, INSTAGRAM_APP_KEY, INSTAGRAM_REDIRECT_URI, timeout=5, verify=False):
    ''' Authorization Code cannot repeat '''
    proxies = {
        "http": "http://101.200.125.9:7071",
        "https": "http://101.200.125.9:7071",
    }
    Access_Token_Url = Splice(scheme="https", netloc="api.instagram.com", path="/oauth/access_token", query={"client_id": INSTAGRAM_APP_ID, "client_secret": INSTAGRAM_APP_KEY, "code": code, "redirect_uri": INSTAGRAM_REDIRECT_URI, "grant_type": "authorization_code"}).geturl
    logger.debug(Access_Token_Url)
    data = requests.post(Access_Token_Url, timeout=timeout, verify=verify, proxies=proxies).json()

    if "access_token" in data:
        access_token  = data.get("access_token")
        data          = requests.get(User_Info_Url, timeout=timeout, verify=verify, proxies=proxies).json()
        User_Info_Url = Splice(scheme="https", netloc="api.instagram.com", path="/v1/users/self/", query={"access_token": access_token}).geturl
        data          = requests.get(User_Info_Url, timeout=timeout, verify=verify, proxies=proxies).json()
        username      = "Instagram_" + data.get("username")
        user_id       = data.get("id")
        user_cname    = data.get("full_name")
        user_avater   = data.get("profile_picture")
        user_url      = data.get("website")
        user_motto    = data.get("bio")
        user_extra    = data.get("counts")
        try:
            UserSQL  = "INSERT INTO User (username, cname, motto, avatar, time, url, extra) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            mysql.insert(UserSQL, username, user_cname, user_motto, user_avater, How_Much_Time(), user_url, user_extra)
            OAuthSQL = "INSERT INTO OAuth (oauth_username, oauth_type, oauth_openid, oauth_access_token, oauth_expires) VALUES (%s, %s, %s, %s, %s)"
            mysql.insert(OAuthSQL, username, "Instagram", user_id, access_token, How_Much_Time())
        except IntegrityError, e:
            logger.debug(e, exc_info=True)
            #Check if it has been registered
            CheckSQL = "SELECT oauth_username FROM OAuth WHERE oauth_username=%s"
            if mysql.get(CheckSQL, username):
                UpdateSQL = "UPDATE OAuth SET oauth_access_token=%s, oauth_expires=%s, oauth_openid=%s WHERE oauth_username=%s"
                mysql.update(UpdateSQL, access_token, How_Much_Time(), user_id, username)
                #update user profile
                if "http://" in user_avater or "https://" in user_avater:
                    UpdateUserSQL = "UPDATE User SET cname=%s, avatar=%s, url=%s, motto=%s, extra=%s WHERE username=%s"
                    mysql.update(UpdateUserSQL, user_cname, user_avater, user_url, user_motto, user_extra, username)
                else:
                    UpdateUserSQL = "UPDATE User SET cname=%s, url=%s, motto=%s, extra=%s WHERE username=%s"
                    mysql.update(UpdateUserSQL, user_cname, user_url, user_motto, user_extra, username)
                return {"username": username, "uid": user_id}
        except Exception,e:
            logger.error(e, exc_info=True)
            return False
        else:
            logger.info("insert into User and OAuth, %s" %username)
            return {"username": username, "uid": user_id}
    else:
        logger.error(data)
        return False

class QQ_Callback_Page(Resource):

    def get(self):

        code = request.args.get("code")
        SSORequest  = True if request.args.get("sso") in ("true", "True", True, "1", "on") else False
        SSOProject  = request.args.get("sso_p")
        SSORedirect = request.args.get("sso_r")
        SSOToken    = request.args.get("sso_t")
        SSOTokenMD5 = md5("%s:%s" %(SSOProject, SSORedirect))
        logger.debug(request.args)
        logger.debug(SSOTokenMD5==SSOToken)
        if g.signin:
            return redirect(url_for("uc"))
        elif code:
            SSOLoginURL = "%s?%s" %(PLUGINS['thirdLogin']['QQ']['REDIRECT_URI'], urlencode({"sso": SSORequest, "sso_r": SSORedirect, "sso_p": SSOProject, "sso_t": SSOToken}))
            logger.debug(SSOLoginURL)
            data = QQ_Login_Page_State(code, PLUGINS['thirdLogin']['QQ']['APP_ID'], PLUGINS['thirdLogin']['QQ']['APP_KEY'], SSOLoginURL)
            if data:
                username    = data.get("username")
                expires_in  = int(data.get("expires_in"))
                openid      = data.get("openid")
                expire_time = How_Much_Time(expires_in) if expires_in else None
                sessionId   = md5('%s-%s-%s-%s' %(username, openid, expire_time, "COOKIE_KEY")).upper()
                if SSOProject in GLOBAL.get("ACL") and SSORequest and SSORedirect and SSOTokenMD5 == SSOToken:
                    logger.info("RequestURL:%s, SSORequest:%s, SSOProject:%s, SSORedirect:%s" %(request.url, SSORequest, SSOProject, SSORedirect))
                    ticket    = '.'.join([ username, expire_time, sessionId ])
                    returnURL = SSORedirect + "?ticket=" + ticket
                    logger.info("SSO(%s) request project is in acl, will create a ticket, redirect to %s" %(SSOProject, returnURL))
                    resp = make_response(redirect(returnURL))
                else:
                    logger.info("Not SSO Auth, to QQ auth")
                    resp = make_response(redirect(url_for("uc")))
                resp.set_cookie(key='logged_in', value="yes", max_age=expires_in)
                resp.set_cookie(key='username',  value=username, max_age=expires_in)
                resp.set_cookie(key='time', value=expire_time, max_age=expires_in)
                resp.set_cookie(key='Azone', value="QQ", max_age=expires_in)
                resp.set_cookie(key='sessionId', value=sessionId, max_age=expires_in)
                return resp
        return redirect(url_for("login"))

class Weibo_Callback_Page(Resource):

    def get(self):

        code = request.args.get("code")
        SSORequest  = True if request.args.get("sso") in ("true", "True", True, "1", "on") else False
        SSOProject  = request.args.get("sso_p")
        SSORedirect = request.args.get("sso_r")
        SSOToken    = request.args.get("sso_t")
        SSOTokenMD5 = md5("%s:%s" %(SSOProject, SSORedirect))
        logger.debug(request.args)
        logger.debug(SSOTokenMD5==SSOToken)
        if g.signin:
            return redirect(url_for("uc"))
        elif code:
            SSOLoginURL = "%s?%s" %(PLUGINS['thirdLogin']['WEIBO']['REDIRECT_URI'], urlencode({"sso": SSORequest, "sso_r": SSORedirect, "sso_p": SSOProject, "sso_t": SSOToken}))
            logger.debug(SSOLoginURL)
            data = Weibo_Login_Page_State(code, PLUGINS['thirdLogin']['WEIBO']['APP_ID'], PLUGINS['thirdLogin']['WEIBO']['APP_KEY'], SSOLoginURL)
            if data:
                username    = data.get("username")
                expires_in  = int(data.get("expires_in"))
                userid      = data.get("uid")
                expire_time = How_Much_Time(seconds=expires_in) if expires_in else None
                sessionId   = md5('%s-%s-%s-%s' %(username, userid, expire_time, "COOKIE_KEY")).upper()
                if SSOProject in GLOBAL.get("ACL") and SSORequest and SSORedirect and SSOTokenMD5 == SSOToken:
                    logger.info("RequestURL:%s, SSORequest:%s, SSOProject:%s, SSORedirect:%s" %(request.url, SSORequest, SSOProject, SSORedirect))
                    ticket    = '.'.join([ username, expire_time, sessionId ])
                    returnURL = SSORedirect + "?ticket=" + ticket
                    logger.info("SSO(%s) request project is in acl, will create a ticket, redirect to %s" %(SSOProject, returnURL))
                    resp = make_response(redirect(returnURL))
                else:
                    logger.info("Not SSO Auth, to Weibo auth")
                    resp = make_response(redirect(url_for("uc")))
                resp.set_cookie(key='logged_in', value="yes", max_age=expires_in)
                resp.set_cookie(key='username',  value=username, max_age=expires_in)
                resp.set_cookie(key='time', value=expire_time, max_age=expires_in)
                resp.set_cookie(key='Azone', value="Weibo", max_age=expires_in)
                resp.set_cookie(key='sessionId', value=sessionId, max_age=expires_in)
                return resp
        return redirect(url_for("login"))

class GitHub_Callback_Page(Resource):

    def get(self):

        code = request.args.get("code")
        SSORequest  = True if request.args.get("sso") in ("true", "True", True, "1", "on") else False
        SSOProject  = request.args.get("sso_p")
        SSORedirect = request.args.get("sso_r")
        SSOToken    = request.args.get("sso_t")
        SSOTokenMD5 = md5("%s:%s" %(SSOProject, SSORedirect))
        logger.debug(request.args)
        logger.debug(SSOTokenMD5==SSOToken)
        if g.signin:
            return redirect(url_for("uc"))
        elif code:
            SSOLoginURL = "%s?%s" %(PLUGINS['thirdLogin']['GITHUB']['REDIRECT_URI'], urlencode({"sso": SSORequest, "sso_r": SSORedirect, "sso_p": SSOProject, "sso_t": SSOToken}))
            logger.debug(SSOLoginURL)
            data = GitHub_Login_Page_State(code, PLUGINS['thirdLogin']['GITHUB']['APP_ID'], PLUGINS['thirdLogin']['GITHUB']['APP_KEY'],SSOLoginURL)
            if data:
                username    = data.get("username")
                expires_in  = 3600 * 24 * 30
                userid      = data.get("uid")
                expire_time = How_Much_Time(seconds=expires_in) if expires_in else None
                sessionId   = md5('%s-%s-%s-%s' %(username, userid, expire_time, "COOKIE_KEY")).upper()
                if SSOProject in GLOBAL.get("ACL") and SSORequest and SSORedirect and SSOTokenMD5 == SSOToken:
                    logger.info("RequestURL:%s, SSORequest:%s, SSOProject:%s, SSORedirect:%s" %(request.url, SSORequest, SSOProject, SSORedirect))
                    ticket    = '.'.join([ username, expire_time, sessionId ])
                    returnURL = SSORedirect + "?ticket=" + ticket
                    logger.info("SSO(%s) request project is in acl, will create a ticket, redirect to %s" %(SSOProject, returnURL))
                    resp = make_response(redirect(returnURL))
                else:
                    logger.info("Not SSO Auth, to local auth")
                    resp = make_response(redirect(url_for("uc")))
                resp.set_cookie(key='logged_in', value="yes", max_age=expires_in)
                resp.set_cookie(key='username',  value=username, max_age=expires_in)
                resp.set_cookie(key='time', value=expire_time, max_age=expires_in)
                resp.set_cookie(key='Azone', value="GitHub", max_age=expires_in)
                resp.set_cookie(key='sessionId', value=sessionId, max_age=expires_in)
                return resp
        return redirect(url_for("login"))

class Instagram_Callback_Page(Resource):

    def get(self):

        code = request.args.get("code")
        SSORequest  = True if request.args.get("sso") in ("true", "True", True, "1", "on") else False
        SSOProject  = request.args.get("sso_p")
        SSORedirect = request.args.get("sso_r")
        SSOToken    = request.args.get("sso_t")
        SSOTokenMD5 = md5("%s:%s" %(SSOProject, SSORedirect))
        logger.debug(request.args)
        logger.debug(SSOTokenMD5==SSOToken)
        if g.signin:
            return redirect(url_for("uc"))
        elif code:
            SSOLoginURL = "%s?%s" %(PLUGINS['thirdLogin']['INSTAGRAM']['REDIRECT_URI'], urlencode({"sso": SSORequest, "sso_r": SSORedirect, "sso_p": SSOProject, "sso_t": SSOToken}))
            logger.debug(SSOLoginURL)
            data = Instagram_Login_Page_State(code, PLUGINS['thirdLogin']['INSTAGRAM']['APP_ID'], PLUGINS['thirdLogin']['INSTAGRAM']['APP_KEY'], SSOLoginURL)
            if data:
                username    = data.get("username")
                expires_in  = 3600 * 24 * 30
                userid      = data.get("uid")
                expire_time = How_Much_Time(seconds=expires_in) if expires_in else None
                sessionId   = md5('%s-%s-%s-%s' %(username, userid, expire_time, "COOKIE_KEY")).upper()
                if SSOProject in GLOBAL.get("ACL") and SSORequest and SSORedirect and SSOTokenMD5 == SSOToken:
                    logger.info("RequestURL:%s, SSORequest:%s, SSOProject:%s, SSORedirect:%s" %(request.url, SSORequest, SSOProject, SSORedirect))
                    ticket    = '.'.join([ username, expire_time, sessionId ])
                    returnURL = SSORedirect + "?ticket=" + ticket
                    logger.info("SSO(%s) request project is in acl, will create a ticket, redirect to %s" %(SSOProject, returnURL))
                    resp = make_response(redirect(returnURL))
                else:
                    logger.info("Not SSO Auth, to local auth")
                    resp = make_response(redirect(url_for("uc")))
                resp.set_cookie(key='logged_in', value="yes", max_age=expires_in)
                resp.set_cookie(key='username',  value=username, max_age=expires_in)
                resp.set_cookie(key='time', value=expire_time, max_age=expires_in)
                resp.set_cookie(key='Azone', value="Instagram", max_age=expires_in)
                resp.set_cookie(key='sessionId', value=sessionId, max_age=expires_in)
                return resp
        return redirect(url_for("login"))

callback_blueprint = Blueprint(__name__, __name__)
callback_page = Api(callback_blueprint)
callback_page.add_resource(QQ_Callback_Page, '/qq', '/qq/', endpoint='qq')
callback_page.add_resource(Weibo_Callback_Page, '/weibo', '/weibo/', endpoint='weibo')
callback_page.add_resource(GitHub_Callback_Page, '/github', '/github/', endpoint='github')
callback_page.add_resource(Instagram_Callback_Page, '/instagram', '/instagram/', endpoint='instagram')
