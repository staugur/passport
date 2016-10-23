# -*- coding: utf8 -*-
# 
# The SSO Api
#

from flask import Blueprint, request
from flask_restful import Api, Resource
from utils.tool import logger, isLogged_in

class SSO_Api(Resource):

    def post(self):
        username  = request.form.get("username", "")
        sessionId = request.form.get("sessionId", "")
        expires   = request.form.get("time", "")
        signin    = isLogged_in('.'.join([ username, expires, sessionId ]))
        logger.info("Request SSO %s" %signin)
        return {"success": signin}

sso_blueprint = Blueprint(__name__, __name__)
sso_api = Api(sso_blueprint)
sso_api.add_resource(SSO_Api, '/sso', '/sso/', endpoint='api')