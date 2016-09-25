# -*- coding: utf8 -*-

import json
from flask import Flask, request, g, render_template, url_for
from flask_restful import Api, Resource
from config import GLOBAL, PRODUCT, MODULES
from utils.tool import logger, gen_requestId
from apis.User import User_blueprint

__author__  = 'Mr.tao <staugur@saintic.com>'
__doc__     = 'Authentication System for SaintIC Web Applications.'
__date__    = '2016-09-22'
__version__ = '0.0.1'
__process__ = PRODUCT.get('ProcessName', 'Auth')

app = Flask(__name__)

@app.before_request
def before_request():
    logger.debug(app.url_map)
    logger.debug(url_for("apis.User.user"))
    g.requestId = gen_requestId()
    logger.info("Start Once Access, and this requestId is %s" % g.requestId)

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

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

#register url rule, if get the result, please use app.url_map()
app.register_blueprint(User_blueprint)

if __name__ == '__main__':
    Host  = GLOBAL.get('Host')
    Port  = GLOBAL.get('Port')
    Debug = GLOBAL.get('Debug', True)
    app.run(host = Host, port = int(Port), debug = Debug)
