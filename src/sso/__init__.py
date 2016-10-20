# -*- coding: utf8 -*-
# 
# The callback blueprint for uniform landing and exit
#

from flask import Blueprint, g, redirect, url_for
from flask_restful import Api, Resource
from SpliceURL import Splice, Modify
from utils.tool import logger

class QQ_Login_Page(Resource):

    def get(self):

        return redirect(url_for("login"))

login_blueprint = Blueprint(__name__, __name__)
login_page = Api(login_blueprint)
login_page.add_resource(QQ_Login_Page, '/qq', '/qq/', endpoint='qq')
login_page.add_resource(Weibo_Login_Page, '/weibo', '/weibo/', endpoint='weibo')
