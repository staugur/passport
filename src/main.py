# -*- coding: utf-8 -*-
"""
    passport.main
    ~~~~~~~~~~~~~~

    Entrance

    Docstring conventions:
    http://flask.pocoo.org/docs/0.10/styleguide/#docstrings

    Comments:
    http://flask.pocoo.org/docs/0.10/styleguide/#comments

    :copyright: (c) 2017 by staugur.
    :license: MIT, see LICENSE for more details.
"""

import config, json, datetime, jinja2, os, sys
from version import __version__
from utils.tool import logger, access_logger, create_redis_engine, create_mysql_engine, generate_verification_code, email_check, phone_check
from utils.web import email_tpl, login_required, anonymous_required, set_cookie, verify_cookie, analysis_cookie, dfr
from utils.send_email_msg import SendMail
from libs.plugins import PluginManager
from libs.auth import Authentication
from vaptchasdk import vaptcha as VaptchaApi
from flask import Flask, request, g, jsonify, redirect, make_response, url_for, render_template, flash
reload(sys)
sys.setdefaultencoding('utf-8')

__author__  = 'staugur'
__email__   = 'staugur@saintic.com'
__doc__     = '统一认证与单点登录系统'
__date__    = '2018-01-09'


#初始化定义application
app = Flask(__name__)
app.config.from_object(config)
app.config.update(
    SECRET_KEY=os.urandom(24)
)
#初始化邮箱发送服务
sendmail = SendMail()
#初始化手势验证码服务
vaptcha = VaptchaApi(app.config["VAPTCHA"]["vid"], app.config["VAPTCHA"]["key"])
#初始化插件管理器(自动扫描并加载运行)
plugin = PluginManager()

#注册多模板文件夹
loader = jinja2.ChoiceLoader([
    app.jinja_loader,
    jinja2.FileSystemLoader([ p.get("plugin_tpl_path") for p in plugin.get_enabled_plugins if os.path.isdir(os.path.join(app.root_path, p["plugin_tpl_path"])) ]),
])
app.jinja_loader = loader

#注册全局模板扩展点
for tep_name,tep_func in plugin.get_all_tep.iteritems():
    app.add_template_global(tep_func, tep_name)

# 注册蓝图扩展点
for bep in plugin.get_all_bep:
    prefix = bep["prefix"]
    app.register_blueprint(bep["blueprint"], url_prefix=prefix)

# 模板中重写覆盖url_for函数
def static_url_for(endpoint, **values):
    if endpoint == 'static':
        STATIC_URL_ROOT = app.config["GLOBAL"].get("STATIC_URL_ROOT")
        LAST_URL = STATIC_URL_ROOT.strip("/") + url_for(endpoint, **values) if STATIC_URL_ROOT else url_for(endpoint, **values)
        return LAST_URL
    else:
        return url_for(endpoint, **values)

# 添加模板上下文变量
@app.context_processor  
def GlobalTemplateVariables():  
    data = {"Version": __version__, "Author": __author__, "Email": __email__, "Doc": __doc__, "url_for": static_url_for}
    return data

@app.before_request
def before_request():
    g.redis = create_redis_engine(app.config["REDIS"])
    g.mysql = create_mysql_engine(app.config["MYSQL"])
    g.signin = verify_cookie(request.cookies.get("sessionId"))
    g.uid = analysis_cookie(request.cookies.get("sessionId")).get("uid")
    g.ref = request.referrer
    g.redirect_uri = g.ref or url_for('index') if request.endpoint and request.endpoint in ("logout", ) else request.url
    #access_logger.debug("referrer: {}, redirect_uri: {}".format(g.ref, g.redirect_uri))
    #上下文扩展点之请求后(返回前)
    before_request_hook = plugin.get_all_cep.get("before_request_hook")
    for cep_func in before_request_hook():
        cep_func(request=request, g=g)
    #app.logger.debug(app.url_map)

@app.after_request
def after_request(response):
    data = {
        "status_code": response.status_code,
        "method": request.method,
        "ip": request.headers.get('X-Real-Ip', request.remote_addr),
        "url": request.url,
        "referer": request.headers.get('Referer'),
        "agent": request.headers.get("User-Agent"),
        "signin": g.signin
    }
    access_logger.info(data)
    #上下文扩展点之请求后(返回前)
    after_request_hook = plugin.get_all_cep.get("after_request_hook")
    for cep_func in after_request_hook():
        cep_func(request=request, response=response, data=data)
    return response

@app.teardown_request
def teardown_request(exception):
    if hasattr(g, "redis"):
        g.redis.connection_pool.disconnect()
    if hasattr(g, "mysql"):
        g.mysql.close()

@app.errorhandler(500)
def server_error(error=None):
    message = {
        "msg": "Server Error",
        "code": 500
    }
    return jsonify(message), 500

@app.errorhandler(404)
def not_found(error=None):
    message = {
        'code': 404,
        'msg': 'Not Found: ' + request.url,
    }
    resp = jsonify(message)
    resp.status_code = 404
    return resp

@app.errorhandler(403)
def Permission_denied(error=None):
    message = {
        "msg": "Authentication failed, permission denied.",
        "code": 403
    }
    return jsonify(message), 403

@app.route('/')
def index():
    #首页
    return render_template("index.html")

@app.route('/link')
def link():
    """重定向链接"""
    nextUrl = request.args.get("nextUrl") or url_for("index")
    return redirect(nextUrl)

@app.route('/signUp', methods=['GET', 'POST'])
@anonymous_required
def signUp():
    if request.method == 'POST':
        sceneid = request.args.get("sceneid") or "02"
        token = request.form.get("token")
        challenge = request.form.get("challenge")
        if token and challenge and vaptcha.validate(challenge, token, sceneid):
            account = request.form.get("account")
            vcode = request.form.get("vcode")
            password = request.form.get("password")
            repassword = request.form.get("repassword")
            register_ip = request.headers.get('X-Real-Ip', request.remote_addr)
            auth = Authentication(g.mysql, g.redis)
            try:
                res = auth.signUp(account=account, vcode=vcode, password=password, repassword=repassword, register_ip=register_ip)
            except Exception,e:
                logger.error(e, exc_info=True)
                flash(u"系统异常，请稍后再试")
            else:
                res = dfr(res)
                if res["success"]:
                    # 写登陆日志
                    return redirect(url_for('signIn'))
                else:
                    flash(res["msg"])
        else:
            flash(u"人机验证失败")
        return redirect(url_for('signUp'))
    return render_template("auth/signUp.html")

@app.route('/signIn', methods=['GET', 'POST'])
@anonymous_required
def signIn():
    if request.method == 'POST':
        sceneid = request.args.get("sceneid") or "01"
        token = request.form.get("token")
        challenge = request.form.get("challenge")
        if token and challenge and vaptcha.validate(challenge, token, sceneid):
            account = request.form.get("account")
            password = request.form.get("password")
            login_ip = request.headers.get('X-Real-Ip', request.remote_addr)
            auth = Authentication(g.mysql, g.redis)
            res = auth.signIn(account=account, password=password)
            res = dfr(res)
            if res["success"]:
                # 记录登录日志
                auth.brush_loginlog(res, login_ip=login_ip, user_agent=request.headers.get("User-Agent"))
                # 登录成功，设置cookie
                sessionId = set_cookie(uid=res["uid"])
                response = make_response(redirect(g.redirect_uri))
                # 设置cookie根据浏览器周期过期，当无https时去除`secure=True`
                secure = False if request.url_root.split("://")[0] == "http" else True
                response.set_cookie(key="sessionId", value=sessionId, max_age=None, httponly=True, secure=secure)
                return response
            else:
                flash(res["msg"])
        else:
            flash(u"人机验证失败")
        return redirect(url_for('signIn'))
    return render_template("auth/signIn.html")

@app.route("/OAuthGuide")
@anonymous_required
def OAuthGuide():
    """OAuth2登录未注册时引导路由，选择绑定已有账号或直接登录(首选)"""
    if request.args.get("openid"):
        return render_template("auth/OAuthGuide.html")
    else:
        return redirect(url_for("index"))

@app.route("/OAuthGuide/DirectLogin", methods=["POST"])
@anonymous_required
def OAuthDirectLogin():
    """OAuth2直接登录(首选)"""
    if request.method == 'POST':
        openid = request.form.get("openid")
        if openid:
            auth = Authentication(g.mysql, g.redis)
            # 直接注册新账号并设置登录态
            ip = request.headers.get('X-Real-Ip', request.remote_addr)
            res = auth.oauth2_signUp(openid, ip)
            res = dfr(res)
            if res["success"]:
                # 记录登录日志
                auth.brush_loginlog(res, login_ip=ip, user_agent=request.headers.get("User-Agent"))
                # 登录成功，设置cookie
                sessionId = set_cookie(uid=res["uid"])
                response = make_response(redirect(url_for("index")))
                # 设置cookie根据浏览器周期过期，当无https时去除`secure=True`
                secure = False if request.url_root.split("://")[0] == "http" else True
                response.set_cookie(key="sessionId", value=sessionId, max_age=None, httponly=True, secure=secure)
                return response
            else:
                flash(res["msg"])
            return redirect(url_for('index'))
        else:
            return redirect(url_for("index"))

@app.route("/OAuthGuide/BindAccount", methods=["GET", "POST"])
@anonymous_required
def OAuthBindAccount():
    """OAuth2绑定已有账号登录"""
    if request.method == 'POST':
        openid = request.form.get("openid")
        sceneid = request.args.get("sceneid") or "03"
        token = request.form.get("token")
        challenge = request.form.get("challenge")
        if token and challenge and vaptcha.validate(challenge, token, sceneid):
            account = request.form.get("account")
            password = request.form.get("password")
            auth = Authentication(g.mysql, g.redis)
            res = auth.oauth2_bindLogin(openid=openid, account=account, password=password)
            res = dfr(res)
            if res["success"]:
                # 记录登录日志
                auth.brush_loginlog(res, login_ip=request.headers.get('X-Real-Ip', request.remote_addr), user_agent=request.headers.get("User-Agent"))
                # 登录成功，设置cookie
                sessionId = set_cookie(uid=res["uid"])
                response = make_response(redirect(url_for("index")))
                # 设置cookie根据浏览器周期过期，当无https时去除`secure=True`
                secure = False if request.url_root.split("://")[0] == "http" else True
                response.set_cookie(key="sessionId", value=sessionId, max_age=None, httponly=True, secure=secure)
                return response
            else:
                flash(res["msg"])
        else:
            flash(u"人机验证失败")
        return redirect(url_for('OAuthBindAccount', openid=openid))
    else:
        openid = request.args.get("openid")
        if openid:
            return render_template("auth/OAuthBindAccount.html")
        else:
            redirect(url_for("index"))

@app.route('/miscellaneous/_sendVcode', methods=['POST'])
def misc_sendVcode():
    """发送验证码：邮箱、手机"""
    res = dict(msg=None, success=False)
    account = request.form.get("account")
    if email_check(account):
        email = account
        key = "passport:signUp:vcode:{}".format(email)
        try:
            hasKey = g.redis.exists(key)
        except Exception,e:
            logger.error(e, exc_info=True)
            res.update(msg="System is abnormal")
        else:
            if hasKey:
                res.update(msg="Have sent the verification code, please check the mailbox")
            else:
                vcode = generate_verification_code()
                result = sendmail.SendMessage(to_addr=email, subject=u"Passport邮箱注册验证码", formatType="html", message=email_tpl %(email, u"注册", vcode))
                if result["success"]:
                    try:
                        g.redis.set(key, vcode)
                        g.redis.expire(key, 300)
                    except Exception,e:
                        logger.error(e, exc_info=True)
                        res.update(msg="System is abnormal")
                    else:
                        res.update(msg="Sent verification code, valid for 300 seconds", success=True)
                else:
                    res.update(msg="Mail delivery failed, please try again later")
    elif phone_check(account):
        res.update(msg="Not support phone number registration")
    else:
        res.update(msg="Invalid account")
    logger.debug(res)
    return jsonify(dfr(res))

@app.route("/miscellaneous/_getChallenge")
def misc_getChallenge():
    """Vaptcha获取流水
    @param sceneid str: 场景id，如01登录、02注册
    """
    sceneid = request.args.get("sceneid") or ""
    return jsonify(json.loads(vaptcha.get_challenge(sceneid)))

@app.route("/miscellaneous/_getDownTime")
def misc_getDownTime():
    """Vaptcha宕机模式
    like: ?data=request&_t=1516092685906
    """
    data = request.args.get("data")
    logger.info("vaptcha into downtime, get data: {}, query string: {}".format(data, request.args.to_dict()))
    return jsonify(json.loads(vaptcha.downtime(data)))

@app.route("/logout")
@login_required
def logout():
    response = make_response(redirect(url_for('signIn')))
    response.set_cookie(key='sessionId', value='', expires=0)
    return response

if __name__ == '__main__':
    app.run(host=app.config["GLOBAL"]["Host"], port=int(app.config["GLOBAL"]["Port"]), debug=True)
