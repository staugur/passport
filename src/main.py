# -*- coding: utf8 -*-

import json, datetime
from config import GLOBAL, PLUGINS
from flask import Flask, request, g, render_template, url_for, abort, make_response, redirect, jsonify
from flask_restful import Api, Resource
from utils.tool import logger, gen_requestId, dms, md5, mysql, make_signed_cookie, parse_signed_cookie, isLogged_in, How_Much_Time
from libs.AuthenticationManager import UserAuth_Login
from callback import callback_blueprint
from plugins.thirdLogin import login_blueprint

__author__  = 'Mr.tao <staugur@saintic.com>'
__doc__     = 'SSO for SaintIC Web Applications.'
__date__    = '2016-09-22'
__org__     = 'SaintIC'
__version__ = '0.0.1'

app = Flask(__name__)

@app.before_request
def before_request():
    g.requestId = gen_requestId()
    g.username  = request.cookies.get("username", "")
    g.sessionId = request.cookies.get("sessionId", "")
    g.expires   = request.cookies.get("time", "")
    g.signin = isLogged_in('.'.join([ g.username, g.expires, g.sessionId ]))
    logger.info("Start Once Access, this requestId is %s, signin:%s" %(g.requestId, g.signin))

@app.after_request
def after_request(response):
    response.headers["X-SaintIC-Request-Id"] = g.requestId
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
    return "SaintiC SSO"

@app.route("/ucenter/")
def uc():
    if g.signin:
        sql = "SELECT cname, avatar, extra FROM User WHERE username=%s"
        data=mysql.get(sql, g.username)
        return """
        <html>
        <head>
        <title>SaintIC Passport User Center</title>
        </head>
        <body>
        <img src="%s" />
        <h1>%s</h1>
        <h2>%s</h2>
        <p><a href="%s">Logout</a></p>
        """ %(data.get("avatar"), data.get("cname"), data.get("extra"), url_for("logout"))
    else:
        return redirect(url_for("login"))

@app.route("/login/")
def login():
    if g.signin:
        return redirect(url_for("uc"))
    else:
        return render_template("login.html", enable_qq=PLUGINS['thirdLogin']['QQ']['ENABLE'], enable_weibo=PLUGINS['thirdLogin']['WEIBO']['ENABLE'])

@app.route("/logout/")
def logout():
    resp = make_response(redirect(url_for('login')))
    resp.set_cookie(key='logged_in', value='no', expires=None)
    resp.set_cookie(key='username',  value='', expires=0)
    resp.set_cookie(key='sessionId',  value='', expires=0)
    resp.set_cookie(key='Azone',  value='', expires=0)
    resp.set_cookie(key='time',  value='', expires=0)
    return resp

@app.route('/_auth/', methods=["POST", ])
def _auth():
    username = request.form.get("username")
    password = request.form.get("password")
    remember = 30 if request.form.get("remember") in ("True", "true", True) else None
    if username and password and UserAuth_Login(username, password):
            max_age_sec = 3600 * 24 * remember if remember else None
            expires     = How_Much_Time(max_age_sec)
            #expire_time= datetime.datetime.today() + datetime.timedelta(days=remember) if remember else None
            logger.debug("max_age_sec: %s, expire_time: %s, expires: %s" %(max_age_sec, None, expires))

            resp = make_response(redirect(url_for("uc")))
            resp.set_cookie(key='logged_in', value="yes", max_age=max_age_sec)
            resp.set_cookie(key='username',  value=username, max_age=max_age_sec)
            resp.set_cookie(key='sessionId', value=md5('%s-%s-%s-%s' %(username, md5(password), expires, "COOKIE_KEY")).upper(), max_age=max_age_sec)
            resp.set_cookie(key='time', value=expires, max_age=max_age_sec)
            #LogonCredentials: make_signed_cookie(username, md5(password), seconds=max_age_sec)
            #LogonCredentials: make_signed_cookie(username, openid/uid, seconds=max_age_sec)
            resp.set_cookie(key='Azone', value="local", max_age=max_age_sec)
            return resp
    else:
        return redirect(url_for("login"))

#register url rule(Blueprint), if get the result, please use app.url_map
app.register_blueprint(callback_blueprint, url_prefix="/callback")
app.register_blueprint(login_blueprint, url_prefix="/login")

if __name__ == '__main__':
    Host  = GLOBAL.get('Host')
    Port  = GLOBAL.get('Port')
    Debug = GLOBAL.get('Debug', True)
    app.run(host = Host, port = int(Port), debug = Debug)
