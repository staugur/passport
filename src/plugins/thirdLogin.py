# -*- coding: utf8 -*-
#
# Web application with the third account login module
#

from flask import Blueprint, g, redirect, url_for
from flask_restful import Api, Resource
from SpliceURL import Splice
from utils.tool import logger, Parse_Access_Token, Callback_Returned_To_Dict, How_Much_Time
from config import PLUGINS


def QQ_Login_Page_Url(QQ_APP_ID, QQ_REDIRECT_URI):
    ''' Redirect QQ Landing Page URL '''
    return Splice(scheme="https", domain="graph.qq.com", path="/oauth2.0/authorize", query={"response_type": "code", "client_id": QQ_APP_ID, "redirect_uri": QQ_REDIRECT_URI, "scope": "get_user_info"}).geturl

def Weibo_Login_Page_Url(WEIBO_APP_ID, WEIBO_REDIRECT_URI):
    ''' Redirect Weibo Landing Page URL '''
    return Splice(scheme="https", domain="api.weibo.com", path="/oauth2/authorize", query={"response_type": "code", "client_id": WEIBO_APP_ID, "redirect_uri": WEIBO_REDIRECT_URI}).geturl

def GitHub_Login_Page_Url(GITHUB_APP_ID, GITHUB_REDIRECT_URI):
    ''' Redirect GitHub Landing Page URL '''
    return Splice(scheme="https", domain="github.com", path="/login/oauth/authorize", query={"client_id": GITHUB_APP_ID, "redirect_uri": GITHUB_REDIRECT_URI}).geturl

class QQ_Login_Page(Resource):

    def get(self):

        if g.signin:
            return redirect(url_for("uc"))
        else:
            if PLUGINS['thirdLogin']['QQ']['ENABLE']:
                return redirect(QQ_Login_Page_Url(PLUGINS['thirdLogin']['QQ']['APP_ID'], PLUGINS['thirdLogin']['QQ']['REDIRECT_URI']))
            else:
                return redirect(url_for("login"))

class Weibo_Login_Page(Resource):

    def get(self):

        if g.signin:
            return redirect(url_for("uc"))
        else:
            if PLUGINS['thirdLogin']['WEIBO']['ENABLE']:
                return redirect(Weibo_Login_Page_Url(PLUGINS['thirdLogin']['WEIBO']['APP_ID'], PLUGINS['thirdLogin']['WEIBO']['REDIRECT_URI']))
            else:
                return redirect(url_for("login"))

class GitHub_Login_Page(Resource):

    def get(self):

        if g.signin:
            return redirect(url_for("uc"))
        else:
            if PLUGINS['thirdLogin']['GITHUB']['ENABLE']:
                return redirect(GitHub_Login_Page_Url(PLUGINS['thirdLogin']['GITHUB']['APP_ID'], PLUGINS['thirdLogin']['GITHUB']['REDIRECT_URI']))
            else:
                return redirect(url_for("login"))


login_blueprint = Blueprint(__name__, __name__)
login_page = Api(login_blueprint)
login_page.add_resource(QQ_Login_Page, '/qq', '/qq/', endpoint='qq')
login_page.add_resource(Weibo_Login_Page, '/weibo', '/weibo/', endpoint='weibo')
login_page.add_resource(GitHub_Login_Page, '/github', '/github/', endpoint='github')
