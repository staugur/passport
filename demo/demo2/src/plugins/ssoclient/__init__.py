# -*- coding: utf-8 -*-
"""
    ProcessName_XXX.plugins.ssoclient
    ~~~~~~~~~~~~~~

    SSO Client

    :copyright: (c) 2017 by staugur.
    :license: MIT, see LICENSE for more details.
"""

#: Importing these two modules is the first and must be done.
#: 首先导入这两个必须模块
from __future__ import absolute_import
from libs.base import PluginBase
#: Import the other modules here, and if it's your own module, use the relative Import. eg: from .lib import Lib
#: 在这里导入其他模块, 如果有自定义包目录, 使用相对导入, 如: from .lib import Lib
import requests
from config import SSO
from utils.web import anonymous_required, set_ssoparam, set_sessionId, get_redirect_url
from utils.tool import url_check, logger
from flask import Blueprint, request, jsonify, g, redirect, url_for, make_response

#：Your plug-in name must be consistent with the plug-in directory name.
#：你的插件名称，必须和插件目录名称等保持一致.
__name__        = "ssoclient"
#: Plugin describes information. What does it do?
#: 插件描述信息,什么用处.
__description__ = "SSO Client"
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

# 定义sso server地址并删除SSO多余参数
sso_server = SSO.get("sso_server")

# 定义蓝图
sso_blueprint = Blueprint("sso", "sso")

# 定义请求函数
def sso_request(url, params=None, data=None, timeout=5, num_retries=1):
    """
    @params dict: 请求查询参数
    @data dict: 提交表单数据
    @timeout int: 超时时间，单位秒
    @num_retries int: 超时重试次数
    """
    headers = {"User-Agent": "Mozilla/5.0 (X11; CentOS; Linux i686; rv:7.0.1406) Gecko/20100101 PassportClient/{}".format(__version__)}
    try:
        resp = requests.post(url, params=params, headers=headers, timeout=timeout, data=data).json()
    except requests.exceptions.Timeout,e:
        if num_retries > 0:
            return sso_request(url, params=params, data=data, timeout=timeout, num_retries=num_retries-1)
    else:
        return resp

@sso_blueprint.route("/Login")
@anonymous_required
def Login():
    """ Client登录地址，需要跳转到SSO Server上 """
    if url_check(sso_server):
        logger.debug("SSO Configuration: {}".format(SSO))
        NextUrl = "{}/sso/?sso={}".format(sso_server.strip("/"), set_ssoparam())
        return redirect(NextUrl)
    else:
        return "Invalid Configuration"

@sso_blueprint.route("/authorized")
@anonymous_required
def authorized():
    """ Client SSO 单点登录、注销入口, 根据`Action`参数判断是`ssoLogin`还是`ssoLogout` """
    Action = request.args.get("Action") or "ssoLogin"
    if Action == "ssoLogin":
        ticket = request.args.get("ticket")
        if ticket:
            resp = sso_request("{}/sso/validate".format(sso_server.strip("/")), dict(Action="validate_ticket"), dict(ticket=ticket, app_name=SSO["app_name"], get_userinfo=True, get_userbind=False))
            logger.debug("SSO check ticket resp: {}".format(resp))
            if resp and isinstance(resp, dict) and "success" in resp:
                if resp["success"] is True:
                    userinfo = resp["userinfo"]
                    logger.debug(userinfo)
                    # 授权令牌验证通过，设置局部会话，允许登录
                    sessionId = set_sessionId(uid=resp["uid"])
                    response = make_response(redirect(get_redirect_url("front.index")))
                    # 设置cookie根据浏览器周期过期，当无https时去除`secure=True`
                    secure = False if request.url_root.split("://")[0] == "http" else True
                    response.set_cookie(key="sessionId", value=sessionId, max_age=None, httponly=True, secure=secure)
                    return response
    return "Invalid Authorized"

#: 返回插件主类
def getPluginClass():
    return SSOClientMain

#: 插件主类, 不强制要求名称与插件名一致, 保证getPluginClass准确返回此类
class SSOClientMain(PluginBase):

    def register_bep(self):
        """注册蓝图入口, 返回蓝图路由前缀及蓝图名称"""
        bep = {"prefix": "/sso", "blueprint": sso_blueprint}
        return bep
