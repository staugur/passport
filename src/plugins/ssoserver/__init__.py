# -*- coding: utf-8 -*-
"""
    passport.plugins.ssoserver
    ~~~~~~~~~~~~~~

    SSO Server with http://www.cnblogs.com/ywlaker/p/6113927.html

    :copyright: (c) 2017 by staugur.
    :license: MIT, see LICENSE for more details.
"""

#: Importing these two modules is the first and must be done.
#: 首先导入这两个必须模块
from __future__ import absolute_import
from libs.base import PluginBase
#: Import the other modules here, and if it's your own module, use the relative Import. eg: from .lib import Lib
#: 在这里导入其他模块, 如果有自定义包目录, 使用相对导入, 如: from .lib import Lib
from utils.tool import logger
from utils.web import verify_sessionId
from flask import Blueprint, request, jsonify, g, redirect, url_for

#：Your plug-in name must be consistent with the plug-in directory name.
#：你的插件名称，必须和插件目录名称等保持一致.
__name__        = "ssoserver"
#: Plugin describes information. What does it do?
#: 插件描述信息,什么用处.
__description__ = "SSO Server"
#: Plugin Author
#: 插件作者
__author__      = "Mr.tao <staugur@saintic.com>"
#: Plugin Version
#: 插件版本
__version__     = "0.1" 
#: Plugin Url
#: 插件主页
__url__         = "https://www.saintic.com"
#: Plugin License
#: 插件许可证
__license__     = "MIT"
#: Plugin License File
#: 插件许可证文件
__license_file__= "LICENSE"
#: Plugin Readme File
#: 插件自述文件
__readme_file__ = "README"
#: Plugin state, enabled or disabled, default: enabled
#: 插件状态, enabled、disabled, 默认enabled
__state__       = "enabled"

sso_blueprint = Blueprint("sso", "sso")
@sso_blueprint.route("/")
def index():
    """sso入口，仅判断是否为sso请求，最终重定向到登录页"""
    sso = request.args.get("sso")
    if verify_sessionId(sso):
        return redirect(url_for("front.signIn", sso=sso))
    return redirect(url_for("front.signIn"))

@sso_blueprint.route("/validate", methods=["POST"])
def validate():
    res = dict(msg=None, success=False)
    Action = request.args.get("Action")
    if request.method == "POST":
        if Action == "validate_ticket":
            ticket = request.form.get("ticket")
            get_userinfo = True if request.form.get("get_userinfo") in (1, True, "1", "True", "true", "on") else False
            get_userbind = True if request.form.get("get_userbind") in (1, True, "1", "True", "true", "on") else False
            if ticket:
                resp = g.api.userapp.ssoGetWithTicket(ticket)
                logger.debug("sso validate ticket resp: {}".format(resp))
                if resp and isinstance(resp, dict):
                    # 此时表明ticket验证通过，应当返回如下信息：
                    # dict(uid=必需, sid=必需，app_name=必需)
                    res.update(success=True, uid=resp["uid"])
                    # 有效，此sid已登录客户端中注册app_name
                    res.update(register=g.api.userapp.ssoRegisterClient(sid=resp["sid"], app_name=resp["app_name"]))
                    if get_userinfo is True:
                        userinfo = g.api.userprofile.getUserProfile(uid=resp["uid"], getBind=get_userbind)
                        res.update(userinfo=userinfo)
                else:
                    res.update(msg="Invaild ticket or expired")
            else:
                res.update(msg="Invaild ticket")
        else:
            res.update(msg="Invaild Action")
    return jsonify(res)

#: 返回插件主类
def getPluginClass():
    return SSOServerMain

#: 插件主类, 不强制要求名称与插件名一致, 保证getPluginClass准确返回此类
class SSOServerMain(PluginBase):

    def register_bep(self):
        """注册蓝图入口, 返回蓝图路由前缀及蓝图名称"""
        bep = {"prefix": "/sso", "blueprint": sso_blueprint}
        return bep
