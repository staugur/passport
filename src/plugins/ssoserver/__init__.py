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
from flask import Blueprint, request, jsonify, g, abort, redirect, url_for
from utils.web import get_redirect_url, verify_sessionId, analysis_sessionId

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
__state__       = "disabled"

sso_blueprint = Blueprint("sso", "sso")
@sso_blueprint.route("/")
def index():
    """ 单点登录、注销
    登录流程
        1. Client跳转到Server的/sso/页面，携带参数sso(所需sso信息的加密串)。
        2. 校验参数通过后，Server跳转到/signIn/页面，设置ReturnUrl(从数据库读取)，且不携带参数；校验未通过不携带参数直接返回错误信息。
        3. 用户在Server未登录时，输入用户名密码或第三方登录成功后，创建全局会话(设置Server登录态)、授权令牌(ticket)，根据ticket生成sid(登录态id)写入redis，并携带ticket返回ReturnUrl；
           已登录时，创建ticket并携带跳回ReturnUrl。
        4. Client用ticket到Server校验(通过api方式)，通过redis校验cookie是否存在
        -- sso加密规则：
            aes_cbc("app_name:app_id.app_secret")
        -- sso校验流程：
            根据sso参数，验证是否有效，解析参数获取name、id、secret等，并用name获取到对应信息一一校验
        -- 备注：
            第3步，需要signIn、OAuthGuide方面路由设置
            第4步，需要在插件内增加api路由
    注销流程
    """
    sso = request.args.get("sso")
    if verify_sessionId(sso):
        # sso jwt payload
        sso = analysis_sessionId(sso)
        if sso and isinstance(sso, dict) and "app_name" in sso and "app_id" in sso and "app_secret" in sso:
            # 通过app_name获取注册信息并校验参数
            app_data = g.api.userapp.getUserApp(sso["app_name"])
            if app_data:
                if sso["app_id"] == app_data["app_id"] and sso["app_secret"] == app_data["app_secret"]:
                    ReturnUrl = app_data["app_redirect_url"] + "?Action=login"
                    return redirect(url_for("front.signIn", ReturnUrl=ReturnUrl))
    return abort(404)

@sso_blueprint.route("/validate")
def validate():
    pass

#: 返回插件主类
def getPluginClass():
    return SSOServerMain

#: 插件主类, 不强制要求名称与插件名一致, 保证getPluginClass准确返回此类
class SSOServerMain(PluginBase):

    def register_bep(self):
        """注册蓝图入口, 返回蓝图路由前缀及蓝图名称"""
        bep = {"prefix": "/sso", "blueprint": sso_blueprint}
        return bep
