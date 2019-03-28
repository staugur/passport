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
import time
from version import __version__
from utils.tool import logger, err_logger, access_logger, create_redis_engine, create_mysql_engine, DO
from utils.web import verify_sessionId, analysis_sessionId, tpl_adminlogin_required, get_redirect_url
from hlm import UserAppManager, UserSSOManager, UserMsgManager, UserProfileManager
from views import FrontBlueprint, ApiBlueprint
from flask import request, g, jsonify
from flask_pluginkit import Flask, PluginManager
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
    MAX_CONTENT_LENGTH=4 * 1024 * 1024
)

# 初始化接口管理器
api = DO({
    "userapp": UserAppManager(),
    "usersso": UserSSOManager(),
    "usermsg": UserMsgManager(),
    "userprofile": UserProfileManager(),
})

# 初始化插件管理器(自动扫描并加载运行)
plugin = PluginManager(app)

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
    sessionId = request.cookies.get("sessionId", request.headers.get("sessionId"))
    g.startTime = time.time()
    g.redis = create_redis_engine()
    g.mysql = create_mysql_engine()
    g.signin = verify_sessionId(sessionId)
    g.sid, g.uid = analysis_sessionId(sessionId, "tuple") if g.signin else (None, None)
    logger.debug("uid: {}, sid: {}".format(g.uid, g.sid))
    g.api = api
    g.ip = request.headers.get('X-Real-Ip', request.remote_addr)
    g.agent = request.headers.get("User-Agent")
    # 仅是重定向页面快捷定义
    g.redirect_uri = get_redirect_url()


@app.after_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET,OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Access-Control-Allow-Orgin,sessionId,XMLHttpRequest,Referer,Accept,Authorization,Cache-Control,Content-Type,Keep-Alive,Origin,User-Agent,X-Requested-With'
    return response


@app.teardown_request
def teardown_request(exception):
    if exception:
        err_logger.error(exception, exc_info=True)
    if hasattr(g, "redis"):
        g.redis.connection_pool.disconnect()
    if hasattr(g, "mysql"):
        g.mysql.close()


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
    from werkzeug.contrib.fixers import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app)
    app.run(host=config.GLOBAL["Host"], port=int(config.GLOBAL["Port"]), debug=True)
