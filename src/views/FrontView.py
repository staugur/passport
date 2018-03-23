# -*- coding: utf-8 -*-
"""
    passport.views.FrontView
    ~~~~~~~~~~~~~~

    The blueprint for front view.

    :copyright: (c) 2017 by staugur.
    :license: MIT, see LICENSE for more details.
"""
from config import SYSTEM
from utils.web import login_required, anonymous_required, adminlogin_required, dfr, oauth2_name2type, get_redirect_url, checkGet_ssoRequest, checkSet_ssoTicketSid, set_loginstate, VaptchaApi
from utils.tool import logger, email_check, phone_check, md5
from libs.auth import Authentication
from urllib import urlencode
from flask import Blueprint, request, render_template, g, redirect, url_for, flash, make_response

#初始化前台蓝图
FrontBlueprint = Blueprint("front", __name__)
#初始化手势验证码服务
vaptcha = VaptchaApi()

@FrontBlueprint.route('/')
@login_required
def index():
    # 未登录时跳转到登录页；已登录后跳转到个人设置页面
    return redirect(url_for(".userset"))

@FrontBlueprint.route('/user/setting/')
@login_required
def userset():
    """用户基本设置"""
    return render_template("user/setting.html")

@FrontBlueprint.route('/user/app/')
@adminlogin_required
def userapp():
    Action = request.args.get("Action")
    if Action == "editView":
        # 编辑应用
        return render_template("user/apps.edit.html")
    # 默认返回应用选项卡
    return render_template("user/apps.html")

@FrontBlueprint.route('/sys/manager/')
@adminlogin_required
def sysmanager():
    # 系统管理
    return render_template("user/sysmanager.html")

@FrontBlueprint.route('/user/message/')
@login_required
def usermsg():
    """用户消息"""
    return render_template("user/message.html")

@FrontBlueprint.route('/signUp', methods=['GET', 'POST'])
@anonymous_required
def signUp():
    if request.method == 'POST':
        if vaptcha.validate:
            account = request.form.get("account")
            vcode = request.form.get("vcode")
            password = request.form.get("password")
            repassword = request.form.get("repassword")
            auth = Authentication(g.mysql, g.redis)
            try:
                res = auth.signUp(account=account, vcode=vcode, password=password, repassword=repassword, register_ip=g.ip)
            except Exception,e:
                logger.error(e, exc_info=True)
                flash(u"系统异常，请稍后再试")
            else:
                res = dfr(res)
                if res["success"]:
                    # 写登陆日志
                    return redirect(url_for('.signIn'))
                else:
                    flash(res["msg"])
        else:
            flash(u"人机验证失败")
        return redirect(url_for('.signUp'))
    return render_template("auth/signUp.html", vaptcha=vaptcha.getChallenge)

@FrontBlueprint.route('/signIn', methods=['GET', 'POST'])
def signIn():
    """ 单点登录流程
        1. Client跳转到Server的登录页，携带参数sso(所需sso信息的加密串)，验证并获取应用数据。
        2. 未登录时，GET请求显示登录表单，输入用户名密码或第三方POST登录成功后(一处是signIn post；一处是OAuthDirectLogin post；一处是OAuthBindAccount post)，创建全局会话(设置Server登录态)、授权令牌ticket，根据ticket生成sid(全局会话id)写入redis，ReturnUrl组合ticket跳转；
           已登录后，检查是否有sid，没有则创建ticket，ReturnUrl组合ticket跳转。
        3. 校验参数通过后，设置ReturnUrl(从数据库读取)为Client登录地址；校验未通过时ReturnUrl为系统redirect_uri。
        4. Client用ticket到Server校验(通过api方式)，通过redis校验cookie是否存在；存在则创建局部会话(设置Client登录态)，否则登录失败。
        -- sso加密规则：
            aes_cbc(jwt_encrypt("app_name:app_id.app_secret"))
        -- sso校验流程：
            根据sso参数，验证是否有效，解析参数获取name、id、secret等，并用name获取到对应信息一一校验
        -- 备注：
            第3步，需要signIn、OAuthGuide方面路由设置
            第4步，需要在插件内增加api路由
    """
    # 加密的sso参数值
    sso = request.args.get("sso") or None
    sso_isOk, sso_returnUrl, sso_appName = checkGet_ssoRequest(sso)
    logger.debug("method: {}, sso_isOk: {}, ReturnUrl: {}".format(request.method, sso_isOk, sso_returnUrl))
    if g.signin:
        # 已登录后流程
        # 如果没有sid说明是本地登录，需要重置登录态
        if sso_isOk:
            if g.sid:
                # 创建ticket，返回为真即是ticket
                tickets = g.api.usersso.ssoCreateTicket(sid=g.sid)
                if tickets:
                    ticket, sid = tickets
                    returnUrl = "{}&ticket={}".format(sso_returnUrl, ticket)
                    return redirect(returnUrl)
                else:
                    flash(dfr(dict(msg="Failed to create authorization ticket")))
            else:
                sessionId, returnUrl = checkSet_ssoTicketSid(sso_isOk, sso_returnUrl, sso_appName, g.uid, get_redirect_url("front.userset"))
                return set_loginstate(sessionId, returnUrl)
        return redirect(url_for("front.userset"))
    else:
        # 未登录时流程
        if request.method == 'POST':
            # POST请求不仅要设置登录态、还要设置全局会话
            if vaptcha.validate:
                account = request.form.get("account")
                password = request.form.get("password")
                auth = Authentication(g.mysql, g.redis)
                res = auth.signIn(account=account, password=password)
                res = dfr(res)
                if res["success"]:
                    # 记录登录日志
                    auth.brush_loginlog(res, login_ip=g.ip, user_agent=request.headers.get("User-Agent"))
                    sessionId, returnUrl = checkSet_ssoTicketSid(sso_isOk, sso_returnUrl, sso_appName, res["uid"], get_redirect_url("front.userset"))
                    logger.debug("signIn post returnUrl: {}".format(returnUrl))
                    return set_loginstate(sessionId, returnUrl)
                else:
                    flash(res["msg"])
            else:
                flash(u"人机验证失败")
            return redirect(url_for('.signIn', sso=sso)) if sso_isOk else redirect(url_for('.signIn'))
        else:
            # GET请求仅用于渲染
            return render_template("auth/signIn.html", vaptcha=vaptcha.getChallenge)

@FrontBlueprint.route("/OAuthGuide")
@anonymous_required
def OAuthGuide():
    """OAuth2登录未注册时引导路由(来源于OAuth goto_signUp)，选择绑定已有账号或直接登录(首选)"""
    if request.args.get("openid"):
        return render_template("auth/OAuthGuide.html")
    else:
        return redirect(g.redirect_uri)

@FrontBlueprint.route("/OAuthGuide/DirectLogin", methods=["POST"])
@anonymous_required
def OAuthDirectLogin():
    """OAuth2直接登录(首选)"""
    if request.method == 'POST':
        sso = request.args.get("sso") or None
        logger.debug("OAuthDirectLogin, sso type: {}, content: {}".format(type(sso), sso))
        openid = request.form.get("openid")
        if openid:
            auth = Authentication(g.mysql, g.redis)
            # 直接注册新账号并设置登录态
            res = auth.oauth2_signUp(openid, g.ip)
            res = dfr(res)
            if res["success"]:
                # 记录登录日志
                auth.brush_loginlog(res, login_ip=g.ip, user_agent=request.headers.get("User-Agent"))
                sso_isOk, sso_returnUrl, sso_appName = checkGet_ssoRequest(sso)
                sessionId, returnUrl = checkSet_ssoTicketSid(sso_isOk, sso_returnUrl, sso_appName, res["uid"], url_for("front.userset", _anchor="bind"))
                logger.debug("OAuthDirectLogin post returnUrl: {}".format(returnUrl))
                return set_loginstate(sessionId, returnUrl)
            else:
                flash(res["msg"])
                return redirect(url_for("front.OAuthGuide", openid=openid, sso=sso))
        else:
            return redirect(g.redirect_uri)

@FrontBlueprint.route("/OAuthGuide/BindAccount", methods=["GET", "POST"])
@anonymous_required
def OAuthBindAccount():
    """OAuth2绑定已有账号登录"""
    if request.method == 'POST':
        sso = request.args.get("sso") or None
        logger.debug("OAuthBindAccount, sso type: {}, content: {}".format(type(sso), sso))
        openid = request.form.get("openid")
        if vaptcha.validate:
            account = request.form.get("account")
            password = request.form.get("password")
            auth = Authentication(g.mysql, g.redis)
            res = auth.oauth2_bindLogin(openid=openid, account=account, password=password)
            res = dfr(res)
            if res["success"]:
                # 记录登录日志
                auth.brush_loginlog(res, login_ip=g.ip, user_agent=request.headers.get("User-Agent"))
                sso_isOk, sso_returnUrl, sso_appName = checkGet_ssoRequest(sso)
                sessionId, returnUrl = checkSet_ssoTicketSid(sso_isOk, sso_returnUrl, sso_appName, res["uid"], url_for("front.userset", _anchor="bind"))
                logger.debug("OAuthBindAccount post returnUrl: {}".format(returnUrl))
                return set_loginstate(sessionId, returnUrl)
            else:
                flash(res["msg"])
        else:
            flash(u"人机验证失败")
        return redirect(url_for('.OAuthBindAccount', openid=openid, sso=sso))
    else:
        openid = request.args.get("openid")
        if openid:
            return render_template("auth/OAuthBindAccount.html", vaptcha=vaptcha.getChallenge)
        else:
            return redirect(g.redirect_uri)

@FrontBlueprint.route("/signOut")
@login_required
def signOut():
    """ 单点注销流程
        1. 根据sid查找注册的clients
        2. pop一个client并跳转到其注销页面，携带参数为`NextUrl=当前路由地址`，如果有`ReturnUrl`同样携带。
           client处理：检测通过注销局部会话并跳转回当前路由
        3. 循环第2步，直到clients为空（所有已注册的局部会话已经注销）
        4. 注销本地全局会话，删除相关数据，跳转到登录页面
    """
    # 最终跳转回地址
    ReturnUrl = request.args.get("ReturnUrl") or url_for(".signOut", _external=True)
    if g.sid:
        clients = g.api.usersso.ssoGetRegisteredClient(g.sid)
        logger.debug("has sid, get clients: {}".format(clients))
        if clients and isinstance(clients, list) and len(clients) > 0:
            clientName = clients.pop()
            clientData = g.api.userapp.getUserApp(clientName)
            if clientData:
                if g.api.usersso.clearRegisteredClient(g.sid, clientName):
                    NextUrl = "{}/sso/authorized?{}".format(clientData["app_redirect_url"].strip("/"), urlencode(dict(Action="ssoLogout", ReturnUrl=ReturnUrl, app_name=clientName)))
                    return redirect(NextUrl)
            return redirect(url_for(".signOut"))
    # 没有sid时，或者存在sid已经注销到第4步
    g.api.usersso.clearRegisteredUserSid(g.uid, g.sid)
    response = make_response(redirect(ReturnUrl))
    response.set_cookie(key='sessionId', value='', expires=0)
    return response

@FrontBlueprint.route("/unbind")
@login_required
def unbind():
    # 解绑账号
    identity_name = request.args.get("identity_name")
    if identity_name:
        auth = Authentication(g.mysql, g.redis)
        res = auth.unbind(g.uid, oauth2_name2type(identity_name))
        res = dfr(res)
        if res["code"] == 0:
            flash(u"解绑成功")
        else:
            flash(res["msg"])
    else:
        flash(u"无效参数")
    return redirect(url_for("front.userset", _anchor="bind"))

@FrontBlueprint.route("/terms.html")
def terms():
    # 服务条款
    return render_template("public/terms.html")
