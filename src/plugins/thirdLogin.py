# -*- coding: utf-8 -*-
#
# Web application with the third account login module
#

import os
import json
import requests
from flask import Blueprint, g, redirect, url_for
from flask_restful import Api, Resource
from SpliceURL import Splice
from utils.tool import logger, Parse_Access_Token, Callback_Returned_To_Dict, How_Much_Time
from config import PLUGINS

'''
QQ_APP_ID          = GLOBAL['QQ_APP_ID']
QQ_APP_KEY         = GLOBAL['QQ_APP_KEY']
QQ_REDIRECT_URI    = GLOBAL['QQ_REDIRECT_URI']
WEIBO_APP_ID       = GLOBAL['WEIBO_APP_ID']
WEIBO_APP_KEY      = GLOBAL['WEIBO_APP_KEY']
WEIBO_REDIRECT_URI = GLOBAL['WEIBO_REDIRECT_URI']
'''
thirdLoginPlugins  = PLUGINS['thirdLogin']


def QQ_Login_Page_Url(QQ_APP_ID, QQ_REDIRECT_URI):
    ''' Redirect QQ Landing Page URL '''
    return Splice(scheme="https", domain="graph.qq.com", path="/oauth2.0/authorize", query={"response_type": "code", "client_id": QQ_APP_ID, "redirect_uri": QQ_REDIRECT_URI, "scope": "get_user_info"}).geturl

def Weibo_Login_Page_Url(WEIBO_APP_ID, WEIBO_REDIRECT_URI):
    ''' Redirect Weibo Landing Page URL '''
    return Splice(scheme="https", domain="api.weibo.com", path="/oauth2/authorize", query={"response_type": "code", "client_id": WEIBO_APP_ID, "redirect_uri": WEIBO_REDIRECT_URI}).geturl


class QQ_Login_Page(Resource):

    def get(self):

        if g.signin:
            return redirect(url_for("uc"))
        else:
            if thirdLoginPlugins['QQ']['ENABLE']:
                return redirect(QQ_Login_Page_Url(thirdLoginPlugins['QQ']['APP_ID'], thirdLoginPlugins['QQ']['REDIRECT_URI']))
            else:
                return redirect(url_for("login"))

class Weibo_Login_Page(Resource):

    def get(self):

        if g.signin:
            return redirect(url_for("uc"))
        else:
            if thirdLoginPlugins['WEIBO']['ENABLE']:
                return redirect(Weibo_Login_Page_Url(thirdLoginPlugins['WEIBO']['APP_ID'], thirdLoginPlugins['WEIBO']['REDIRECT_URI']))
            else:
                return redirect(url_for("login"))

login_blueprint = Blueprint(__name__, __name__)
login_page = Api(login_blueprint)
login_page.add_resource(QQ_Login_Page, '/qq', '/qq/', endpoint='qq')
login_page.add_resource(Weibo_Login_Page, '/weibo', '/weibo/', endpoint='weibo')
