# -*- coding: utf8 -*-
# 
# The SSO Api
#

from flask import Blueprint, request, jsonify, make_response
from flask_restful import Api, Resource
from utils.tool import logger, isLogged_in

class SSO_Api(Resource):

    def post(self):
        username  = request.form.get("username", "")
        sessionId = request.form.get("sessionId", "")
        expires   = request.form.get("time", "")
        signin    = isLogged_in('.'.join([ username, expires, sessionId ]))
        logger.info("CREATE SSO %s" %signin)
        return {"success": signin}

    def delete(self):
        username  = request.form.get("username", "")
        sessionId = request.form.get("sessionId", "")
        expires   = request.form.get("time", "")
        signin    = isLogged_in('.'.join([ username, expires, sessionId ]))
        logger.info("DELETE SSO %s" %signin)
        if signin:
            resp = make_response(jsonify(success=True))
            resp.set_cookie(key='logged_in', value='no', expires=None)
            resp.set_cookie(key='username',  value='', expires=0)
            resp.set_cookie(key='sessionId',  value='', expires=0)
            resp.set_cookie(key='Azone',  value='', expires=0)
            resp.set_cookie(key='time',  value='', expires=0)
        else:
            resp = make_response(jsonify(success=False))
        return resp

sso_blueprint = Blueprint(__name__, __name__)
sso_api = Api(sso_blueprint)
sso_api.add_resource(SSO_Api, '/sso', '/sso/', endpoint='api')