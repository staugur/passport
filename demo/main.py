# -*- coding: utf-8 -*-
"""
    demo.main
    ~~~~~~~~~~~~~~

    Entrance

    Docstring conventions:
    http://flask.pocoo.org/docs/0.10/styleguide/#docstrings

    Comments:
    http://flask.pocoo.org/docs/0.10/styleguide/#comments

    :copyright: (c) 2017 by staugur.
    :license: MIT, see LICENSE for more details.
"""

import os
import jinja2
from config import GLOBAL
from utils.tool import err_logger, access_logger
from utils.web import verify_sessionId, analysis_sessionId, get_redirect_url
from views import FrontBlueprint
from flask import Flask, request, g, jsonify
from flask_pluginkit import PluginManager


__author__ = 'staugur'
__email__ = 'staugur@saintic.com'
__doc__ = 'SSO Cient Demo'
__date__ = '2018-03-14'
__version__ = '0.1.0'


# 初始化定义application
app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.urandom(24)
)

# 初始化插件管理器(自动扫描并加载运行)
plugin = PluginManager(app)

# 注册视图包中蓝图
app.register_blueprint(FrontBlueprint)

# 添加模板上下文变量
@app.context_processor
def GlobalTemplateVariables():
    data = {"Version": __version__, "Author": __author__, "Email": __email__, "Doc": __doc__}
    return data


@app.before_request
def before_request():
    g.signin = verify_sessionId(request.cookies.get("sessionId"))
    g.sid, g.uid = analysis_sessionId(request.cookies.get("sessionId"), "tuple") if g.signin else (None, None)
    g.ip = request.headers.get('X-Real-Ip', request.remote_addr)
    # 仅是重定向页面快捷定义
    g.redirect_uri = get_redirect_url()


if __name__ == '__main__':
    app.run(host=GLOBAL["Host"], port=int(GLOBAL["Port"]), debug=True)
