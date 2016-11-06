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
from config import PLUGINS
from urllib import urlencode


def QQ_Login_Page_State(code, QQ_APP_ID, QQ_APP_KEY, QQ_REDIRECT_URI, timeout=5, verify=False):
    ''' Authorization Code cannot repeat '''
    QQ_Access_Token_Url = Splice(scheme="https", domain="graph.qq.com", path="/oauth2.0/token", query={"grant_type": "authorization_code", "client_id": QQ_APP_ID, "client_secret": QQ_APP_KEY, "code": code, "state": "P.passport", "redirect_uri": QQ_REDIRECT_URI}).geturl
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
        refresh_token= data.get("refresh_token")

        '''Update some required parameters for OAuth2.0 API calls'''
        Update_Access_Token_Url = Splice(scheme="https", domain="graph.qq.com", path="/oauth2.0/token", query={"grant_type": "refresh_token", "client_id": QQ_APP_ID, "client_secret": QQ_APP_KEY, "refresh_token": refresh_token}).geturl
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

        getId  = Splice(scheme="https", domain="graph.qq.com", path="/oauth2.0/me", query={"access_token": access_token}).geturl
        data   = Callback_Returned_To_Dict(requests.get(getId, timeout=timeout, verify=verify).text)
        logger.debug(data)
        openid = data.get("openid")
        if openid:
            User_Info_Url = Splice(scheme="https", domain="graph.qq.com", path="/user/get_user_info", query={"access_token": access_token, "oauth_consumer_key": QQ_APP_ID, "openid": openid}).geturl
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
    Access_Token_Url = Splice(scheme="https", domain="api.weibo.com", path="/oauth2/access_token", query={"grant_type": "authorization_code", "client_id": WEIBO_APP_ID, "client_secret": WEIBO_APP_KEY, "code": code, "redirect_uri": WEIBO_REDIRECT_URI}).geturl
    data = requests.post(Access_Token_Url, timeout=timeout, verify=verify).json()
    if "access_token" in data:
        access_token  = data.get("access_token")
        expires_in    = data.get("expires_in")
        uid           = requests.get("https://api.weibo.com/2/account/get_uid.json?access_token=%s" %access_token, timeout=timeout, verify=verify).json().get("uid", data.get("uid"))
        User_Info_Url = Splice(scheme="https", domain="api.weibo.com", path="/2/users/show.json", query={"access_token": access_token, "uid": uid}).geturl
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
                UpdateUserSQL = "UPDATE User SET cname=%s, avatar=%s, weibo=%s, gender=%s, extra=%s WHERE username=%s"
                mysql.update(UpdateUserSQL, user_cname, user_avater, user_weibo, user_gender, user_extra, username)
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
    Access_Token_Url = Splice(scheme="https", domain="github.com", path="/login/oauth/access_token", query={"client_id": GITHUB_APP_ID, "client_secret": GITHUB_APP_KEY, "code": code, "redirect_uri": GITHUB_REDIRECT_URI}).geturl
    data = requests.post(Access_Token_Url, timeout=timeout, verify=verify).text
    data = Parse_Access_Token(data)

    if "access_token" in data:
        access_token  = data.get("access_token")
        User_Info_Url = Splice(scheme="https", domain="api.github.com", path="/user", query={"access_token": access_token}).geturl
        data          = requests.get(User_Info_Url, timeout=timeout, verify=verify).json()
        username      = "GitHub_" + data.get("login")
        user_id       = data.get("id")
        user_github   = data.get("html_url")
        user_cname    = data.get("name")
        user_avater   = data.get("avatar_url")
        user_email    = data.get("email")
        user_extra    = "blog:%s, company:%s, location:%s" %(data.get("blog"), data.get("company"), data.get("location"))
        try:
            UserSQL  = "INSERT INTO User (username, cname, email, avatar, time, github, extra) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            mysql.insert(UserSQL, username, user_cname, user_email, user_avater, How_Much_Time(), user_github, user_extra)
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
                UpdateUserSQL = "UPDATE User SET cname=%s, avatar=%s, extra=%s WHERE username=%s"
                mysql.update(UpdateUserSQL, user_cname, user_avater, user_extra, username)
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
        logger.debug(request.args)
        if g.signin:
            return redirect(url_for("uc"))
        elif code:
            SSOLoginURL = "%s?%s" %(PLUGINS['thirdLogin']['QQ']['REDIRECT_URI'], urlencode({"sso": request.args.get('sso'), "sso_r": request.args.get('sso_r'), "sso_p": request.args.get('sso_p'), "sso_t": request.args.get('sso_t')}))
            logger.debug(SSOLoginURL)
            data = QQ_Login_Page_State(code, PLUGINS['thirdLogin']['QQ']['APP_ID'], PLUGINS['thirdLogin']['QQ']['APP_KEY'], SSOLoginURL)
            if data:
                username    = data.get("username")
                expires_in  = int(data.get("expires_in"))
                openid      = data.get("openid")
                expire_time = How_Much_Time(expires_in) if expires_in else None

                resp = make_response(redirect(url_for("uc")))
                resp.set_cookie(key='logged_in', value="yes", max_age=expires_in)
                resp.set_cookie(key='username',  value=username, max_age=expires_in)
                resp.set_cookie(key='time', value=expire_time, max_age=expires_in)
                resp.set_cookie(key='Azone', value="QQ", max_age=expires_in)
                resp.set_cookie(key='sessionId', value=md5('%s-%s-%s-%s' %(username, openid, expire_time, "COOKIE_KEY")).upper(), max_age=expires_in)
                return resp
        else:
            return redirect(url_for("login"))

class Weibo_Callback_Page(Resource):

    def get(self):

        code = request.args.get("code")
        logger.debug(request.args)
        if g.signin:
            return redirect(url_for("uc"))
        elif code:
            data = Weibo_Login_Page_State(code, PLUGINS['thirdLogin']['WEIBO']['APP_ID'], PLUGINS['thirdLogin']['WEIBO']['APP_KEY'], PLUGINS['thirdLogin']['WEIBO']['REDIRECT_URI'])
            if data:
                username    = data.get("username")
                expires_in  = int(data.get("expires_in"))
                userid      = data.get("uid")
                expire_time = How_Much_Time(seconds=expires_in) if expires_in else None

                resp = make_response(redirect(url_for("uc")))
                resp.set_cookie(key='logged_in', value="yes", max_age=expires_in)
                resp.set_cookie(key='username',  value=username, max_age=expires_in)
                resp.set_cookie(key='time', value=expire_time, max_age=expires_in)
                resp.set_cookie(key='Azone', value="Weibo", max_age=expires_in)
                resp.set_cookie(key='sessionId', value=md5('%s-%s-%s-%s' %(username, userid, expire_time, "COOKIE_KEY")).upper(), max_age=expires_in)
                return resp
        else:
            return redirect(url_for("login"))

class GitHub_Callback_Page(Resource):

    def get(self):

        code = request.args.get("code")
        if g.signin:
            return redirect(url_for("uc"))
        elif code:
            data = GitHub_Login_Page_State(code, PLUGINS['thirdLogin']['GITHUB']['APP_ID'], PLUGINS['thirdLogin']['GITHUB']['APP_KEY'], PLUGINS['thirdLogin']['GITHUB']['REDIRECT_URI'])
            if data:
                username    = data.get("username")
                expires_in  = 3600 * 24 * 30
                userid      = data.get("uid")
                expire_time = How_Much_Time(seconds=expires_in) if expires_in else None

                resp = make_response(redirect(url_for("uc")))
                resp.set_cookie(key='logged_in', value="yes", max_age=expires_in)
                resp.set_cookie(key='username',  value=username, max_age=expires_in)
                resp.set_cookie(key='time', value=expire_time, max_age=expires_in)
                resp.set_cookie(key='Azone', value="GitHub", max_age=expires_in)
                resp.set_cookie(key='sessionId', value=md5('%s-%s-%s-%s' %(username, userid, expire_time, "COOKIE_KEY")).upper(), max_age=expires_in)
                return resp
        else:
            return redirect(url_for("login"))


callback_blueprint = Blueprint(__name__, __name__)
callback_page = Api(callback_blueprint)
callback_page.add_resource(QQ_Callback_Page, '/qq', '/qq/', endpoint='qq')
callback_page.add_resource(Weibo_Callback_Page, '/weibo', '/weibo/', endpoint='weibo')
callback_page.add_resource(GitHub_Callback_Page, '/github', '/github/', endpoint='github')
