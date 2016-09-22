# -*- coding: utf8 -*-

__doc__ = "register application rule map"

from flask import Blueprint, request
from flask_restful import Api, Resource
from config import GLOBAL


class Registry(Resource):

    """Define /registry, register and list applications"""

    def get(self):
        pass

    def post(self):
        """Get data frpm requests"""

        RegistryApplicationName     = request.form.get("application_name")
        RegistryApplicationPort     = request.form.get("application_port")
        RegistryApplicationLoglevel = request.form.get("application_loglevel")
        RegistryApplicationWanip    = request.headers.get('X-Real-Ip', request.remote_addr)
        RegistryApplicationProtype  = request.form.get("application_protype")
        RegistryApplicationOther    = request.form.get("application_other")
        index = GLOBAL.get("AppPrefix")
        key   = RegistryApplicationName
        value = "port:%s, ip:%s, loglevel:%s, proctype:%s, other:%s" %(RegistryApplicationPort, RegistryApplicationWanip, RegistryApplicationLoglevel, RegistryApplicationProtype, RegistryApplicationOther)

        logger.info("Post Api, register application open: key is %s, value is %s" %(key, value))
        return {}
        SessionType = MODULES.get('Session')['type']
        SessionHost = MODULES.get('Session')['host']
        SessionPort = MODULES.get('Session')['port']
        SessionPass = MODULES.get('Session')['pass']
        rc    = RedisBaseApi(SessionType, host=SessionHost, port=SessionPort, auth=SessionPass)
        res   = put2RedisSimple(rc, key, value)
        logger.info("Post Api, register application, result is %s" %res)
        return res

application_registry_blueprint = Blueprint("Registry", __name__)
api = Api(application_registry_blueprint)
api.add_resource(Registry, '/registry', '/registry/', endpoint='registry')
