# -*- coding: utf8 -*-

import json, base64, datetime
from flask import Flask, request, g, render_template, url_for, abort, make_response, redirect, jsonify
from flask_restful import Api, Resource
from config import GLOBAL, PRODUCT, MODULES
from apis.User import User_blueprint
from utils.tool import logger, gen_requestId, dms, md5
from libs.AuthenticationManager import UserAuth

__author__  = 'Mr.tao <staugur@saintic.com>'
__doc__     = 'Authentication System for SaintIC Web Applications.'
__date__    = '2016-09-22'
__org__     = 'SaintIC'
__version__ = '0.0.1'
__process__ = PRODUCT.get('ProcessName', 'Auth')

app   = Flask(__name__)
key   = GLOBAL.get("UserQueueKeyName", "user_authentication_mq")
auth  = UserAuth()

@app.before_request
def before_request():
    g.refererUrl= request.cookies.get("PageUrl") \
        if request.cookies.get("PageUrl") \
        and not "/auth" in request.cookies.get("PageUrl") \
        and not "favicon.ico" in request.cookies.get("PageUrl") \
        and not "robots.txt" in request.cookies.get("PageUrl") \
        and not "/logout" in request.cookies.get("PageUrl") \
        and not "index.js.map" in request.cookies.get("PageUrl") \
        and not "static" in request.cookies.get("PageUrl") \
        else url_for("index")
    logger.debug(g.refererUrl)
    g.requestId = gen_requestId()
    g.username  = request.cookies.get("username", "")
    g.sessionId = request.cookies.get("sessionId", "")
    g.password  = dms.hgetall(key).get(g.username) if g.username and g.sessionId else ""
    g.signin    = True if g.sessionId == md5(g.username + base64.decodestring(g.password)) else False
    logger.info("Start Once Access, this requestId is %s, signin:%s" %(g.requestId, g.signin))

@app.after_request
def after_request(response):
    response.headers["X-SaintIC-Request-Id"] = g.requestId
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.set_cookie(key="PageUrl", value=request.url, expires=None)
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

@app.route("/")
def index():
    return "index, " + str(g.signin) + "<a href='/login'> login </a>"

@app.route("/login/")
def login():
    if g.signin:
        return redirect(request.args.get('next', g.refererUrl))
    else:
        return render_template("login.html")

@app.route("/register/")
def register():
    if g.signin:
        return redirect(request.args.get('next', g.refererUrl))
    else:
        return render_template("register.html")

@app.route('/_auth/', methods=["POST", ])
def _auth():
    username = request.form.get("username")
    password = request.form.get("password")
    remember = request.form.get("remember")
    logger.debug(remember)
    if username and password and auth.login(username, password):
            expire_time = datetime.datetime.today() + datetime.timedelta(days=1)
            if dms.hset(key, username, base64.encodestring(password)):
                logger.info("Create a redis session key(%s) successfully." %username)
                resp = jsonify(loggedIn=True)
                #resp = make_response(redirect(request.args.get('next', g.refererUrl)))
                resp.set_cookie(key='logged_in', value="yes", expires=expire_time)
                resp.set_cookie(key='username',  value=username, expires=expire_time)
                resp.set_cookie(key='sessionId', value=md5(username + password), expires=expire_time)
            else:
                resp = jsonify(loggedIn=False)
                logger.warn("Create a redis session key(%s) failed." %username)
            return resp
    else:
        error = "Login fail, invaild username or password."
        return jsonify(loggedIn=False, error=error)
    
#register url rule(Blueprint), if get the result, please use app.url_map()
app.register_blueprint(User_blueprint, url_prefix="/api")

if __name__ == '__main__':
    Host  = GLOBAL.get('Host')
    Port  = GLOBAL.get('Port')
    Debug = GLOBAL.get('Debug', True)
    app.run(host = Host, port = int(Port), debug = Debug)
