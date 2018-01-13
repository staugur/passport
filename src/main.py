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

import config, json, datetime, jinja2, os
from version import __version__
from flask import Flask, request, g, jsonify, redirect, make_response, url_for, render_template, flash
from utils.tool import logger, gen_requestId, create_redis_engine, create_mysql_engine, generate_verification_code, email_check, phone_check, email_tpl
from utils.send_email_msg import SendMail
from libs.plugins import PluginManager

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
sendmail = SendMail()

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
    g.signin = True
    g.ref = request.referrer
    g.redirect_uri = g.ref or url_for('index') if request.endpoint and request.endpoint in ("logout", ) else request.url
    #上下文扩展点之请求后(返回前)
    before_request_hook = plugin.get_all_cep.get("before_request_hook")
    for cep_func in before_request_hook():
        cep_func(request=request, g=g)

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
    logger.info(data)
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
    return "index"

@app.route('/signUp', methods=['GET', 'POST'])
def signUp():
    return render_template("auth/signUp.html")

@app.route('/signIn', methods=['GET', 'POST'])
def signIn():
    if request.method == 'POST':
        token = request.form.get("token")
        challenge = request.form.get("challenge")
        user_id = request.form.get("user_id")
        password = request.form.get("password")
        if token and challenge and _validate(challenge, token):
            if user_id and password and str(user_id) == "admin" and str(password) == "admin":
                return redirect(url_for('index'))
            else:
                flash(u"无效的登录凭证")
        else:
            flash(u"人机验证失败")
        return redirect(url_for('signIn'))
    return render_template("auth/signIn.html")

@app.route('/miscellaneous/_sendVcode', methods=['POST'])
def misc_sendVcode():
    """发送验证码：邮箱、手机"""
    res = dict(msg=None, success=False)
    account = request.form.get("account")
    if email_check(account):
        email = account
        key = "passport:signUp:vcode:{}".format(email)
        if g.redis.exists(key):
            res.update(msg=u"已发送过验证码，请查收邮箱")
        else:
            vcode = generate_verification_code()
            result = sendmail.SendMessage(to_addr=email, subject=u"Passport邮箱注册验证码", formatType="html", message=email_tpl %(email, u"注册", vcode))
            if result["success"]:
                try:
                    g.redis.set(key, vcode)
                    g.redis.expire(key, 300)
                except Exception,e:
                    logger.error(e, exc_info=True)
                    res.update(msg=u"系统异常，请稍后重试")
                else:
                    res.update(msg=u"已发送验证码，有效期300秒", success=True)
            else:
                res.update(msg=u"邮件系统故障，请稍后重试")
    elif phone_check(account):
        res.update(msg=u"暂不支持手机注册")
    else:
        res.update(msg=u"无效账号")
    logger.debug(res)
    return jsonify(res)

from vaptchasdk import vaptcha
vid='5a55a721a48617214c19dc49'
key='56bb055bfbb84f949e30a9f145ba6372'
_vaptcha=vaptcha(vid, key)
@app.route("/getVaptcha")
def getVaptcha():
    sceneid = request.args.get("sceneid") or ""
    return jsonify(json.loads(_vaptcha.get_challenge(sceneid)))

@app.route("/getDowTime")
def getDowTime():
    return jsonify(json.loads(_vaptcha.downtime(data)))

def _validate(challenge,token):
    return _vaptcha.validate(challenge, token)

if __name__ == '__main__':
    app.run(host=app.config["GLOBAL"]["Host"], port=int(app.config["GLOBAL"]["Port"]), debug=True)
