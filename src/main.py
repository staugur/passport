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

import jinja2
import os
import sys
import config
from version import __version__
from utils.tool import logger, err_logger, access_logger, create_redis_engine, create_mysql_engine, DO
from utils.web import verify_sessionId, analysis_sessionId, tpl_adminlogin_required, get_redirect_url
from libs.plugins import PluginManager
from hlm import UserAppManager, UserSSOManager, UserProfileManager
from views import FrontBlueprint, ApiBlueprint
from flask import Flask, request, g, jsonify
reload(sys)
sys.setdefaultencoding('utf-8')

__author__ = 'staugur'
__email__ = 'staugur@saintic.com'
__doc__ = '统一认证与单点登录系统'
__date__ = '2018-01-09'


# 初始化定义application
app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.urandom(24),
    MAX_CONTENT_LENGTH=2 * 1024 * 1024
)

# 初始化接口管理器
api = DO({
    "userapp": UserAppManager(),
    "usersso": UserSSOManager(),
    "userprofile": UserProfileManager(),
})

# 初始化插件管理器(自动扫描并加载运行)
plugin = PluginManager()

# 注册多模板文件夹
loader = jinja2.ChoiceLoader([
    app.jinja_loader,
    jinja2.FileSystemLoader([p.get("plugin_tpl_path") for p in plugin.get_enabled_plugins if os.path.isdir(os.path.join(app.root_path, p["plugin_tpl_path"]))]),
])
app.jinja_loader = loader

# 注册全局模板扩展点
for tep_name, tep_func in plugin.get_all_tep.iteritems():
    app.add_template_global(tep_func, tep_name)

# 注册蓝图扩展点
for bep in plugin.get_all_bep:
    prefix = bep["prefix"]
    app.register_blueprint(bep["blueprint"], url_prefix=prefix)

# 注册视图包中蓝图
app.register_blueprint(FrontBlueprint)
app.register_blueprint(ApiBlueprint, url_prefix="/api")

# 添加模板上下文变量
@app.context_processor
def GlobalTemplateVariables():
    data = {"Version": __version__, "Author": __author__, "Email": __email__, "Doc": __doc__, "CONFIG": config, "tpl_adminlogin_required": tpl_adminlogin_required}
    return data

@app.before_request
def before_request():
    g.redis = create_redis_engine()
    g.mysql = create_mysql_engine()
    g.signin = verify_sessionId(request.cookies.get("sessionId"))
    g.sid, g.uid = analysis_sessionId(request.cookies.get("sessionId"), "tuple") if g.signin else (None, None)
    g.api = api
    g.ip = request.headers.get('X-Real-Ip', request.remote_addr)
    # 仅是重定向页面快捷定义
    g.redirect_uri = get_redirect_url()
    # 上下文扩展点之请求后(返回前)
    before_request_hook = plugin.get_all_cep.get("before_request_hook")
    for cep_func in before_request_hook():
        cep_func(request=request, g=g)
    before_request_return = plugin.get_all_cep.get("before_request_return")
    for cep_func in before_request_return():
        resp = cep_func(request=request, g=g)
        try:
            success = resp.is_before_request_return
        except:
            logger.warn("Plugin returns abnormalities when before_request_return")
        else:
            if success is True:
                return resp

@app.after_request
def after_request(response):
    data = {
        "status_code": response.status_code,
        "method": request.method,
        "ip": g.ip,
        "url": request.url,
        "referer": request.headers.get('Referer'),
        "agent": request.headers.get("User-Agent"),
    }
    access_logger.info(data)
    # 上下文扩展点之请求后(返回前)
    after_request_hook = plugin.get_all_cep.get("after_request_hook")
    for cep_func in after_request_hook():
        cep_func(request=request, response=response, data=data)
    return response

@app.teardown_request
def teardown_request(exception):
    if exception:
        err_logger.error(exception, exc_info=True)
    if hasattr(g, "redis"):
        g.redis.connection_pool.disconnect()
    if hasattr(g, "mysql"):
        g.mysql.close()
    teardown_request_hook = plugin.get_all_cep.get("teardown_request_hook")
    for cep_func in teardown_request_hook():
        cep_func(request=request, g=g, exception=exception)

@app.errorhandler(500)
def server_error(error=None):
    if error:
        err_logger.error("500: {}".format(error), exc_info=True)
    message = {
        "msg": "Server Error",
        "code": 500
    }
    return jsonify(message), 500

@app.errorhandler(404)
def not_found(error=None):
    if error:
        err_logger.debug("404: {}".format(error))
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

if __name__ == '__main__':
    #from werkzeug.contrib.fixers import ProxyFix
    #app.wsgi_app = ProxyFix(app.wsgi_app)
    app.run(host=config.GLOBAL["Host"], port=int(config.GLOBAL["Port"]), debug=True)
