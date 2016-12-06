# -*- coding: utf8 -*-

import json
import datetime
from flask import Flask, request, g, render_template, url_for, abort, make_response, redirect
from config import GLOBAL, PLUGINS
from utils.tool import logger, gen_requestId, md5, mysql, isLogged_in, How_Much_Time
from libs.AuthenticationManager import UserAuth_Login
from plugins.thirdLogin import login_blueprint
from callback import callback_blueprint
from sso import sso_blueprint

__author__  = 'Mr.tao <staugur@saintic.com>'
__doc__     = 'Unified authentication and single sign on system for SaintIC web applications.'
__date__    = '2016-11-01'
__org__     = 'SaintIC'
__version__ = '1.0.2'

app = Flask(__name__)
#register url rule(Blueprint), if get the result, please use app.url_map
app.register_blueprint(callback_blueprint, url_prefix="/callback")
app.register_blueprint(login_blueprint, url_prefix="/login")
app.register_blueprint(sso_blueprint)

@app.before_request
def before_request():
    g.requestId = gen_requestId()
    g.username  = request.cookies.get("username", "")
    g.sessionId = request.cookies.get("sessionId", "")
    g.expires   = request.cookies.get("time", "")
    g.credential= '.'.join([ g.username, g.expires, g.sessionId ])
    g.signin    = isLogged_in(g.credential)
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
    return """<h1> 404 Not Found Page!</h1>
    <p>I am sorry to inform you that I have not found this page in our system. Please return to the <a href="%s">home page.</a></p>
    """ % url_for("index"), 404

@app.route("/")
def index():
    return redirect(url_for("login"))

@app.route("/ucenter/")
def uc():
    if g.signin:
        return redirect("https://www.saintic.com/home/")
        return "SaintIC User Center"
    else:
        return redirect(url_for("login"))

@app.route("/login/", methods=["POST", "GET"])
def login():
    SSORequest  = True if request.args.get("sso") in ("true", "True", True, "1", "on") else False
    SSOProject  = request.args.get("sso_p")
    SSORedirect = request.args.get("sso_r")
    SSOToken    = request.args.get("sso_t")
    SSOTokenMD5 = md5("%s:%s" %(SSOProject, SSORedirect))
    logger.debug(request.args)
    logger.debug("remember: %s" %request.form)
    logger.debug(SSOTokenMD5==SSOToken)
    if g.signin:
        if SSOProject in GLOBAL.get("ACL") and SSORequest and SSORedirect and SSOTokenMD5 == SSOToken:
            returnURL = SSORedirect + "?ticket=" + g.credential
            logger.info("SSO(%s) request project is in acl, already landing, redirect to %s" %(SSOProject, returnURL))
            return redirect(returnURL)
        else:
            return redirect(url_for("uc"))
    else:
        if request.method == "GET":
            return render_template("signin.html", enable_qq=PLUGINS['thirdLogin']['QQ']['ENABLE'], enable_weibo=PLUGINS['thirdLogin']['WEIBO']['ENABLE'], enable_github=PLUGINS['thirdLogin']['GITHUB']['ENABLE'], enable_instagram=PLUGINS['thirdLogin']['INSTAGRAM']['ENABLE'])
        else:
            username = request.form.get("username")
            password = request.form.get("password")
            remember = 30 if request.form.get("remember") in ("True", "true", True) else None
            if username and password and UserAuth_Login(username, password):
                max_age_sec = 3600 * 24 * remember if remember else None
                expires     = How_Much_Time(max_age_sec) if max_age_sec else 'None'
                #expire_time = datetime.datetime.today() + datetime.timedelta(days=remember) if remember else None
                sessionId   = md5('%s-%s-%s-%s' %(username, md5(password), expires, "COOKIE_KEY")).upper()
                logger.debug("check user login successful, max_age_sec: %s, expires: %s" %(max_age_sec, expires))
                if SSOProject in GLOBAL.get("ACL") and SSORequest and SSORedirect and SSOTokenMD5 == SSOToken:
                    logger.info("RequestURL:%s, SSORequest:%s, SSOProject:%s, SSORedirect:%s" %(request.url, SSORequest, SSOProject, SSORedirect))
                    ticket    = '.'.join([ username, expires, sessionId ])
                    returnURL = SSORedirect + "?ticket=" + ticket
                    logger.info("SSO(%s) request project is in acl, will create a ticket, redirect to %s" %(SSOProject, returnURL))
                    resp = make_response(redirect(returnURL))
                else:
                    logger.info("Not SSO Auth, to local auth")
                    resp = make_response(redirect(url_for("uc")))
                resp.set_cookie(key='logged_in', value="yes", max_age=max_age_sec)
                resp.set_cookie(key='username',  value=username, max_age=max_age_sec)
                resp.set_cookie(key='sessionId', value=sessionId, max_age=max_age_sec)
                resp.set_cookie(key='time', value=expires, max_age=max_age_sec)
                resp.set_cookie(key='Azone', value="local", max_age=max_age_sec)
                #LogonCredentials: make_signed_cookie(username, md5(password), seconds=max_age_sec)
                #LogonCredentials: make_signed_cookie(username, openid/uid, seconds=max_age_sec)
                return resp
            else:
                if SSORequest:
                    return redirect(url_for("login", sso=SSORequest, sso_p=SSOProject, sso_r=SSORedirect, sso_t=SSOToken))
                else:
                    return redirect(url_for("login"))

@app.route("/logout/")
def logout():
    nextUrl = request.args.get("nextUrl") or url_for('login')
    resp = make_response(redirect(nextUrl))
    resp.set_cookie(key='logged_in', value='no', expires=None)
    resp.set_cookie(key='username',  value='', expires=0)
    resp.set_cookie(key='sessionId',  value='', expires=0)
    resp.set_cookie(key='Azone',  value='', expires=0)
    resp.set_cookie(key='time',  value='', expires=0)
    return resp

if __name__ == '__main__':
    Host  = GLOBAL.get('Host')
    Port  = GLOBAL.get('Port')
    app.run(host=Host, port=int(Port), debug=True)
