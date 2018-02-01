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

import jinja2, os, sys
from config import GLOBAL, SYSTEM
from version import __version__
from utils.tool import logger, err_logger, access_logger, create_redis_engine, create_mysql_engine, DO
from utils.web import verify_cookie, analysis_cookie
from libs.plugins import PluginManager
from hlm import UserAppManager, UserProfileManager
from views import FrontBlueprint, AdminBlueprint, ApiBlueprint
from flask import Flask, request, g, jsonify, url_for, render_template
reload(sys)
sys.setdefaultencoding('utf-8')

__author__  = 'staugur'
__email__   = 'staugur@saintic.com'
__doc__     = '统一认证与单点登录系统'
__date__    = '2018-01-09'


#初始化定义application
app = Flask(__name__)
app.config.update(
    SECRET_KEY = os.urandom(24)
)

# 初始化接口管理器
api = DO({
    "userapp": UserAppManager(),
    "userprofile": UserProfileManager(),
})

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

# 注册视图包中蓝图
app.register_blueprint(FrontBlueprint)
app.register_blueprint(AdminBlueprint, url_prefix="/admin")
app.register_blueprint(ApiBlueprint, url_prefix="/api")

# 添加模板上下文变量
@app.context_processor  
def GlobalTemplateVariables():  
    data = {"Version": __version__, "Author": __author__, "Email": __email__, "Doc": __doc__, "SYSTEM": SYSTEM}
    return data

@app.before_request
def before_request():
    g.redis = create_redis_engine()
    g.mysql = create_mysql_engine()
    g.signin = verify_cookie(request.cookies.get("sessionId"))
    g.uid = analysis_cookie(request.cookies.get("sessionId")).get("uid") if g.signin else None
    g.api = api
    g.ref = request.referrer
    g.redirect_uri = g.ref or url_for('front.index') if request.endpoint and request.endpoint in ("logout", ) else request.url
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
    err_logger.error("500: {}".format(error), exc_info=True)
    message = {
        "msg": "Server Error",
        "code": 500
    }
    return jsonify(message), 500

@app.errorhandler(404)
def not_found(error=None):
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
    app.run(host=GLOBAL["Host"], port=int(GLOBAL["Port"]), debug=True)
