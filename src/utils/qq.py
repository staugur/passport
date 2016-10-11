# -*- coding: utf-8 -*-

import json
import requests
import datetime
from SpliceURL import Splice
from .tool import mysql, logger


class QQLogin:

    ''' Web application with qq login module '''

    timeout = 5
    verify  = False

    def __init__(self, QQ_APP_ID, QQ_APP_KEY, REDIRECT_URI):
        self.QQ_APP_ID    = QQ_APP_ID
        self.QQ_APP_KEY   = QQ_APP_KEY
        self.REDIRECT_URI = REDIRECT_URI



    def Parse_Access_Token(self, x):
        '''
        parse string, such as access_token=E8BF2BCAF63B7CE749796519F5C5D5EB&expires_in=7776000&refresh_token=30AF0BD336324575029492BD2D1E134B.
        return data, such as {'access_token': 'E8BF2BCAF63B7CE749796519F5C5D5EB', 'expires_in': '7776000', 'refresh_token': '30AF0BD336324575029492BD2D1E134B'}
        '''

        return dict( _.split('=') for _ in x.split('&') )

    def Callback_Returned_To_Dict(self, x):
        '''OAuthResponse class can't parse the JSON data with content-type text/html and because of a rubbish api, we can't just tell flask-oauthlib to treat it as json.'''

        logger.debug(x)

        if x.find(b'callback') > -1:
            # the rubbish api (https://graph.qq.com/oauth2.0/authorize) is handled here as special case
            pos_lb = x.find(b'{')
            pos_rb = x.find(b'}')
            x = x[pos_lb:pos_rb + 1]

        try:
            if type(x) != str:  # Py3k
                x = x.decode('utf-8')
            data = json.loads(x, encoding='utf-8')
        except:
            data = x

        logger.debug(type(data))
        logger.debug(data)
        if isinstance(data, dict):
            return data
        return json.loads(data)

    @property
    def QQ_Login_Page_Url(self):
        ''' Redirect QQ Landing Page URL '''
        return Splice(scheme="https", domain="graph.qq.com", path="/oauth2.0/authorize", query={"response_type": "code", "client_id": self.QQ_APP_ID, "redirect_uri": self.REDIRECT_URI, "scope": "get_user_info"}).geturl

    def Get_Access_Token(self, code):
        ''' Authorization Code cannot repeat '''
        Get_Access_Token_Url = Splice(scheme="https", domain="graph.qq.com", path="/oauth2.0/token", query={"grant_type": "authorization_code", "client_id": self.QQ_APP_ID, "client_secret": self.QQ_APP_KEY, "code": code, "state": "P.passport", "redirect_uri": self.REDIRECT_URI}).geturl
        access_token_data = requests.get(Get_Access_Token_Url, timeout=self.timeout, verify=self.verify).text

        try:
            data = self.Parse_Access_Token(access_token_data)
        except Exception,e:
            logger.error(e, exc_info=True)
            data = self.Callback_Returned_To_Dict(access_token_data)

        #Should returned right data, such as {'access_token': '79D493208A237BAB3C9AE93FAD2798CE', 'expires_in': '7776000', 'refresh_token': '30AF0BD336324575029492BD2D1E134B'}
        if isinstance(data, dict):
            access_token = data.get("access_token")
            expires_in   = data.get("expires_in")
            refresh_token= data.get("refresh_token")
            return self.Get_OpenID_to_MySQL(access_token, expires_in)
        else:
            logger.error("Get Access Token Error with Authorization Code")
            return False

    def Update_Access_Token(self, refresh_token):
        '''Update some required parameters for OAuth2.0 API calls'''
        Update_Access_Token_Url = Splice(scheme="https", domain="graph.qq.com", path="/oauth2.0/token", query={"grant_type": "refresh_token", "client_id": self.QQ_APP_ID, "client_secret": self.QQ_APP_KEY, "refresh_token": refresh_token}).geturl
        access_token_data = requests.get(Update_Access_Token_Url, timeout=self.timeout, verify=self.verify).text

        try:
            data = self.Parse_Access_Token(access_token_data)
        except Exception,e:
            logger.error(e, exc_info=True)
            data = self.Callback_Returned_To_Dict(access_token_data)

        #returned data, such as {'access_token': '79D493208A237BAB3C9AE93FAD2798CE', 'expires_in': '7776000', 'refresh_token': '30AF0BD336324575029492BD2D1E134B'}
        if isinstance(data, dict):
            return data
        else:
            logger.error("Update Access Token Error with refresh_token")
            return False

    def Get_OpenID_to_MySQL(self, access_token, expires_in):
        ''' Unique user ID '''

        Get_OpenID_Url = Splice(scheme="https", domain="graph.qq.com", path="/oauth2.0/me", query={"access_token": access_token}).geturl
        openid_data = requests.get(Get_OpenID_Url, timeout=self.timeout, verify=self.verify).text

        #Should returned right data, such as {"client_id":"100581101","openid":"AF8AA7E0F77451736DD97FB796849024"}
        data   = self.Callback_Returned_To_Dict(openid_data)
        openid = data.get("openid")
        if not openid: return False

        UserQzoneInfo = self.Get_User_Qzone_Info(access_token, openid)
        cname  = UserQzoneInfo.get("nickname")
        avatar =  UserQzoneInfo.get("figureurl_qq_1")
        sql = "INSERT INTO User (cname, avatar, time, extra) VALUES (%s, %s, %s, %s)"
        try:
            uid = int(mysql.insert(sql, cname, avatar, datetime.datetime.now().strftime("%Y-%m-%d"), "大家好，我是来自QQ的小伙伴！"))
        except Exception,e:
            logger.error(e, exc_info=True)
            return False
        else:
            logger.info("insert into User(%s)" %cname)
            expires = (datetime.datetime.now() + datetime.timedelta(seconds=int(expires_in))).strftime("%Y-%m-%d")
            logger.debug(expires)
            sql = "INSERT INTO OAuth (user_id, oauth_type, oauth_username, oauth_id, oauth_access_token, oauth_expires) VALUES (%s, %s, %s, %s, %s, %s)"
            mysql.insert(sql, uid, "QQ", "QQ_" + openid[:9], openid, access_token, expires)
            logger.info("insert into OAuth(%s)" %openid)
            return True

    def Get_User_Qzone_Info(self, access_token, openid):
        ''' With access_token and openid, access the qq api, get user resources '''
        Get_User_Info_Url = Splice(scheme="https", domain="graph.qq.com", path="/user/get_user_info", query={"access_token": access_token, "oauth_consumer_key": self.QQ_APP_ID, "openid": openid}).geturl
        return requests.get(Get_User_Info_Url, timeout=self.timeout, verify=self.verify).json()
