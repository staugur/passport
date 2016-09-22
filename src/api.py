# -*- coding:utf-8 -*-

import json
from config import GLOBAL, PRODUCT, MODULES
from libs.SessionConnection import RedisBaseApi
from utils import logger, gen_requestId, put2RedisSimple
from flask import Flask, request, g, redirect, jsonify
from flask_restful import Api, Resource
from threading import Thread

__author__  = 'Mr.tao <staugur@saintic.com>'
__doc__     = 'Authentication System for SaintIC Web Applications.'
__date__    = '2016-09-22'
__version__ = '0.0.1'
__process__ = PRODUCT.get('ProcessName', 'Auth')

app = Flask(__name__)
api = Api(app)

#每个URL请求之前，定义requestId并绑定到g.
@app.before_request
def before_request():
    g.requestId = gen_requestId()
    logger.info("Start Once Access, and this requestId is %s" % g.requestId)

#每次返回数据中，带上响应头，包含API版本和本次请求的requestId，以及允许所有域跨域访问API, 记录访问日志
@app.after_request
def add_header(response):
    response.headers["X-SaintIC-Request-Id"] = g.requestId
    response.headers["Access-Control-Allow-Origin"] = "*"
    logger.info(json.dumps({
        "AccessLog": {
            "status_code": response.status_code,
            "method": request.method,
            "ip": request.headers.get('X-Real-Ip', request.remote_addr),
            "url": request.url,
            "referer": request.headers.get('Referer'),
            "agent": request.headers.get("User-Agent"),
            "requestId": g.requestId,
            }
        }
    ))
    return response

#自定义错误显示信息，404错误和500错误
@app.errorhandler(404)
def not_found(error=None):
    message = {
        'status': 404,
        'message': 'Not Found: ' + request.url,
    }
    resp = jsonify(message)
    resp.status_code = 404
    return resp

#Define /, make it chcek or get
class Index(Resource):

    def get(self):
        return {__process__: "ok"}

#Define /registry, register and list applications
class Registry(Resource):

    def get(self):
        pass

    def post(self):
        """Get data frpm requests"""

        RegistryApplicationName     = request.form.get("application_name")
        RegistryApplicationPort     = request.form.get("application_port")
        RegistryApplicationLoglevel = request.form.get("application_loglevel")
        RegistryApplicationWanip    = request.form.get("application_wanip")
        RegistryApplicationLanip    = request.form.get("application_lanip")
        RegistryApplicationProtype  = request.form.get("application_protype")
        RegistryApplicationOther    = request.form.get("application_other")

        logger.info("Post Api, register application, open.")
        SessionType = MODULES.get('Session')['type']
        SessionHost = MODULES.get('Session')['host']
        SessionPort = MODULES.get('Session')['port']
        SessionPass = MODULES.get('Session')['pass']
        rc    = RedisBaseApi(SessionType, host=SessionHost, port=SessionPort, auth=SessionPass)
        key   = "%s.%s.%s:%s" %(GLOBAL.get("AppPrefix"), str(RegistryApplicationName), str(RegistryApplicationWanip), str(RegistryApplicationPort))
        value = "proc:%s, port:%s, wanIp:%s, lanIp:%s, loglevel:%s, proctype:%s" %(RegistryApplicationName, RegistryApplicationPort, RegistryApplicationWanip, RegistryApplicationLanip, RegistryApplicationLoglevel, RegistryApplicationProtype)
        logger.info("Post Api, register application, key is %s, value is %s" %(key, value))
        res   = put2RedisSimple(rc, key, value)
        logger.info("Post Api, register application, result is %s" %res)
        return res

#Router rules
api.add_resource(Index, '/', endpoint='index')
api.add_resource(Registry, '/registry', '/registry/', endpoint='registry')

if __name__ == '__main__':
    Host  = GLOBAL.get('Host')
    Port  = GLOBAL.get('Port')
    Debug = GLOBAL.get('Debug', True)
    app.run(host = Host, port = int(Port), debug = Debug)
