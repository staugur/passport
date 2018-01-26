# -*- coding: utf-8 -*-
"""
    passport.plugins.oauth2_qq
    ~~~~~~~~~~~~~~

    使用qq登录

    :copyright: (c) 2017 by staugur.
    :license: MIT, see LICENSE for more details.
"""

#: Importing these two modules is the first and must be done.
#: 首先导入这两个必须模块
from __future__ import absolute_import
from libs.base import PluginBase
#: Import the other modules here, and if it's your own module, use the relative Import. eg: from .lib import Lib
#: 在这里导入其他模块, 如果有自定义包目录, 使用相对导入, 如: from .lib import Lib
import json
from flask import Blueprint, request, jsonify, g, flash, redirect, url_for
from utils.web import OAuth2, analysis_cookie, dfr, oauth2_name2type, oauth2_genderconverter
from config import PLUGINS
from libs.auth import Authentication

#：Your plug-in name must be consistent with the plug-in directory name.
#：你的插件名称，必须和插件目录名称等保持一致.
__name__        = "oauth2_qq"
#: Plugin describes information. What does it do?
#: 插件描述信息,什么用处.
__description__ = "Connection QQ with OAuth2"
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
name = "qq"
if PLUGINS[name]["ENABLE"] in ("true", "True", True):
    __state__   = "enabled"
else:
    __state__   = "disabled"

qq = OAuth2(name,
    client_id = PLUGINS[name]["APP_ID"],
    client_secret = PLUGINS[name]["APP_KEY"],
    redirect_url = PLUGINS[name]["REDIRECT_URI"],
    authorize_url = "https://graph.qq.com/oauth2.0/authorize",
    access_token_url = "https://graph.qq.com/oauth2.0/token",
    access_token_method = "get",
    get_openid_url = "https://graph.qq.com/oauth2.0/me",
    get_openid_method = "get",
    get_userinfo_url = "https://graph.qq.com/user/get_user_info",
    get_userinfo_method = "get"
)

plugin_blueprint = Blueprint("oauth2_qq", "oauth2_qq")
@plugin_blueprint.route("/login")
def login():
    """ 跳转此OAuth应用登录以授权
    此路由地址：/oauth2/qq/login
    """
    return qq.authorize()

@plugin_blueprint.route("/authorized")
def authorized():
    """ 授权回调路由
    此路由地址：/oauth2/qq/authorized
    """
    # 换取access_token
    resp = qq.authorized_response()
    if "callback" in resp:
        resp = json.loads(resp[10:-3])
    else:
        resp = qq.url_code(resp)
    print "authorized_response:",resp
    if resp and isinstance(resp, dict) and "access_token" in resp:
        # 获取用户唯一标识
        openid = json.loads(qq.get_openid(resp["access_token"])[10:-3]).get("openid")
        # 根据access_token获取用户基本信息
        user = qq.get_userinfo(resp["access_token"], openid=openid, oauth_consumer_key=PLUGINS[name]["APP_ID"])
        if int(user.get("ret", 0)) < 0:
            flash(user.get("msg"))
            return redirect(url_for("front.index"))
        # 处理第三方登录逻辑
        auth = Authentication(g.mysql, g.redis)
        # 第三方账号登录入口`oauth2_go`
        goinfo = auth.oauth2_go(name=name, signin=g.signin, tokeninfo=resp, userinfo=dict(openid=openid, nick_name=user["nickname"], gender=oauth2_genderconverter(user["gender"]), avatar=user["figureurl_qq_1"], location="%s %s" %(user.get("province"), user.get("city"))), uid=g.uid)
        goinfo = dfr(goinfo)
        if goinfo["pageAction"] == "goto_signIn":
            """ 未登录流程->执行登录 """
            # 记录登录日志
            auth.brush_loginlog(dict(identity_type=oauth2_name2type(name), uid=goinfo["goto_signIn_data"]["guid"], success=True), login_ip=request.headers.get('X-Real-Ip', request.remote_addr), user_agent=request.headers.get("User-Agent"))
            # 设置登录态
            return qq.goto_signIn(uid=goinfo["goto_signIn_data"]["guid"])
        elif goinfo["pageAction"] == "goto_signUp":
            """ 未登录流程->执行注册绑定功能 """
            return qq.goto_signUp(openid=goinfo["goto_signUp_data"]["openid"])
        else:
            # 已登录流程->反馈绑定结果
            if goinfo["success"]:
                # 绑定成功，返回原页面
                flash(u"已绑定")
            else:
                # 绑定失败，返回原页面
                flash(goinfo["msg"])
            # 跳回原页面
            return redirect(url_for("front.index"))
    else:
        flash(u'Access denied: reason=%s error=%s' % (
            resp.get('error'),
            resp.get('error_description')
        ))
    return redirect(url_for("front.index"))

#: 返回插件主类
def getPluginClass():
    return OAuth2_QQ_Main

#: 插件主类, 不强制要求名称与插件名一致, 保证getPluginClass准确返回此类
class OAuth2_QQ_Main(PluginBase):
    """ 继承自PluginBase基类 """

    def register_tep(self):
        """注册模板入口, 返回扩展点名称及扩展的代码, 其中include点必须是实际的HTML文件, string点必须是HTML代码."""
        tep = {"auth_signIn_socialLogin_include": "connect_qq.html"}
        return tep

    def register_bep(self):
        """注册蓝图入口, 返回蓝图路由前缀及蓝图名称"""
        bep = {"prefix": "/oauth2/qq", "blueprint": plugin_blueprint}
        return bep
